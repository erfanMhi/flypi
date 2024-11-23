from groq import AsyncGroq
from typing import Dict, Any
import base64
import asyncio
from app.core.config import get_settings

settings = get_settings()
client = AsyncGroq(api_key=settings.GROQ_API_KEY)

def encode_image_bytes(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode('utf-8')

def create_structured_prompt() -> str:
    return """Analyze this circuit image and identify all electronic components present. 
    
    Focus specifically on:
    1. Power sources (batteries, power supplies)
    2. Passive components (resistors, capacitors, inductors)
    3. Active components (transistors, diodes)
    4. Output components (LEDs, light bulbs, motors, buzzers)
    
    For each component found:
    - Specify the quantity
    - Note any visible ratings or values (if shown)
    - Describe its position/role in the circuit (if clear)
    
    Format your response as a clear, structured list. Do not include wires or connections in the component count.
    If you're uncertain about any component, indicate this clearly.
    """

async def analyze_circuit_image(image_bytes: bytes) -> Dict[str, Any]:
    image_data = encode_image_bytes(image_bytes)
    
    completion = await asyncio.wait_for(
        client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": "As an expert electronics engineer specializing in circuit analysis, " + create_structured_prompt()
                        },
                        {
                            "type": "image_url", 
                            "image_url": {"url": f"data:image/png;base64,{image_data}"}
                        }
                    ]
                }
            ],
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
            top_p=1,
            stream=False,
            stop=None,
        ),
        timeout=settings.GROQ_API_TIMEOUT
    )
    
    return completion 