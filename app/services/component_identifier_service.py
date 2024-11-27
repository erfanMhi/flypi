from typing import Set, Dict, Any, List, Tuple
from loguru import logger
from app.services.llm_client import LLMService
from app.prompt_schemas.component_presence_schema import (
    BatteryPresence,
    LEDPresence,
    ResistorPresence,
    SwitchPresence
)
from app.core.config import Settings
import asyncio


class ComponentIdentifierService:
    def __init__(self, settings: Settings, llm_service: LLMService):
        """Initialize the component identifier service.

        Args:
            settings: Application settings
            llm_service: LLM service instance
        """
        self.llm_service = llm_service
        self.settings = settings
        self._semaphore = asyncio.Semaphore(self.settings.MAX_PARALLEL_REQUESTS)
        self.component_checkers = {
            "battery": self._is_there_a_battery,
            "led": self._is_there_a_led,
            "resistor": self._is_there_a_resistor,
            "switch": self._is_there_a_switch,
        }
        self.circuit_description_prompt = (
            "Starting at the top-left corner of the circuit diagram, describe in "
            "detailed and clear terms how the shapes along the circuit line "
            "appear as if you are walking along the path of the wire. Provide a "
            "step-by-step \"tour\" of the circuit, describing every turn, "
            "connection, or distinct feature you encounter, until you eventually "
            "return to the starting point. Do not make any assumptions about the "
            "specific components or symbols in the circuit—focus solely on "
            "describing the physical shapes and structure of the lines as you "
            "navigate them. Be as thorough and explicit as possible"
        )

    async def identify_components(
        self, 
        image_bytes: bytes
    ) -> Tuple[str, List[Dict[str, str]]]:
        """Given an image, get its description and identify components present.

        Args:
            image_bytes: The image data as bytes.

        Returns:
            Tuple[str, List[Dict[str, str]]]: Circuit description and list of 
            components with their type and ID.
        """
        # Get initial circuit description
        description = await self._get_circuit_description(image_bytes)
        logger.info("Generated circuit description")
        logger.debug(f"Circuit description: {description}")

        # Identify components
        components = await self._identify_components(image_bytes)
        
        return description, components

    async def _get_circuit_description(self, image_bytes: bytes) -> str:
        """Get a detailed description of the circuit layout.

        Args:
            image_bytes: The image data as bytes.

        Returns:
            str: Detailed description of the circuit layout.
        """
        response = await self.llm_service.communicate(
            prompt=self.circuit_description_prompt,
            image_bytes=image_bytes,
            temperature=self.settings.TEMPERATURE
        )
        return response

    async def identify_components(self, image_bytes: bytes) -> List[Dict[str, str]]:
        """Given an image, identify the components present.

        Args:
            image_bytes: The image data as bytes.

        Returns:
            List[Dict[str, str]]: List of components with their type and ID.
            Example: [{"type": "battery", "id": "b1"}, {"type": "led", "id": "l1"}]
        """
        description = await self._get_circuit_description(image_bytes)
        logger.info("Generated circuit description")
        logger.debug(f"Circuit description: {description}")

        async def check_component(name: str, checker: callable) -> tuple[str, bool]:
            async with self._semaphore:
                # Modify the checker functions to accept description parameter
                result = await checker(image_bytes, description)
                return name, result

        # Run all component checks in parallel with semaphore control
        tasks = [
            check_component(name, checker)
            for name, checker in self.component_checkers.items()
        ]
        results = await asyncio.gather(*tasks)
        
        # Convert results to dictionary
        components = dict(results)
        
        logger.debug(f"Identified components: {components}")
        component_list = [
            {"type": component, "id": f"{component[0]}1"} 
            for component, presence in components.items() 
            if presence
        ]
        
        return component_list

    async def _check_component(
        self, 
        image_bytes: bytes, 
        component_name: str, 
        schema: Any,
        circuit_description: str
    ) -> bool:
        """Check for component presence using configured prompt."""
        prompt = self.settings.COMPONENT_DESCRIPTIONS[component_name]["identification"]
        return await self._check_component_base(
            image_bytes, 
            prompt, 
            schema,
            circuit_description
        )

    async def _check_component_base(
        self, 
        image_bytes: bytes, 
        prompt: str, 
        schema: Any,
        circuit_description: str
    ) -> bool:
        # Using two shot prompting to help the LLM understand the circuit before identifying the component
        enhanced_prompt = f"""Given a circuit diagram, analyze it for specific components.

Context:
A detailed description of the circuit layout is provided below. Use this description 
along with the visual information to make your determination.

Circuit Layout Description:
{circuit_description}

{prompt}

Important: 
- Focus on identifying definitive evidence of the component
- Consider both the visual representation and how it fits within the described circuit path
"""

        response = await self.llm_service.communicate(
            prompt=enhanced_prompt,
            image_bytes=image_bytes,
            schema=schema,
            temperature=self.settings.TEMPERATURE
        )
        return response['is_present']

    async def _is_there_a_battery(self, image_bytes: bytes, description: str) -> bool:
        return await self._check_component(image_bytes, "battery", BatteryPresence, description)

    async def _is_there_a_resistor(self, image_bytes: bytes, description: str) -> bool:
        return await self._check_component(image_bytes, "resistor", ResistorPresence, description)

    async def _is_there_a_led(self, image_bytes: bytes, description: str) -> bool:
        return await self._check_component(image_bytes, "led", LEDPresence, description)

    async def _is_there_a_switch(self, image_bytes: bytes, description: str) -> bool:
        return await self._check_component(image_bytes, "switch", SwitchPresence, description)
