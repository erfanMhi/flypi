from pydantic import BaseModel

class CircuitImageRequest(BaseModel):
    image_data: str
    content_type: str