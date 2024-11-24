from app.schema_models.circuit_schema import CircuitSchema
from typing import Dict, Any, List
import json
from app.services.component_identifier_service import ComponentIdentifierService
from app.services.groq_client import communicate_with_groq, encode_image_bytes
from app.core.config import get_settings

settings = get_settings()

async def analyze_circuit_image(image_bytes: bytes) -> Dict[str, Any]:
    image_data = encode_image_bytes(image_bytes)
    
    prompt = """Analyze this simple circuit diagram and count the following components:

    1. Batteries (voltage sources)
    2. Resistors (shown as zigzag lines)
    3. Switches
    4. LEDs

    Provide your response in this exact format:
    - Batteries: [number]
    - Resistors: [number]
    - Switches: [number]
    - LEDs: [number]

    Only count these specific components. Ignore connecting wires."""
    
    return await communicate_with_groq(
        prompt=f"As an expert electronics engineer specializing in circuit analysis, {prompt}",
        image_bytes=image_bytes
    )

async def identify_components(image_bytes: bytes) -> set[str]:
    identifier = ComponentIdentifierService()
    print("Identifying components")
    return await identifier.identify_components(image_bytes)

async def branched_extraction(image_bytes: bytes) -> Dict[str, Any]:
    """This method first calls to identify the presence of what components exist, not quantity
    """
    components_available = await identify_components(image_bytes)
    print(f"Components available: {components_available}")
    result = await get_schema_with_components_given(image_bytes, components_available)
    schema_data = json.loads(result)
    validated_schema = CircuitSchema.model_validate(schema_data)
    return validated_schema.model_dump()

async def get_schema_with_components_given(image_bytes: bytes, components_available: set[str]) -> Dict[str, Any]:
    """Given a set of components that exist, generate a request to extract the full schema
    """
    # Dictionary of component descriptions and their example images
    prompt_dict = {
        "battery": {"description": "The battery component will always be represented by a pair of parallel lines, one long and one short. These lines will be perpendicular to its connecting wires",
                    "image_path": "battery.png"},
        "resistor": {"description": "The resistor component will always be represented by a zigzag line",
                    "image_path": "resistor.png"},
        "led": {"description": "The led component will always be represented by a bulb symbol, this is a twist enclosed in a circle",
                "image_path": "led.png"},
        "switch": {"description": "The switch component will always be represented by a line with a break in it",
                    "image_path": "switch.png"},
    }

    # Build up component knowledge through training
    component_knowledge = []

    # Train on each component that's present in the circuit
    for component in components_available:
        if component in prompt_dict:
            try:
                with open(prompt_dict[component]["image_path"], "rb") as f:
                    component_bytes = f.read()
                
                # Train the model on this component
                response = await communicate_with_groq(
                    prompt=f"This is what a {component} looks like in circuit diagrams. {prompt_dict[component]['description']}",
                    image_bytes=component_bytes
                )
                
                component_knowledge.append({
                    "component": component,
                    "knowledge": response
                })
                
            except FileNotFoundError:
                print(f"Warning: Example image for {component} not found at {prompt_dict[component]['image_path']}")
                continue

    # Create the final analysis prompt with the accumulated knowledge
    knowledge_summary = "\n".join([
        f"{k['component'].title()}: {k['knowledge']}"
        for k in component_knowledge
    ])

    analysis_prompt = f"""As an expert circuit analyzer, I've learned about How the following components look in circuit diagrams:

```
{knowledge_summary}
```

Now, I will analyze this circuit diagram and output a JSON schema of the components and their connections.

"""
    #4. Follow exactly this JSON schema: {json.dumps(CircuitSchema.model_json_schema(), indent=2)}

    # Final analysis with schema validation
    result = await communicate_with_groq(
        prompt=analysis_prompt,
        image_bytes=image_bytes,
        schema=CircuitSchema,
        temperature=0.5  # Lower temperature for more precise output
    )

    return result

async def test_extract_full_schema(image_bytes: bytes, basic: bool = True) -> Dict[str, Any]:
    """Extract a full circuit schema from an image using the CircuitSchema model.
    
    This function:
    1. Shows examples of basic components (battery, resistor)
    2. Asks for a structured analysis of the circuit
    3. Returns the analysis in CircuitSchema format

    If basic is False, we go into a more detailed analysis of the circuit
    """
    
    print("Running branched extraction")
    return await branched_extraction(image_bytes)


async def test_extract_full_schema_v0(image_bytes: bytes) -> List[str]:
    """Extract only the components list from the schema as return it as a list

    This is a simplified version of the full schema extraction
    """
    components_available = await identify_components(image_bytes)
    print(f"Components available: {components_available}")
    return list(components_available)
    
    # # First teach about basic components
    # battery_prompt = """This is what a battery looks like in circuit diagrams. 
    # It's represented by a long and short parallel lines. In a schema, it should be 
    # identified as type 'battery'."""
    
    # resistor_prompt = """This is what a resistor looks like in circuit diagrams. 
    # It's shown as a zigzag line or rectangular block. In a schema, it should be 
    # identified as type 'resistor'."""
    
    # try:
    #     # Load and encode example images - now with proper error handling
    #     with open("battery.png", "rb") as f:
    #         battery_bytes = f.read()
    #         battery_data = encode_image_bytes(battery_bytes)
    #     with open("resistor.png", "rb") as f:
    #         resistor_bytes = f.read()
    #         resistor_data = encode_image_bytes(resistor_bytes)
    #     circuit_data = encode_image_bytes(image_bytes)
        
    #     # Teach about components first
    #     await communicate_with_groq(battery_prompt, battery_bytes)
    #     await communicate_with_groq(resistor_prompt, resistor_bytes)
        
    #     # Now analyze the actual circuit with JSON schema
    #     analysis_prompt = f"""As an expert circuit analyzer, analyze this circuit diagram and output a JSON schema of the components and their connections.
        
    #     Rules:
    #     1. Identify each component (battery, resistor, LED, etc.)
    #     2. Assign unique IDs (e.g., "B1" for first battery, "R1" for first resistor)
    #     3. Map the connections between components
    #     4. Follow exactly this JSON schema: {json.dumps(CircuitSchema.model_json_schema(), indent=2)}
        
    #     Output only valid JSON matching the schema."""
        
    #     completion = await client.chat.completions.create(
    #         model=settings.MODEL_NAME,
    #         messages=[
    #             {
    #                 "role": "user",
    #                 "content": [
    #                     {"type": "text", "text": analysis_prompt},
    #                     {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{circuit_data}"}}
    #                 ]
    #             }
    #         ],
    #         temperature=0.2,  
    #         max_tokens=settings.MAX_TOKENS,
    #         response_format={"type": "json_object"},
    #     )
        
    #     # Parse and validate the response against our schema
    #     schema_data = json.loads(completion.choices[0].message.content)
    #     validated_schema = CircuitSchema.model_validate(schema_data)

    #     ## print the schema and model dump
    #     print(f"Schema: {validated_schema}")
    #     print(f"Model dump: {validated_schema.model_dump()}")
        
    #     return validated_schema.model_dump()
    # except Exception as e:
    #     print(f"Error in test_extract_full_schema: {e}")
    #     return {}
    
