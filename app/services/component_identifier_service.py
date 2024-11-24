from typing import Set, Dict, Any
from app.schema_models.component_presence_schema import (
    BatteryPresence,
    LEDPresence,
    ResistorPresence,
    SwitchPresence
)
from app.services.groq_client import communicate_with_groq

class ComponentIdentifierService:
    def __init__(self):
        self.component_checkers = {
            "battery": self._is_there_a_battery,
            "resistor": self._is_there_a_resistor,
            "led": self._is_there_a_led,
            "switch": self._is_there_a_switch,
        }

    async def identify_components(self, image_bytes: bytes) -> Set[str]:
        """Given an image, identify the components present
        Returns a set of component names (e.g., {"battery", "resistor", "led"})
        """
        components = {}
        for component_name, checker_method in self.component_checkers.items():
            components[component_name] = await checker_method(image_bytes)
        
        print('Components', components)
        return {
            component for component, presence in components.items() 
            if presence
        }

    async def _check_component(self, image_bytes: bytes, prompt: str, schema: Any) -> bool:
        response = await communicate_with_groq(prompt, image_bytes, schema=schema)
        print('Reasoning: ', response['reasoning'])
        print('Approximate location: ', response['approximate_location'])
        return response['is_present']

    async def _is_there_a_battery(self, image_bytes: bytes) -> bool:
        prompt = """
        Analyze this circuit diagram and determine if a battery is present.
        Always consider that this component is present in the circuit.
        """
        return True
        return await self._check_component(image_bytes, prompt, BatteryPresence)

    async def _is_there_a_resistor(self, image_bytes: bytes) -> bool:
        prompt = """
        Analyze this circuit diagram and determine if a resistor is present. 
        Always consider that this component is present in the circuit.
        """
        return True
        return await self._check_component(image_bytes, prompt, ResistorPresence)

    async def _is_there_a_led(self, image_bytes: bytes) -> bool:
        prompt = """
        Task: Determine if the given hand-drawn circuit diagram contains an LED component.

        Characteristics of an LED component in the diagram:
        1. Look for a hand-drawn small loop, a circular shape, or an ellipse in the diagram.
        2. The interior of the shape is empty, with no additional markings or symbols inside.

        Based on these characteristics, determine if an LED is present in the diagram.
        """
        return await self._check_component(image_bytes, prompt, LEDPresence)

    async def _is_there_a_switch(self, image_bytes: bytes) -> bool:
        prompt = """
        Task: Determine whether the hand-drawn circuit diagram contains a switch component. A switch has the following strict characteristics:

        1. A switch makes a gap following the line of the circuit wire and suddenly getting diagonal (with 30 to 60 degrees and diagnal to wire) and separates two parts of the circuit from each other.
        2. The diagonal line must not resemble the zigzag pattern of resistors, the small loop of LEDs, or parallel lines of a battery with a gap.
        3. Do not consider any loops or circular shapes as switches.

        All of these characteristics must be present in the diagram for a switch to be present.

        Note: Do not mistake zigzag patterns (resistor), loops/arrows (LED), or continuous straight lines (battery) for a switch.

        Output: Return whether a switch is present, ensuring all characteristics are met.
        """
        print('IN SWITCH')
        return await self._check_component(image_bytes, prompt, SwitchPresence)
