from pydantic import BaseModel, Field
from typing import List, Dict


class Component(BaseModel):
    id: str = Field(description="Unique identifier for the component")
    type: str = Field(description="The type of component (e.g., battery, resistor, led)")

class Connection(BaseModel):
    component: str = Field(description="ID of the component making the connections")
    connections: list[str] = Field(description="List of IDs of components this component is connected to")

class ComponentList(BaseModel):
    components: list[Component] = Field(description="List of components in the circuit")

class ConnectionList(BaseModel):
    connections: list[Connection] = Field(description="List of connections in the circuit")

class CircuitSchema(BaseModel):
    components: list[Component]
    connections: list[Connection]

class ResistorPresence(BaseModel):
    """
    Pydantic model to represent the presence of a resistor in a circuit diagram.
    
    This model contains a single boolean field, `resistor`, which indicates
    whether a resistor is present or not in the analyzed circuit image.
    """
    
    # The resistor field is described here with Field for extra metadata
    resistor: bool = Field(
        title="Resistor Presence",
        description="Indicates whether a resistor is detected in the circuit diagram image.",
        example=True 
    )

class BatteryPresence(BaseModel):
    battery: bool = Field(
        title="Battery Presence",
        description="Indicates whether a battery is detected in the circuit diagram image.",
        example=True  
    )

class LEDPresence(BaseModel):
    led: bool = Field(
        title="LED Presence",
        description="Indicates whether an LED is detected in the circuit diagram image.",
        example=True  
    )

class SwitchPresence(BaseModel):
    switch: bool = Field(
        title="Switch Presence",
        description="Indicates whether a switch is detected in the circuit diagram image.",
        example=True  
    )


