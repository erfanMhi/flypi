import pytest
from fastapi.testclient import TestClient
from app.main import app
import os

client = TestClient(app)

def test_circuit_analysis():
    """Test circuit analysis with the specific image"""
    
    # Image path
    image_path = "/Users/erfanmiahi/projects/github/flypi/circuit.png"
    
    # Verify image exists
    assert os.path.exists(image_path), f"Test image not found at {image_path}"
    
    # Make the API call
    with open(image_path, "rb") as image_file:
        files = {
            "image": ("circuit.png", image_file, "image/png")
        }
        response = client.post("/api/v1/retrieve-circuit-schema", files=files)
    
    # Print response for debugging
    print("Response Status:", response.status_code)
    print("Response Body:", response.json())
    
    # Basic assertion
    assert response.status_code == 200 