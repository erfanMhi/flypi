import pytest
from fastapi.testclient import TestClient
from app.main import app
import os
import base64

client = TestClient(app)

def test_circuit_analysis():
    """Test circuit analysis with base64 encoded image"""
    
    # Image path
    image_path = "/Users/erfanmiahi/projects/github/flypi/circuit.png"
    
    # Verify image exists
    assert os.path.exists(image_path), f"Test image not found at {image_path}"
    
    # Read and encode image
    with open(image_path, "rb") as image_file:
        image_content = image_file.read()
        base64_image = base64.b64encode(image_content).decode('utf-8')
    
    # Make the API call
    response = client.post(
        "/api/v1/retrieve-circuit-schema",
        json={
            "image_data": base64_image,
            "content_type": "image/png"
        }
    )
    
    # Print response for debugging
    print("Response Status:", response.status_code)
    print("Response Body:", response.json())
    
    # Basic assertion
    assert response.status_code == 200