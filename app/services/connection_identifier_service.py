from typing import Set, Dict, Any, List, Tuple
import asyncio
from app.prompt_schemas.connection_schema import ComponentConnection
from app.services.llm_client import LLMService
from app.core.config import Settings

class ConnectionIdentifierService:

    def __init__(self, settings: Settings, llm_service: LLMService):
        self.llm_service = llm_service
        self.settings = settings
        self._semaphore = asyncio.Semaphore(self.settings.MAX_PARALLEL_REQUESTS)

    async def _check_connection_with_semaphore(
        self, comp1: str, comp2: str, image_bytes: bytes
    ) -> bool:
        """Wrapper for _check_connection that uses a semaphore."""
        async with self._semaphore:
            return await self._check_connection(comp1, comp2, image_bytes)

    async def identify_connections(
        self, 
        components: List[Dict[str, str]], 
        image_bytes: bytes
    ) -> List[Dict[str, Any]]:
        """
        Identifies connections between components in the circuit.
        
        Args:
            components: List of component dictionaries with 'id' and 'type'
            image_bytes: The circuit diagram image bytes
            
        Returns:
            List of dictionaries containing component and their connections
        """
        # Create all possible component pairs
        connection_tasks = []
        component_pairs: List[Tuple[Dict[str, str], Dict[str, str]]] = []
        
        for i, comp in enumerate(components):
            for other_comp in components[i + 1:]:
                if other_comp["type"] != comp["type"]:
                    component_pairs.append((comp, other_comp))
                    connection_tasks.append(
                        self._check_connection_with_semaphore(
                            comp["type"],
                            other_comp["type"],
                            image_bytes
                        )
                    )
        
        # Run all connection checks in parallel
        connection_results = await asyncio.gather(*connection_tasks)
        
        # Build the connections map
        connections_map = {comp["id"]: [] for comp in components}
        
        for (comp, other_comp), is_connected in zip(component_pairs, connection_results):
            if is_connected:
                connections_map[comp["id"]].append(other_comp["id"])
                connections_map[other_comp["id"]].append(comp["id"])
        
        # Format the final output
        return [
            {"component": comp_id, "connections": connections}
            for comp_id, connections in connections_map.items()
        ]

    async def _check_connection(self, comp1: str, comp2: str, image_bytes: bytes) -> bool:
        """
        Checks if two components are connected in the circuit.
        """
        prompt = self._generate_connection_prompt(comp1, comp2)
        response = await self.llm_service.communicate(
            prompt=prompt,
            image_bytes=image_bytes,
            schema=ComponentConnection,
            temperature=self.settings.TEMPERATURE
        )
        return response["is_connected"]

    def _generate_connection_prompt(self, comp1: str, comp2: str) -> str:
        """
        Generates a specific prompt for checking connection between two components.
        """
        comp1_desc = self.settings.COMPONENT_DESCRIPTIONS[comp1]["visual_representation"]
        comp2_desc = self.settings.COMPONENT_DESCRIPTIONS[comp2]["visual_representation"]

        return f"""
        You are analyzing a hand-sketched circuit diagram. Your ONLY task is to determine if there is a direct 
        connection between these two specific components:

        Component 1: {comp1} (represented as {comp1_desc})
        Component 2: {comp2} (represented as {comp2_desc})

        A connection exists if:
        1. The components are directly connected by a continuous line
        2. There shouldn't be any other components in between them just the line

        Important rules:
        - Only focus on these two specific components
        - Ignore all other components unless they form part of the connection path
        - Look for continuous lines or paths between the components
        """ 