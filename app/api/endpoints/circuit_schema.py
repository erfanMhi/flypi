from fastapi import APIRouter, HTTPException
from loguru import logger

from app.core.exceptions import ImageTooLargeError, InvalidImageTypeError
from app.services.circuit_service import extract_schema
from app.core.config import get_settings
from app.api_schemas import CircuitImageRequest, SchemaImageResponse, Component, Connection
from app.services.image_validation import ImageValidator
from app.services.image_decoder import ImageDecoder

router = APIRouter()
settings = get_settings()


@router.post("/retrieve-circuit-schema")
async def retrieve_circuit_schema(
    request: CircuitImageRequest
) -> SchemaImageResponse:
    """Process base64 encoded circuit image."""
    try:
        # First decode the base64 image
        image_decoder = ImageDecoder()
        image_bytes = image_decoder.decode(request.image_data)
        
        # Then validate the decoded image
        image_validator = ImageValidator(settings)
        image_validator.validate(request.content_type, image_bytes)
        
        # Pass validated data to service
        schema = await extract_schema(image_bytes)

        # Format the schema
        formatted_components = []
        formatted_connections = []
        for component in schema['components']:
            formatted_components.append(Component(**component))
        
        for connection in schema['connections']:
            formatted_connections.append(Connection(**connection))
        
        return SchemaImageResponse(components=formatted_components, connections=formatted_connections)
        
    except (ImageTooLargeError, InvalidImageTypeError) as e:
        raise e
    except HTTPException as e:
        # This catches base64 decoding errors from ImageDecoder
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))