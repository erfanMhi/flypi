from pydantic import BaseModel, Field
from typing import List, Dict


class Component(BaseModel):
    id: str = Field(description="Unique identifier for the component")
    type: str = Field(description="The type of component (e.g., battery, resistor, led)")

class Connection(BaseModel):
    component: str = Field(description="ID of the component making the connections")
    connections: list[str] = Field(description="List of IDs of components this component is connected to")

class CircuitSchema(BaseModel):
    components: list[Component]
    connections: list[Connection]

class ResistorPresence(BaseModel):
    resistor: bool = Field(
        title="Resistor Presence",
        description="Indicates whether a resistor is detected in the circuit diagram image.",
    )

class BatteryPresence(BaseModel):
    battery: bool = Field(
        title="Battery Presence",
        description="Indicates whether a battery is detected in the circuit diagram image.",
    )

class LEDPresence(BaseModel):
    led: bool = Field(
        title="LED Presence",
        description="Indicates whether an LED is detected in the circuit diagram image.",
    )

class SwitchPresence(BaseModel):
    switch: bool = Field(
        title="Switch Presence",
        description="Indicates whether a switch is detected in the circuit diagram image.",
    )


