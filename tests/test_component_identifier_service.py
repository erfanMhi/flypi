import pytest
import os
from app.services.component_identifier_service import ComponentIdentifierService

@pytest.fixture
def component_identifier():
    return ComponentIdentifierService()

@pytest.fixture
def test_image_bytes():
    # Get the absolute path to the test image
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, "circuit.png")
    image_path = 'circuit.png'
    
    # Ensure the image exists
    assert os.path.exists(image_path), f"Test image not found at {image_path}"
    
    # Read the image bytes
    with open(image_path, "rb") as f:
        return f.read()

@pytest.mark.asyncio
async def test_identify_components(component_identifier, test_image_bytes):
    """
    Test that the ComponentIdentifierService correctly identifies components
    in a circuit diagram containing a battery, resistor, and switch.
    """
    # When: We analyze the circuit image
    identified_components = await component_identifier.identify_components(test_image_bytes)
    
    # Then: The correct components should be identified
    expected_components = {"resistor", "battery"}
    
    assert identified_components == expected_components, \
        f"Expected components {expected_components}, but got {identified_components}"
    
