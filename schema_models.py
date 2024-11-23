from pydantic import BaseModel, Field

class Component(BaseModel):
    id: str = Field(description="Unique identifier for the component")
    type: str = Field(description="The type of component (e.g., battery, resistor, led)")

class Connection(BaseModel):
    component: str = Field(description="ID of the component making the connections")
    connections: list[str] = Field(description="List of IDs of components this component is connected to")

class CircuitSchema(BaseModel):
    components: list[Component]
    connections: list[Connection]