import os
from typing import Dict, Any, List, Optional
import json
import base64
import asyncio
from litellm import acompletion
from groq import AsyncGroq
from pydantic import BaseModel
from loguru import logger
from app.core.config import Settings


class LLMService:
    """Service for handling communication with Language Learning Models."""

    def __init__(self, settings: Settings):
        """Initialize the LLM service.

        Args:
            settings: Application settings
        """
        self._settings = settings
        self._groq_client = AsyncGroq()

    @staticmethod
    def _encode_image_bytes(image_bytes: bytes) -> str:
        """Encode image bytes to base64 string.

        Args:
            image_bytes: Raw image bytes

        Returns:
            str: Base64 encoded image string
        """
        return base64.b64encode(image_bytes).decode('utf-8')

    async def _communicate_groq(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        schema: Optional[BaseModel] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Handle communication using Groq's native API."""
        try:
            # Remove 'groq/' prefix from model name
            clean_model = model.replace('groq/', '')
            
            completion = await self._groq_client.chat.completions.create(
                model=clean_model,
                messages=messages,
                temperature=temperature or self._settings.TEMPERATURE,
                max_tokens=max_tokens or self._settings.MAX_TOKENS,
                top_p=1.0,
                response_format={"type": "json_object"} if schema else None,
                seed=self._settings.SEED,
            )
            return completion.choices[0].message.content
        except Exception as e:
            raise ValueError(f"Groq API request failed: {str(e)}")

    async def _communicate_litellm(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        schema: Optional[BaseModel] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Communicate with LLM with optional schema validation and context.
        
        Args:
            prompt: The prompt to send
            image_bytes: The image bytes to analyze
            schema: Optional Pydantic model for structured output
            context_messages: Optional list of previous messages for context
            model: Optional model override
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Returns:
            Dict[str, Any]: The validated response from the LLM

        Raises:
            ValueError: If the API request fails or response validation fails
        """
        completion_kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature or self._settings.TEMPERATURE,
            "max_tokens": max_tokens or self._settings.MAX_TOKENS,
            "top_p": 1.0,
            "stream": False,
            "seed": self._settings.SEED,
            "stop": None,
        }

        if schema:
            completion_kwargs["response_format"] = {"type": "json_object"}

        completion = await asyncio.wait_for(
            acompletion(**completion_kwargs),
            timeout=self._settings.LLM_API_TIMEOUT
        )
        return completion.choices[0].message.content

    async def communicate(
        self,
        prompt: str,
        image_bytes: bytes,
        schema: Optional[BaseModel] = None,
        context_messages: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Communicate with LLM with optional schema validation and context.

        Args:
            prompt: The prompt to send
            image_bytes: The image bytes to analyze
            schema: Optional Pydantic model for structured output
            context_messages: Optional list of previous messages for context
            model: Optional model override
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Returns:
            Dict[str, Any]: The validated response from the LLM

        Raises:
            ValueError: If the API request fails or response validation fails
        """
        image_data = self._encode_image_bytes(image_bytes)
        messages = list(context_messages or [])
        final_prompt = prompt

        if schema:
            final_prompt += (
                "\n\nOutput MUST EXACTLY match this JSON schema:"
                f"\n{json.dumps(schema.model_json_schema(), indent=2)}"
            )

        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": final_prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data}"
                    }
                },
            ]
        })

        used_model = model or self._settings.MODEL_NAME

        try:
            # Choose API based on model name
            if used_model.startswith("groq/"):
                response = await self._communicate_groq(
                    messages=messages,
                    model=used_model,
                    schema=schema,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            else:
                response = await self._communicate_litellm(
                    messages=messages,
                    model=used_model,
                    schema=schema,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

            if schema:
                try:
                    data = json.loads(response)
                    validated = schema.model_validate(data)
                    return validated.model_dump()
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON response: {str(e)}")
                except Exception as e:
                    raise ValueError(f"Response validation failed: {str(e)}")

            return response

        except asyncio.TimeoutError:
            raise ValueError(
                f"LLM request timed out after {self._settings.LLM_API_TIMEOUT}s"
            )
        except Exception as e:
            raise ValueError(f"LLM API request failed: {str(e)}")