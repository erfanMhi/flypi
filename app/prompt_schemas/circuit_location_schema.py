from pydantic import BaseModel, Field

class CircuitLocation(BaseModel):
    """Schema for LLM response about circuit location."""
    relative_x: float = Field(
        description="Position from left to right of the image (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    relative_y: float = Field(
        description="Position from top to bottom of the image (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    confidence: float = Field(
        description="Confidence level in the detected location (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    ) 