from app.services.groq_client import identify_components_3shot
from fastapi import APIRouter, HTTPException
from app.core.exceptions import ImageTooLargeError, InvalidImageTypeError, AnalysisTimeoutError
from app.services.groq_service import analyze_circuit_image, test_extract_full_schema, test_extract_full_schema_v0
from app.core.config import get_settings
from app.schemas.circuit import CircuitImageRequest, CircuitImageResponseV0
import asyncio
import base64

router = APIRouter()
settings = get_settings()

@router.post("/retrieve-circuit-schema")
async def retrieve_circuit_schema(request: CircuitImageRequest):
    try:
        # Decode base64 image
        try:
            image_content = base64.b64decode(request.image_data)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid base64 image data")
        
        # Validate file size
        if len(image_content) > settings.MAX_IMAGE_SIZE:
            raise ImageTooLargeError()
            
        # Validate image type
        if not request.content_type.startswith('image/'):
            raise InvalidImageTypeError()
        
        # Analyze the circuit
        completion = await analyze_circuit_image(image_content)
        
        return {
            "analysis": completion.choices[0].message,
            "metadata": {
                "model": settings.MODEL_NAME,
                "timestamp": completion.created,
                "file_info": {
                    "content_type": request.content_type,
                    "size": len(image_content)
                }
            }
        }
        
    except asyncio.TimeoutError:
        raise AnalysisTimeoutError()
    except (ImageTooLargeError, InvalidImageTypeError, AnalysisTimeoutError) as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
    

@router.post("/retrieve-circuit-schema-test")
async def retrieve_circuit_schema_test(request: CircuitImageRequest):
    """Process base64 encoded circuit image
    """
    try:
        # Decode base64 image
        try:
            image_bytes = base64.b64decode(request.image_data)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid base64 image data")
        
        # Validate file size
        if len(image_bytes) > settings.MAX_IMAGE_SIZE:
            raise ImageTooLargeError()
            
        # Validate image type
        if not request.content_type.startswith('image/'):
            raise InvalidImageTypeError()
        
        return await test_extract_full_schema(image_bytes, basic=False)
        
    except (ImageTooLargeError, InvalidImageTypeError) as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/retrieve-circuit-schema-v0", response_model=CircuitImageResponseV0)
async def retrieve_circuit_schema_v0(request: CircuitImageRequest) -> CircuitImageResponseV0:
    """Process base64 encoded circuit image and extract schema
    """
    try:
        # Decode base64 image
        try:
            image_bytes = base64.b64decode(request.image_data)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid base64 image data")
        
        # Validate file size
        if len(image_bytes) > settings.MAX_IMAGE_SIZE:
            raise ImageTooLargeError()
            
        # Validate image type
        if not request.content_type.startswith('image/'):
            raise InvalidImageTypeError()
        
        # Process the image bytes
        components = await test_extract_full_schema_v0(image_bytes)
        return CircuitImageResponseV0(components=components)
        
    except (ImageTooLargeError, InvalidImageTypeError) as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test-connection")
async def test_connection():
    return {"message": "Connection successful"}

# @router.post("/get-response-from-audio")
# async def get_response_from_audio(request: AudioRequest):

@router.post("/get-components-from-image")
async def get_components_from_image(request: CircuitImageRequest):
    components = await identify_components_3shot(request.image_data)
    print(components)

    if components is None:
        components = ['battery', 'resistor', 'led', 'switch']

    if isinstance(components, list) and len(components) == 0:
        components = ['battery', 'resistor', 'led', 'switch']   

    formatted_components = []
    for idx, component in enumerate(components['components'], 1):
        formatted_components.append({
            "id": str(idx),
            "type": component['component_type']
        })

    # Create final response structure

    print(formatted_components)
    
    return formatted_components
    

