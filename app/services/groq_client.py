from typing import Dict, Any, List
import json
import base64
import asyncio
from groq import AsyncGroq
from pydantic import BaseModel
from app.core.config import get_settings
from openai import AsyncOpenAI

settings = get_settings()
client = AsyncGroq(api_key=settings.GROQ_API_KEY)
openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

def encode_image_bytes(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode('utf-8')

async def communicate_with_groq(
    prompt: str, 
    image_bytes: bytes, 
    model: str = settings.MODEL_NAME, 
    temperature: float = settings.TEMPERATURE, 
    max_tokens: int = settings.MAX_TOKENS,
    schema: BaseModel = None,
    context_messages: List[Dict[str, Any]] = None,
    seed: int = settings.SEED,
    api_type: str = "groq"
) -> str:
    """Communicate with groq or openai with optional schema validation and context

    Args:
        prompt: The prompt to send
        image_bytes: The image bytes to analyze
        model: The model to use
        temperature: Temperature for generation
        max_tokens: Maximum tokens to generate
        schema: Optional Pydantic model for structured output
        context_messages: Optional list of previous messages for context
        seed: Fixed random seed for reproducible results
        api_type: The API to use, either 'groq' or 'openai'
    """
    image_data = encode_image_bytes(image_bytes)
    
    # Build the messages array
    messages = []
    
    # Add context messages if provided
    if context_messages:
        messages.extend(context_messages)
    
    # Build the final prompt
    final_prompt = prompt
    if schema:
        final_prompt += f"\n\nOutput must match this JSON schema exactly:\n{json.dumps(schema.model_json_schema(), indent=2)}"
    
    # Add the main message with image
    if api_type == "groq":
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": final_prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
            ]
        })
    elif api_type == "openai":
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": final_prompt},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/png;base64,{image_data}"
                }}
            ]
        })
    else:
        raise ValueError("Invalid API type specified. Use 'groq' or 'openai'.")
    
    # Configure completion options
    completion_kwargs = {
        "model": model if api_type == "groq" else "gpt-4o",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": 1.0,
        "stream": False,
        "seed": seed,
    }
    
    # Add stop parameter only for Groq
    if api_type == "groq":
        completion_kwargs["stop"] = None
    
    # Add response format if schema is provided
    if schema:
        completion_kwargs["response_format"] = {"type": "json_object"}

    print(f'Communicating with {api_type}') 
    
    if api_type == "groq":
        completion = await asyncio.wait_for(
            client.chat.completions.create(**completion_kwargs),
            timeout=settings.GROQ_API_TIMEOUT
        )
    elif api_type == "openai":
        completion = await asyncio.wait_for(
            openai_client.chat.completions.create(**completion_kwargs),
            timeout=settings.OPENAI_API_TIMEOUT
        )
    
    response = completion.choices[0].message.content
    
    # Validate against schema if provided
    if schema:
        try:
            data = json.loads(response)
            validated = schema.model_validate(data)
            return validated.model_dump()
        except Exception as e:
            raise ValueError(f"Response validation failed: {str(e)}")
    
    return response 