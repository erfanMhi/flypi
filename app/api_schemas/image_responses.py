from typing import List
from pydantic import BaseModel
from .components import Component, Connection


class SchemaImageResponse(BaseModel):
    """Schema for full circuit schema response.

    Attributes:
        components: List of components in the circuit
        connections: List of connections between components
    """
    components: List[Component]
    connections: List[Connection]


class ComponentsImageResponse(BaseModel):
    """Schema for component-only response.

    Attributes:
        components: List of components identified in the image
    """
    components: List[Component] 