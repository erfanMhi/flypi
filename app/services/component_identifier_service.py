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
        
        return {
            component for component, presence in components.items() 
            if presence
        }

    async def _check_component(self, image_bytes: bytes, prompt: str, schema: Any) -> bool:
        response = await communicate_with_groq(prompt, image_bytes, schema=schema)
        return list(response.values())[0]

    async def _is_there_a_battery(self, image_bytes: bytes) -> bool:
        prompt = """
        You have been given a circuit diagram image. Your ONLY job is to determine if a battery is present.

        A battery is represented by two parallel lines, one longer (positive terminal) and one shorter (negative terminal), 
        typically arranged vertically or horizontally. Ignore all other shapes or symbols.
        """
        return await self._check_component(image_bytes, prompt, BatteryPresence)

    async def _is_there_a_resistor(self, image_bytes: bytes) -> bool:
        prompt = """
        You have been given a circuit diagram image. Your ONLY job is to determine if a resistor is present.

        A resistor is represented exclusively by a zigzag line with peaks and valleys forming a continuous pattern. 
        Ignore all other shapes or lines.
        """
        return await self._check_component(image_bytes, prompt, ResistorPresence)

    async def _is_there_a_led(self, image_bytes: bytes) -> bool:
        prompt = """
        You have been given a **hand-sketched circuit diagram** image. Your ONLY job is to determine if an LED is present.

        An LED in this context is represented by the following specific pattern:
        1. **Circular Loop:** A closed loop resembling a circle or oval is the defining feature of the LED.
        2. **Connections:** A straight line must enter and exit the circular loop to complete the LED pattern.
        3. **Unique Shape:** The circular loop must be fully visible and distinct, with no zigzag lines, gaps, 
           or other interruptions inside or outside the loop.
        """
        return await self._check_component(image_bytes, prompt, LEDPresence)

    async def _is_there_a_switch(self, image_bytes: bytes) -> bool:
        prompt = """
        You have been given a **hand-sketched circuit diagram** image. Your ONLY job is to determine if an open switch, 
        matching the exact pattern below, is present.

        An open switch in this context is represented by:
        - Two terminals connected to lines.
        - One of the lines is angled or slanted, pointing toward the other terminal but does not touch it, 
          creating a visible gap.
        """
        return await self._check_component(image_bytes, prompt, SwitchPresence) 