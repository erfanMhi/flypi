from pydantic import BaseModel, Field

class Component(BaseModel):
    id: str = Field(description="Unique identifier for the component")
    type: str = Field(description="The type of component (e.g., battery, resistor, led)") 

class ComponentList(BaseModel):
    components: list[Component] = Field(description="List of components in the circuit")

class BasicComponent(BaseModel):
    component_type: str = Field(description="The type of component choose from the list (e.g., battery, resistor, led, switch)")

class BasicComponentList(BaseModel):
    components: list[BasicComponent] = Field(description="List of components in the circuit seen")
