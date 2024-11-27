"""
Test suite for the ComponentIdentifierService.
"""

import os
from venv import logger

import pytest
from loguru import logger

from app.services.component_identifier_service import ComponentIdentifierService
from app.services.llm_client import LLMService
from app.core.config import get_settings


@pytest.fixture
def component_identifier() -> ComponentIdentifierService:
    """Fixture to provide a ComponentIdentifierService instance."""
    settings = get_settings()
    llm_service = LLMService(settings)
    return ComponentIdentifierService(settings, llm_service)


@pytest.fixture
def test_image_bytes() -> bytes:
    """Fixture to provide the bytes of a test image."""
    # Get the absolute path to the test image
    current_dir = os.path.dirname(os.path.abspath(__file__))
    current_dir = os.path.dirname(current_dir)
    image_path = os.path.join(current_dir, "benchmarks/images/v0/circuit_9.png")

    # Ensure the image exists
    assert os.path.exists(image_path), f"Test image not found at {image_path}"

    # Read the image bytes
    with open(image_path, "rb") as f:
        return f.read()


@pytest.mark.asyncio
async def test_identify_components(
    component_identifier: ComponentIdentifierService, test_image_bytes: bytes
) -> None:
    """
    Test that the ComponentIdentifierService correctly identifies components
    in a circuit diagram containing a battery, resistor, and switch.

    Args:
        component_identifier: The service to identify components.
        test_image_bytes: The bytes of the test image.

    Raises:
        AssertionError: If the identified components do not match the expected.
    """
    # When: We analyze the circuit image
    identified_components = await component_identifier.identify_components(
        test_image_bytes
    )

    logger.info(f"Identified components: {identified_components}")

    # Then: The correct components should be identified
    expected_components = [
        {'id': 'b1', 'type': 'battery'},
        {'id': 'r1', 'type': 'resistor'}
    ]

    logger.info(f"Expected components: {expected_components}")

    # Convert lists of dictionaries to sets of tuples for order-independent comparison
    identified_set = set(tuple(sorted(component.items())) for component in identified_components)
    expected_set = set(tuple(sorted(component.items())) for component in expected_components)

    assert identified_set == expected_set, (
        f"Expected components {identified_components}, "
        f"but got {expected_components}"
    )
    
