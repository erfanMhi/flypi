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

async def extract_components(image_bytes: bytes) -> Dict[str, Any]:
    """Given an image, extract the components and their connections
    
    First it will call functions to identify wether true or false if the presence of the main components exists
    
    """
    return 

async def identify_components(image_bytes: bytes) -> set[str]:
    """Given an image, identify the components present

    For example, a set that says ["battery", "resistor", "led"] would be returned
    """
    return

async def is_there_a_battery(image_bytes: bytes) -> bool:
    """Given an image, determine if there is a battery present
    """
    return

async def is_there_a_resistor(image_bytes: bytes) -> bool:
    """Given an image, determine if there is a resistor present
    """
    return 

async def is_there_a_led(image_bytes: bytes) -> bool:
    """Given an image, determine if there is a led present
    """
    return 

async def is_there_a_switch(image_bytes: bytes) -> bool:
    """Given an image, determine if there is a switch present
    """
    return

async def communicate_with_groq(prompt: str, image_bytes: bytes, model: str = settings.MODEL_NAME, temperature: float = settings.TEMPERATURE, max_tokens: int = settings.MAX_TOKENS) -> str:
    """Communicate with groq
    """
    image_data = encode_image_bytes(image_bytes)
    
    completion = await asyncio.wait_for(
        client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
                    ]
                }
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=1,
            stream=False,
            stop=None,
        ),
        timeout=settings.GROQ_API_TIMEOUT
    )
    
    return completion.choices[0].message.content 

async def test_extract_full_schema(image_bytes: bytes) -> Dict[str, Any]:
    """Extract a full circuit schema from an image using the CircuitSchema model.
    
    This function:
    1. Shows examples of basic components (battery, resistor)
    2. Asks for a structured analysis of the circuit
    3. Returns the analysis in CircuitSchema format
    """
    from app.schema_models import CircuitSchema
    import json
    
    # First teach about basic components
    battery_prompt = """This is what a battery looks like in circuit diagrams. 
    It's represented by a long and short parallel lines. In a schema, it should be 
    identified as type 'battery'."""
    
    resistor_prompt = """This is what a resistor looks like in circuit diagrams. 
    It's shown as a zigzag line or rectangular block. In a schema, it should be 
    identified as type 'resistor'."""
    
    try:
        # Load and encode example images - now with proper error handling
        with open("battery.png", "rb") as f:
            battery_bytes = f.read()
            battery_data = encode_image_bytes(battery_bytes)
        with open("resistor.png", "rb") as f:
            resistor_bytes = f.read()
            resistor_data = encode_image_bytes(resistor_bytes)
        circuit_data = encode_image_bytes(image_bytes)
        
        # Teach about components first
        await communicate_with_groq(battery_prompt, battery_bytes)
        await communicate_with_groq(resistor_prompt, resistor_bytes)
        
        # Now analyze the actual circuit with JSON schema
        analysis_prompt = f"""As an expert circuit analyzer, analyze this circuit diagram and output a JSON schema of the components and their connections.
        
        Rules:
        1. Identify each component (battery, resistor, LED, etc.)
        2. Assign unique IDs (e.g., "B1" for first battery, "R1" for first resistor)
        3. Map the connections between components
        4. Follow exactly this JSON schema: {json.dumps(CircuitSchema.model_json_schema(), indent=2)}
        
        Output only valid JSON matching the schema."""
        
        completion = await client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": analysis_prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{circuit_data}"}}
                    ]
                }
            ],
            temperature=0.2,  
            max_tokens=settings.MAX_TOKENS,
            response_format={"type": "json_object"},
        )
        
        # Parse and validate the response against our schema
        schema_data = json.loads(completion.choices[0].message.content)
        validated_schema = CircuitSchema.model_validate(schema_data)
        
        return validated_schema.model_dump()
    except Exception as e:
        print(f"Error in test_extract_full_schema: {e}")
        return {}
    
