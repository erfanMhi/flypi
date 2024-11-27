from fastapi import APIRouter, HTTPException
from loguru import logger

from app.core.exceptions import ImageTooLargeError, InvalidImageTypeError
from app.services.circuit_service import extract_components
from app.core.config import get_settings
from app.api_schemas import CircuitImageRequest,  ComponentsImageResponse, Component
from app.services.image_validation import ImageValidator
from app.services.image_decoder import ImageDecoder


router = APIRouter()
settings = get_settings()


@router.post("/retrieve-circuit-components")
async def retrieve_circuit_components(request: CircuitImageRequest) -> ComponentsImageResponse:
    try:

        # First decode the base64 image
        image_decoder = ImageDecoder()
        image_bytes = image_decoder.decode(request.image_data)
        
        # Then validate the decoded image
        image_validator = ImageValidator(settings)
        image_validator.validate(request.content_type, image_bytes)
        
    except (ImageTooLargeError, InvalidImageTypeError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException as e:
        # This catches base64 decoding errors from ImageDecoder
        raise e

    components = await extract_components(image_bytes)  # Pass decoded bytes instead of raw base64
    logger.debug(f"Extracted components: {components}")

    formatted_components = []
    for component in components:
        component = Component(**component)
        formatted_components.append(component)

    return ComponentsImageResponse(components=formatted_components)