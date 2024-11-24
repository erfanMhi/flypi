from typing import Dict, Any, List
import json
import base64
import asyncio
from app.schema_models.component_schema import BasicComponentList
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


async def identify_components_3shot(image_data: bytes) -> Dict[str, Any]:
    # decode to bytes
    # image_bytes = base64.b64decode(image_data)


    message_list = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "This is a sketched image of a basic high school electronics class. Please look at it well, do you see on the drawing any zigzag lines indicating resistors? any two parallel lines (one shorter that the other)  indicating a battery? Any loops indicating an LED, or any breaks in the line indicating a switch? "
                    }
                ]
            }
        ]

    completion = await client.chat.completions.create(
    model="llama-3.2-90b-vision-preview",
    messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "This is a sketched image of a basic high school electronics class. Please look at it well, do you see on the drawing any zigzag lines indicating resistors? any two parallel lines (one shorter that the other)  indicating a battery? Any loops indicating an LED, or any breaks in the line indicating a switch? THINK carefully, and only answer with the components that are present (battery will always be present), you will not see all components most of the time"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_data}"
                        }
                    }
                ]
            }
        ],
        temperature=0.8,
        # max_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )

    response1 = completion.choices[0].message.content

    print(response1)

    assistant_message = {
        "role": "assistant",
        "content": response1
    }
    message_list.append(assistant_message)

    user_message = {
        "role": "user",
        "content": "What components of the list ('resistor', 'battery', 'led', 'switch') are present? NOT ALL WILL BE PRESENT, battery will always be present"
    }
    message_list.append(user_message)

    completion2 = await client.chat.completions.create(
        model="llama-3.2-90b-vision-preview",
        messages=message_list,
        temperature=0.7,
        # max_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )

    response2 = completion2.choices[0].message.content

    print(response2)

    ## now lets extract the json from the response
    ## similar to this
    
    chat_completion_extraction = await client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are an electrical circuit component identifier that outputs components in JSON.\n"
                # Pass the json schema to the model. Pretty printing improves results.
                f" The JSON object must use the schema: {json.dumps(BasicComponentList.model_json_schema(), indent=2)}",
            },
            {
                "role": "user",
                "content": f"Extract the components from the following text: {response2}",
            },
        ],
        model="llama-3.2-90b-vision-preview",
        temperature=0,
        # Streaming is not supported in JSON mode
        stream=False,
        # Enable JSON mode by setting the response format
        response_format={"type": "json_object"},
    )

    response3 = chat_completion_extraction.choices[0].message.content

    print(response3)

    print("--------------------------------")

    try:
        data = json.loads(response3)
        return data
    except Exception as e:
        return None
    


