import pytest
import os
import base64
from app.services.groq_service import test_extract_full_schema
import asyncio
from typing import Dict, Any
import json
from pathlib import Path

# Test data structure to define expected outputs for each test image
TEST_CASES = {
    "simple_circuit.png": {
        "components": [
            {"id": "B1", "type": "battery", "connections": ["R1"]},
            {"id": "R1", "type": "resistor", "connections": ["B1", "LED1"]},
            {"id": "LED1", "type": "led", "connections": ["R1", "B1"]}
        ]
    },
    "switch_circuit.png": {
        "components": [
            {"id": "B1", "type": "battery", "connections": ["S1"]},
            {"id": "S1", "type": "switch", "connections": ["B1", "R1"]},
            {"id": "R1", "type": "resistor", "connections": ["S1", "LED1"]},
            {"id": "LED1", "type": "led", "connections": ["R1", "B1"]}
        ]
    }
    # Add more test cases as needed
}

@pytest.fixture
def test_images_dir():
    """Fixture to provide the path to test images directory"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "benchmarks", "images", "v1")

@pytest.fixture
def expected_responses_dir():
    """Fixture to provide the path to expected responses directory"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "benchmarks", "expected_responses", "v1")

def load_image_bytes(image_path: str) -> bytes:
    """Helper function to load image bytes from a file"""
    with open(image_path, "rb") as f:
        return f.read()

def load_expected_response(response_path: str) -> Dict[str, Any]:
    """Helper function to load expected response from JSON file"""
    with open(response_path, 'r') as f:
        return json.load(f)

def validate_circuit_schema(result: Dict[str, Any], expected: Dict[str, Any]):
    """Helper function to validate circuit schema results"""
    assert "components" in result, "Result missing 'components' key"
    
    # Check if number of components matches
    assert len(result["components"]) == len(expected["components"]), \
        f"Expected {len(expected['components'])} components, got {len(result['components'])}"
    
    # Create dictionaries for easier comparison
    result_components = {comp["id"]: comp for comp in result["components"]}
    expected_components = {comp["id"]: comp for comp in expected["components"]}
    
    # Compare components
    for comp_id, expected_comp in expected_components.items():
        assert comp_id in result_components, f"Missing component {comp_id}"
        result_comp = result_components[comp_id]
        
        assert result_comp["type"] == expected_comp["type"], \
            f"Component {comp_id} type mismatch: expected {expected_comp['type']}, got {result_comp['type']}"
        
        # Compare connections (order-independent)
        assert set(result_comp["connections"]) == set(expected_comp["connections"]), \
            f"Component {comp_id} connections mismatch: expected {expected_comp['connections']}, got {result_comp['connections']}"

@pytest.mark.asyncio
async def test_circuit_schema_extraction(test_images_dir, expected_responses_dir):
    """Test circuit schema extraction for all test images"""
    
    # Ensure directories exist
    assert os.path.exists(test_images_dir), f"Test images directory not found: {test_images_dir}"
    assert os.path.exists(expected_responses_dir), f"Expected responses directory not found: {expected_responses_dir}"
    
    # Get all image files
    image_files = Path(test_images_dir).glob('*.png')
    
    for image_path in image_files:
        # Construct path to expected response JSON
        response_path = os.path.join(
            expected_responses_dir, 
            f"{image_path.stem}.json"
        )
        
        # Skip if expected response doesn't exist
        if not os.path.exists(response_path):
            pytest.skip(f"Expected response not found for {image_path.name}")
        
        # Load image and expected response
        image_bytes = load_image_bytes(str(image_path))
        expected_schema = load_expected_response(response_path)
        
        # Run extraction
        result = await test_extract_full_schema(image_bytes, basic=False)
        
        # Validate results
        try:
            validate_circuit_schema(result, expected_schema)
        except AssertionError as e:
            pytest.fail(f"Validation failed for {image_path.name}: {str(e)}")

@pytest.mark.asyncio
async def test_invalid_image_handling():
    """Test handling of invalid image input"""
    
    # Test with empty bytes
    result = await test_extract_full_schema(b"", basic=False)
    assert result == {}, "Expected empty dict for invalid image"
    
    # Test with invalid image data
    result = await test_extract_full_schema(b"invalid_image_data", basic=False)
    assert result == {}, "Expected empty dict for corrupted image data" 