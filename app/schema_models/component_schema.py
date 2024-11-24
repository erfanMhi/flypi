from pydantic import BaseModel, Field

class Component(BaseModel):
    id: str = Field(description="Unique identifier for the component")
    type: str = Field(description="The type of component (e.g., battery, resistor, led)") 