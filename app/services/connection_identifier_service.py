from typing import Set, Dict, Any, List, Tuple
from app.schema_models.connection_schema import ComponentConnection
from app.services.groq_client import communicate_with_groq
from itertools import combinations

class ConnectionIdentifierService:
    def __init__(self):
        self.component_descriptions = {
            "battery": "two parallel lines (one longer, one shorter)",
            "resistor": "zigzag line",
            "led": "circular loop with connecting lines",
            "switch": "line with a gap between terminals"
        }

    async def identify_connections(self, components: Set[str], image_bytes: bytes) -> List[Dict[str, Any]]:
        """
        Identifies connections between all pairs of components in the circuit.
        
        Args:
            components: Set of component names present in the circuit
            image_bytes: The circuit diagram image bytes
            
        Returns:
            List of dictionaries containing component pairs and their connection status
        """
        connections = []
        # Generate all possible pairs of components
        component_pairs = list(combinations(components, 2))
        
        for comp1, comp2 in component_pairs:
            is_connected = await self._check_connection(comp1, comp2, image_bytes)
            connections.append({
                "component1": comp1,
                "component2": comp2,
                "connected": is_connected
            })
        
        return connections

    async def _check_connection(self, comp1: str, comp2: str, image_bytes: bytes) -> bool:
        """
        Checks if two components are connected in the circuit.
        """
        prompt = self._generate_connection_prompt(comp1, comp2)
        response = await communicate_with_groq(
            prompt=prompt,
            image_bytes=image_bytes,
            schema=ComponentConnection,
            temperature=0.2  # Lower temperature for more precise answers
        )
        return response["is_connected"]

    def _generate_connection_prompt(self, comp1: str, comp2: str) -> str:
        """
        Generates a specific prompt for checking connection between two components.
        """
        return f"""
        You are analyzing a hand-sketched circuit diagram. Your ONLY task is to determine if there is a direct or indirect 
        connection between these two specific components:

        Component 1: {comp1} (represented as {self.component_descriptions.get(comp1, "")})
        Component 2: {comp2} (represented as {self.component_descriptions.get(comp2, "")})

        A connection exists if:
        1. The components are directly connected by a continuous line
        2. The components are indirectly connected through other components or wires
        3. There is a clear path for electrical current to flow between them

        Important rules:
        - Only focus on these two specific components
        - Ignore all other components unless they form part of the connection path
        - A connection exists even if it goes through other components
        - Look for continuous lines or paths between the components
        - The connection can be made of multiple segments or wires

        Respond with true if a connection exists, false if there is no connection.
        """ 