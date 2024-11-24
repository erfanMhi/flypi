from pydantic import BaseModel

class CircuitImageRequest(BaseModel):
    image_data: str
    content_type: str = "image/png"  # Default to PNG

class CircuitImageResponseV0(BaseModel):
    components: list[str]

class CircuitImageResponseV1(BaseModel):
    components: list[str]
    connections: list[dict]