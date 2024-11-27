from pydantic import BaseModel, Field
from typing import List
from .component_schema import Component


class Connection(BaseModel):
    component: str = Field(description="ID of the component making the connections")
    connections: list[str] = Field(description="List of IDs of components this component is connected to")


class CircuitSchema(BaseModel):
    components: list[Component]
    connections: list[Connection] 