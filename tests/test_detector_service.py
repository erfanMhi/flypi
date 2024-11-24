import pytest
import os
from pathlib import Path
import asyncio
from app.services.detector_service import process_uploaded_image

@pytest.fixture
def test_images_dir():
    """Fixture to provide the path to test images directory"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "benchmarks", "images", "v1")

@pytest.fixture
def output_dir():
    """Fixture to provide the path to output directory"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(current_dir, "benchmarks", "cropped_images", "v1")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)
    return output_path

def load_image_bytes(image_path: str) -> bytes:
    """Helper function to load image bytes from a file"""
    with open(image_path, "rb") as f:
        return f.read()

def save_cropped_image(output_path: str, image_bytes: bytes) -> None:
    """Helper function to save cropped image bytes to a file"""
    with open(output_path, "wb") as f:
        f.write(image_bytes)

@pytest.mark.asyncio
async def test_process_uploaded_images(test_images_dir, output_dir):
    """Test processing all circuit images in the test directory"""
    
    # Ensure test images directory exists
    assert os.path.exists(test_images_dir), f"Test images directory not found: {test_images_dir}"
    
    # Get all PNG files
    image_files = Path(test_images_dir).glob('*.png')
    print('Image files: ', image_files)
    
    results = []
    for image_path in image_files:
        # Load image bytes
        image_bytes = load_image_bytes(str(image_path))
        
        # Process the image
        result = await process_uploaded_image(image_bytes)
        
        # Save results for assertion
        results.append({
            'image_name': image_path.name,
            'status': result['status'],
            'success': result['cropped_image'] is not None
        })
        
        # If cropping was successful, save the cropped image
        if result['cropped_image']:
            output_path = os.path.join(output_dir, f"cropped_{image_path.name}")
            save_cropped_image(output_path, result['cropped_image'])
    
    # Print processing results
    for result in results:
        print(f"\nImage: {result['image_name']}")
        print(f"Status: {result['status']}")
        print(f"Successfully cropped: {result['success']}")
    
    # Assert that at least one image was processed successfully
    assert any(r['success'] for r in results), "No images were successfully processed" 