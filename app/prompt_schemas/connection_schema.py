from pydantic import BaseModel, Field


class ComponentConnection(BaseModel):
    is_connected: bool = Field(description="Whether the two components are connected or not")