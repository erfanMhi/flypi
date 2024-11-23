from fastapi import APIRouter, HTTPException
from app.core.exceptions import ImageTooLargeError, InvalidImageTypeError, AnalysisTimeoutError
from app.services.groq_service import analyze_circuit_image, test_extract_full_schema
from app.core.config import get_settings
from app.schemas.circuit import CircuitImageRequest
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
    """Here we will recieve the image and then pass the image to an analysis service
    """
    
    return await test_extract_full_schema(request)

@router.get("/test-connection")
async def test_connection():
    return {"message": "Connection successful"}

