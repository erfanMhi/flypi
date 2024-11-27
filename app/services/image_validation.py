from app.core.exceptions import ImageTooLargeError, InvalidImageTypeError
from app.core.config import Settings
from loguru import logger

class ImageValidator:
    """Service for validating image data and content types."""

    def __init__(self, settings: Settings):
        """
        Initialize the image validator.

        Args:
            settings: Application settings containing validation parameters
        """
        self._settings = settings

    def validate(self, content_type: str, image_bytes: bytes) -> None:
        """
        Validate image content type and size.

        Args:
            content_type: The content type of the image
            image_bytes: Raw image data

        Raises:
            InvalidImageTypeError: If content type is not an image
            ImageTooLargeError: If image exceeds size limit
        """
        self._validate_content_type(content_type)
        self._validate_size(image_bytes)

    def _validate_content_type(self, content_type: str) -> None:
        if not content_type.startswith("image/"):
            logger.warning(f"Invalid content type received: {content_type}")
            raise InvalidImageTypeError()

    def _validate_size(self, image_bytes: bytes) -> None:
        if len(image_bytes) > self._settings.MAX_IMAGE_SIZE:
            logger.warning(
                f"Image size {len(image_bytes)} exceeds limit "
                f"{self._settings.MAX_IMAGE_SIZE}"
            )
            raise ImageTooLargeError() 