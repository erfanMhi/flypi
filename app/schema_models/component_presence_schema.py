from pydantic import BaseModel, Field

class ResistorPresence(BaseModel):
    description: str = Field(
        title="Circuit component description",
        description="A detailed description of all of the circuit components and how they look like on the diagram.",
    )
    reasoning: str = Field(
        title="Reasoning for Resistor Presence",
        description="Explanation or reasoning for the detected presence or absence of a resistor.",
    )
    approximate_location: str = Field(
        title="Approximate location of the resistor",
        description="The approximate location of the resistor on the diagram.",
    )
    is_present: bool = Field(
        title="Resistor Presence",
        description="Indicates whether a resistor is detected in the circuit diagram image.",
    )

class BatteryPresence(BaseModel):
    description: str = Field(
        title="Circuit component description",
        description="A detailed description of all of the circuit components and how they look like on the diagram.",
    )
    reasoning: str = Field(
        title="Reasoning for Battery Presence",
        description="Explanation or reasoning for the detected presence or absence of a battery.",
    )
    approximate_location: str = Field(
        title="Approximate location of the battery",
        description="The approximate location of the battery on the diagram.",
    )
    is_present: bool = Field(
        title="Battery Presence",
        description="Indicates whether a battery is detected in the circuit diagram image.",
    )

class LEDPresence(BaseModel):
    description: str = Field(
        title="Circuit component description",
        description="A detailed description of all of the circuit components and how they look like on the diagram.",
    )
    reasoning: str = Field(
        title="Reasoning for LED Presence",
        description="Explanation or reasoning for the detected presence or absence of an LED.",
    )
    approximate_location: str = Field(
        title="Approximate location of the LED",
        description="The approximate location of the LED on the diagram.",
    )
    is_present: bool = Field(
        title="LED Presence",
        description="Indicates whether an LED is detected in the circuit diagram image.",
    )


class SwitchPresence(BaseModel):
    description: str = Field(
        title="Circuit component description",
        description="A detailed description of all of the circuit components and how they look like on the diagram.",
    )
    reasoning: str = Field(
        title="Reasoning for Switch Presence",
        description="Explanation or reasoning for the detected presence or absence of a switch.",
    ) 
    approximate_location: str = Field(
        title="Approximate location of the switch",
        description="The approximate location of the switch on the diagram.",
    )
    is_present: bool = Field(
        title="Switch Presence",
        description="Indicates whether a switch is detected in the circuit diagram image.",
    )