from typing import List
from pydantic import BaseModel


class Component(BaseModel):
    """Base schema for a circuit component.

    Attributes:
        id: Unique identifier for the component
        type: Type of the component
    """
    id: str
    type: str


class Connection(BaseModel):
    """Schema for component connections.

    Attributes:
        component: The component being connected
        connections: List of connection point identifiers
    """
    component: str
    connections: List[str] 