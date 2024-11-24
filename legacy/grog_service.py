from app.schema_models import BatteryPresence, ComponentList, ConnectionList, LEDPresence, ResistorPresence, SwitchPresence, CircuitSchema
import json
from groq import AsyncGroq
from typing import Dict, Any, List
import base64
import asyncio
from app.core.config import get_settings
from pydantic import BaseModel, ValidationError
import json

settings = get_settings()
client = AsyncGroq(api_key=settings.GROQ_API_KEY)

def encode_image_bytes(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode('utf-8')

def create_structured_prompt() -> str:
    return """Analyze this simple circuit diagram and count the following components:

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
    """
    return 

async def identify_components(image_bytes: bytes) -> set[str]:
    """Given an image, identify the components present

    For example, a set that says ["battery", "resistor", "led"] would be returned
    """
    components = {
        "battery": await is_there_a_battery(image_bytes),
        "resistor": await is_there_a_resistor(image_bytes),
        "led": await is_there_a_led(image_bytes),
        "switch": await is_there_a_switch(image_bytes),
    }

    print(f"Components: {components}")
    return_set = set()
    for component, presence in components.items():
        if presence:
            return_set.add(component)

    return return_set

async def is_there_a_battery(image_bytes: bytes) -> bool:
    """Given an image, determine if there is a battery present
    """
    prompt = f"""
You have been given a circuit diagram image, from the image your ONLY job is to identify whether there is a battery present or not.

If there is a battery present, return True, if not return False.

    """
    response = await communicate_with_groq(prompt, image_bytes, schema=BatteryPresence)
    print(f"IMPORTANT: {response}")
    return list(response.values())[0]

async def is_there_a_resistor(image_bytes: bytes) -> bool:
    """Given an image, determine if there is a resistor present
    """
    prompt = f"""
You have been given a circuit diagram image, from the image your ONLY job is to identify whether there is a resistor present or not.

If there is a resistor present, return True, if not return False.

    """
    response = await communicate_with_groq(prompt, image_bytes, schema=ResistorPresence)
    print(f"IMPORTANT: {response}")
    ## since we have issues with the dict, but it will always return one key bool pair, lets just iter on the dict first item and
    ## return the bool value    
    return list(response.values())[0]

async def is_there_a_led(image_bytes: bytes) -> bool:
    """Given an image, determine if there is a led present
    """
    prompt = f"""
You have been given a circuit diagram image, from the image your ONLY job is to identify whether there is a led present or not.

If there is a led present, return True, if not return False.

    """
    response = await communicate_with_groq(prompt, image_bytes, schema=LEDPresence)
    print(f"IMPORTANT: {response}")
    return list(response.values())[0]

async def is_there_a_switch(image_bytes: bytes) -> bool:
    """Given an image, determine if there is a switch present
    """
    prompt = f"""
You have been given a circuit diagram image, from the image your ONLY job is to identify whether there is a switch present or not.

If there is a switch present, return True, if not return False.

    """
    response = await communicate_with_groq(prompt, image_bytes, schema=SwitchPresence)
    print(f"IMPORTANT: {response}")
    return list(response.values())[0]
    

async def communicate_with_groq_v2(
    prompt: str, 
    image_bytes: bytes, 
    system_prompt: str,
    model: str = settings.MODEL_NAME, 
    temperature: float = settings.TEMPERATURE, 
    max_tokens: int = settings.MAX_TOKENS,
    schema: BaseModel = None,
    context_messages: List[Dict[str, Any]] = None
) -> str:
    """Communicate with groq with optional schema validation and context
    """
    image_data = encode_image_bytes(image_bytes)


    system_prompt = system_prompt + f"\n\nOutput must match this JSON schema exactly:\n{json.dumps(schema.model_json_schema(), indent=2)}"

    messages = [{"role": "system", "content": system_prompt}]
    
    if context_messages:
        messages.extend(context_messages)
        
    messages.append({
        "role": "user", 
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
        ]
    })
    completion_kwargs = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": 1,
        "stream": False,
        "stop": None,
    }

    if schema:
        completion_kwargs["response_format"] = {"type": "json_object"}

        completion = await asyncio.wait_for(
            client.chat.completions.create(**completion_kwargs),
            timeout=settings.GROQ_API_TIMEOUT
        )
        
        response = completion.choices[0].message.content
        print(f"Raw Response from Groq API: {response}") 

        try:
            validated = schema.model_validate_json(response)
            print(f"Validated Data: {validated}") 
            return validated
        except ValidationError as ve:
            print(f"Pydantic Validation Error: {ve}") 
            raise ValueError(f"Response validation failed: {ve}")

