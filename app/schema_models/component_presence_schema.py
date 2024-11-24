from pydantic import BaseModel, Field

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