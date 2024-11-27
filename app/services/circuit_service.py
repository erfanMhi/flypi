import base64
from typing import Dict, Any, List
from app.services.component_identifier_service import ComponentIdentifierService
from app.services.connection_identifier_service import ConnectionIdentifierService
from app.services.sheet_detector_service import SheetDetectorService
from app.services.llm_client import LLMService
from app.core.config import get_settings
from loguru import logger
settings = get_settings()
llm_service = LLMService(settings)

async def identify_components(image_bytes: bytes) -> set[str]:
    identifier = ComponentIdentifierService(settings, llm_service)
    return await identifier.identify_components(image_bytes)

async def identify_connections(components: set[str], image_bytes: bytes) -> List[Dict[str, Any]]:
    identifier = ConnectionIdentifierService(settings, llm_service)
    return await identifier.identify_connections(components, image_bytes)

async def extract_sheet_image(image_bytes: bytes) -> bytes:
    """Extract and process the circuit diagram from the uploaded image.
    
    Args:
        image_bytes: Raw image bytes containing the circuit diagram
        
    Returns:
        bytes: Processed image bytes of the extracted circuit
        
    Raises:
        ValueError: If circuit diagram cannot be detected in the image
    """
    detector = SheetDetectorService(llm_service)
    result = await detector.process_uploaded_image(image_bytes)
    
    if result["status"] != "Circuit diagram detected and cropped successfully.":
        raise ValueError("Failed to detect circuit diagram in image")
        
    if not result["cropped_image"]:
        raise ValueError("No circuit diagram found in processed image")
        
    return result["cropped_image"]

async def extract_schema(image_bytes: bytes) -> Dict[str, Any]:
    """Extract a full circuit schema from an image using the CircuitSchema model.
    
    This function:
    1. Shows examples of basic components (battery, resistor)
    2. Asks for a structured analysis of the circuit
    3. Returns the analysis in CircuitSchema format

    If basic is False, we go into a more detailed analysis of the circuit
    """
    page_image_bytes = await extract_sheet_image(image_bytes)
    
    components = await identify_components(page_image_bytes)
    logger.info(f"Components: {components}")
    connections = await identify_connections(components, page_image_bytes)
    logger.info(f"Connections: {connections}")
    return {
        "components": components,
        "connections": connections
    }

async def extract_components(image_bytes: bytes) -> List[str]:
    """Extract only the components list from the schema as return it as a list

    This is a simplified version of the full schema extraction
    """

    components_available = await identify_components(image_bytes)

    return list(components_available)