async def communicate_with_groq(
    prompt: str, 
    image_bytes: bytes, 
    model: str = settings.MODEL_NAME, 
    temperature: float = settings.TEMPERATURE, 
    max_tokens: int = settings.MAX_TOKENS,
    schema: BaseModel = None,
    context_messages: List[Dict[str, Any]] = None
) -> str:
    """Communicate with groq with optional schema validation and context

    Args:
        prompt: The prompt to send
        image_bytes: The image bytes to analyze
        model: The model to use
        temperature: Temperature for generation
        max_tokens: Maximum tokens to generate
        schema: Optional Pydantic model for structured output
        context_messages: Optional list of previous messages for context
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
    messages.append({
        "role": "user",
        "content": [
            {"type": "text", "text": final_prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
        ]
    })
    
    # Configure completion options
    completion_kwargs = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": 1,
        "stream": False,
        "stop": None,
    }
    
    # Add response format if schema is provided
    if schema:
        completion_kwargs["response_format"] = {"type": "json_object"}
    
    completion = await asyncio.wait_for(
        client.chat.completions.create(**completion_kwargs),
        timeout=settings.GROQ_API_TIMEOUT
    )
    
    response = completion.choices[0].message.content
    print(f"Raw Response from Groq API: {response}")  # Debugging line
    
    # Validate against schema if provided
    if schema:
        try:
            data = json.loads(response)
            validated = schema.model_validate(data)
            print(f"Validated Data: {validated}")  # Debugging line
            return validated.model_dump()
        except ValidationError as ve:
            print(f"Pydantic Validation Error: {ve}")  # Detailed error logging
            raise ValueError(f"Response validation failed: {ve}")
    
    return response

async def branched_extraction(image_bytes: bytes) -> Dict[str, Any]:
    """This method first calls to identify the presence of what components exist, not quantity
    """
    print(f"Going into branched extraction")
    components_available = await identify_components(image_bytes)
    print(f"Components available: {components_available}")

    ## Now that we got the components, we can generate a request asking WITH the circuit schema, to extract the full schema
    ## given that we know what components exist

    result = await get_schema_with_components_given(image_bytes, components_available)
    print(f"Result: {result}")
    print(f"Type of result: {type(result)}")
    schema_data = json.loads(result)
    validated_schema = CircuitSchema.model_validate(schema_data)

    print(f"Validated schema: {validated_schema}")
    print(f"Model dump: {validated_schema.model_dump()}")
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

    print(f"Going into training loop")

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

    print(f"Out of training loop")
    
    analysis_prompt = f"""As an expert circuit analyzer, I've learned about How the following components look in circuit diagrams:

```
{knowledge_summary}
```

Now, I will analyze this circuit diagram and output a JSON schema of the components and their connections.

