from pydantic import BaseModel, Field

class CircuitImageRequest(BaseModel):
    image_data: str = Field(description="Base64 encoded image data")
    filename: str = Field(description="Original filename")
    content_type: str = Field(description="Image content type (e.g., image/png)")