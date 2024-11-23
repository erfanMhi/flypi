from fastapi import APIRouter, UploadFile, File
from app.core.exceptions import ImageTooLargeError, InvalidImageTypeError, AnalysisTimeoutError
from app.services.groq_service import analyze_circuit_image
from app.core.config import get_settings
import asyncio

router = APIRouter()
settings = get_settings()

@router.post("/retrieve-circuit-schema")
async def retrieve_circuit_schema(image: UploadFile = File(...)):
    try:
        # Validate file size
        image_content = await image.read()
        if len(image_content) > settings.MAX_IMAGE_SIZE:
            raise ImageTooLargeError()
            
        # Validate image type
        if not image.content_type.startswith('image/'):
            raise InvalidImageTypeError()
        
        # Analyze the circuit
        completion = await analyze_circuit_image(image_content)
        
        return {
            "analysis": completion.choices[0].message,
            "metadata": {
                "model": settings.MODEL_NAME,
                "timestamp": completion.created,
                "file_info": {
                    "filename": image.filename,
                    "content_type": image.content_type,
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