"""
    #4. Follow exactly this JSON schema: {json.dumps(CircuitSchema.model_json_schema(), indent=2)}

    print(f"Analysis prompt: {analysis_prompt}")
    # Final analysis with schema validation
    result = await communicate_with_groq(
        prompt=analysis_prompt,
        image_bytes=image_bytes,
        schema=CircuitSchema,
        temperature=0.5  # Lower temperature for more precise output
    )

    print(f"Out of final analysis")

    return result

async def test_extract_full_schema(image_bytes: bytes, basic: bool = True) -> Dict[str, Any]:
    """Extract a full circuit schema from an image using the CircuitSchema model.
    
    This function:
    1. Shows examples of basic components (battery, resistor)
    2. Asks for a structured analysis of the circuit
    3. Returns the analysis in CircuitSchema format

    If basic is False, we go into a more detailed analysis of the circuit
    """
    
    if not basic:
        print("Running branched extraction")
        return await branched_extraction(image_bytes)
    
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

        ## print the schema and model dump
        print(f"Schema: {validated_schema}")
        print(f"Model dump: {validated_schema.model_dump()}")
        
        return validated_schema.model_dump()
    except Exception as e:
        print(f"Error in test_extract_full_schema: {e}")
        return {}
    

async def test_extract_full_schema_v2(image_bytes: bytes, basic: bool = True) -> Dict[str, Any]:
    """Extract a full circuit schema from an image using the CircuitSchema model.
    """

    ## lets do it all in a single shot

    print("--------------------------------")   
    print("Starting test_extract_full_schema_v2")
    print("--------------------------------")

    description_dict = {
        "battery": "The battery component will always be represented by a pair of parallel lines, one long and one short. These lines will be perpendicular to its connecting wires",
        "resistor": "The resistor component will always be represented by a zigzag line or rectangular block",
        "led": "The led component will always be represented by a bulb symbol, this is a twist enclosed in a circle",
        "switch": "The switch component will always be represented by a line with a break in it",
    }

    get_components_prompt = f"""
You will be given a circuit diagram image, your job is to identify the components present in the circuit.

You have to identify the components based on the following descriptions of how they visually look in circuit diagram that you will be given:

```
{description_dict}
```

"""
    response = await communicate_with_groq(get_components_prompt, image_bytes)

    ## lets draft the next prompt and store in messages 
    messages = [
        {"role": "user", "content": get_components_prompt},
        {"role": "assistant", "content": response}
    ]

    get_connections_prompt = f"""
Now that we know what components are present, lets output the components in a json schema following this format:

"""
    
    component_response = await communicate_with_groq_v2(prompt=get_connections_prompt, image_bytes=image_bytes, context_messages=messages, temperature=0, system_prompt=f"You are an expert circuit component identifier, you will be given a circuit diagram image and you will have to identify the components present in the circuit. The components will be identifiable based on the following descriptions {description_dict}. Please output only valid JSON matching the schema.", schema=ComponentList)

    print(f"Components: {component_response}") ## list of components

    ## now we need to get the connections

    messages.append({"role": "assistant", "content": f"The components present in the circuit are: {component_response}"})
    
    connection_prompt = f"""
Now that we know that the following components are present:

```
{', '.join(component_response)}
```

What are the connections between the components?
For example, if component A is connected to component B, it should be represented as "A" -> "B".
or if component A is connected to component B and component C, it should be represented as "A" -> ["B", "C"]

Think step by step.
"""
    response = await communicate_with_groq(prompt=connection_prompt, image_bytes=image_bytes, context_messages=messages)

    messages.append({"role": "user", "content": connection_prompt})
    messages.append({"role": "assistant", "content": response})


    connections_response = await communicate_with_groq_v2(prompt="Please given the connections, output the full schema for the connections", image_bytes=image_bytes, context_messages=messages, temperature=0, system_prompt=f"You are an expert circuit connection identifier, you will be given a circuit diagram image and you will have to identify the connections between the components. Please output only valid JSON matching the schema.", schema=ConnectionList)

    ## now we need to combine the components and connections

    print("--------------------------------")
    print(f"Components: {component_response}")
    print(f"Connections: {connections_response}")
    print("--------------------------------")
    final_schema = CircuitSchema(components=component_response, connections=connections_response)

    print(f"Final schema: {final_schema}")
    print(f"Final schema model dump: {final_schema.model_dump()}")

    return final_schema.model_dump()

