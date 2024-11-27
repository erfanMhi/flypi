from fastapi import HTTPException
import base64
from loguru import logger

class ImageDecoder:
    """Service for decoding base64 image data."""

    @staticmethod
    def decode(image_data: str) -> bytes:
        """
        Decode base64 image data to bytes.

        Args:
            image_data: Base64 encoded image data

        Returns:
            bytes: Decoded image data

        Raises:
            HTTPException: If base64 decoding fails
        """
        try:
            return base64.b64decode(image_data)
        except Exception as e:
            logger.error(f"Base64 decoding failed: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail="Invalid base64 image data"
            ) 