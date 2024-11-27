from pydantic import BaseModel, Field


class ResistorPresence(BaseModel):
    reasoning: str = Field(
        title="Reasoning for Resistor Presence",
        description="Explanation or reasoning for the detected presence or absence of a resistor. Clearly elaborate. Not more than 100 words.",
    )
    approximate_location: str = Field(
        title="Approximate Location of Resistor",
        description="The approximate location of the resistor on the circuit diagram. This should be a rough estimate based on the image and the component description.",
    )
    is_present: bool = Field(
        title="Resistor Presence",
        description="Indicates whether a resistor is detected in the circuit diagram image.",
    )


class BatteryPresence(BaseModel):
    reasoning: str = Field(
        title="Reasoning for Battery Presence",
        description="Explanation or reasoning for the detected presence or absence of a battery. Clearly elaborate. Not more than 100 words.",
    )
    approximate_location: str = Field(
        title="Approximate Location of Battery",
        description="The approximate location of the battery on the circuit diagram. This should be a rough estimate based on the image and the component description.",
    )
    is_present: bool = Field(
        title="Battery Presence",
        description="Indicates whether a battery is detected in the circuit diagram image.",
    )


class LEDPresence(BaseModel):
    reasoning: str = Field(
        title="Reasoning for LED Presence",
        description="Explanation or reasoning for the detected presence or absence of an LED. Clearly elaborate. Not more than 100 words.",
    )
    approximate_location: str = Field(
        title="Approximate Location of LED",
        description="The approximate location of the LED on the circuit diagram. This should be a rough estimate based on the image and the component description.",
    )
    is_present: bool = Field(
        title="LED Presence",
        description="Indicates whether an LED is detected in the circuit diagram image.",
    )


class SwitchPresence(BaseModel):
    reasoning: str = Field(
        title="Reasoning for Switch Presence",
        description="Explanation or reasoning for the detected presence or absence of a switch. Clearly elaborate. Not more than 100 words.",
    )
    approximate_location: str = Field(
        title="Approximate Location of Switch",
        description="The approximate location of the switch on the circuit diagram. This should be a rough estimate based on the image and the component description.",
    )
    is_present: bool = Field(
        title="Switch Presence",
        description="Indicates whether a switch is detected in the circuit diagram image.",
    )