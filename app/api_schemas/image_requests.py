from pydantic import BaseModel


class CircuitImageRequest(BaseModel):
    """Schema for circuit image upload request.

    Attributes:
        image_data: Base64 encoded image data
        content_type: MIME type of the image
    """
    image_data: str
    content_type: str = "image/png" 