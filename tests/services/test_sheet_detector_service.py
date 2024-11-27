import os
from pathlib import Path
import asyncio

import pytest
from unittest.mock import Mock

from app.services.sheet_detector_service import SheetDetectorService


@pytest.fixture
def test_images_dir() -> str:
    """Fixture to provide the path to test images directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    return os.path.join(parent_dir, "benchmarks", "images", "v1")


@pytest.fixture
def output_dir() -> str:
    """Fixture to provide the path to output directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    output_path = os.path.join(
        parent_dir, "benchmarks", "cropped_images", "v1"
    )

    # Create output directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)
    return output_path


def load_image_bytes(image_path: str) -> bytes:
    """Helper function to load image bytes from a file."""
    with open(image_path, "rb") as f:
        return f.read()


def save_cropped_image(output_path: str, image_bytes: bytes) -> None:
    """Helper function to save cropped image bytes to a file."""
    with open(output_path, "wb") as f:
        f.write(image_bytes)


@pytest.fixture
def llm_service() -> Mock:
    """Fixture to provide a mock LLM service."""
    mock_llm = Mock()

    # Create a future to simulate an async return value
    future = asyncio.Future()
    future.set_result({
        "relative_x": 0.5,
        "relative_y": 0.5,
        "confidence": 0.8
    })

    # Set the mock to return the future
    mock_llm.communicate.return_value = future

    return mock_llm


@pytest.fixture
def sheet_detector_service(llm_service: Mock) -> SheetDetectorService:
    """Fixture to provide SheetDetectorService instance."""
    return SheetDetectorService(llm_service=llm_service, debug=True)


@pytest.mark.asyncio
async def test_process_single_image(
    sheet_detector_service: SheetDetectorService,
    test_images_dir: str,
    output_dir: str
) -> None:
    """Test processing a single circuit image."""
    image_path = Path(test_images_dir) / "circuit_5.png"

    # Ensure the image file exists
    assert image_path.exists(), f"Image file not found: {image_path}"

    # Load image bytes
    image_bytes = load_image_bytes(str(image_path))

    # Process the image using the service
    result = await sheet_detector_service.process_uploaded_image(image_bytes)

    # Save results for assertion
    success = result["cropped_image"] is not None

    # If cropping was successful, save the cropped image
    if success:
        output_path = os.path.join(output_dir, f"cropped_{image_path.name}")
        save_cropped_image(output_path, result["cropped_image"])

    # Print processing result
    print(f"\nImage: {image_path.name}")
    print(f"Status: {result['status']}")
    print(f"Successfully cropped: {success}")
    
    # Assert that the image was processed successfully
    assert success, "The image was not successfully processed"
