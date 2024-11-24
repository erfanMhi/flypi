import pytest
import os
import base64
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.parametrize("test_id", [
    "circuit_1",
    "circuit_2",
    "circuit_3",
    "circuit_4",
    "circuit_5",
    "circuit_6",
    "circuit_7",
    "circuit_8",
    "circuit_9",
    "circuit_10",
])
def test_circuit_v0_responses(test_id):
    """
    Test the /retrieve-circuit-schema-test endpoint with all expected v0 responses.
    """
    # Paths to the expected JSON response and corresponding image
    json_path = os.path.join("tests", "benchmarks", "expected_responses", "v0", f"{test_id}.json")
    image_path = os.path.join("tests", "benchmarks", "images", "v0", f"{test_id}.png")

    # Verify that the expected JSON file exists
    assert os.path.exists(json_path), f"Expected response file not found: {json_path}"

    # Verify that the corresponding image exists
    assert os.path.exists(image_path), f"Image file not found for test {test_id}: {image_path}"

    # Read and encode the image
    with open(image_path, "rb") as img_file:
        image_bytes = img_file.read()
        base64_image = base64.b64encode(image_bytes).decode('utf-8')

    # Prepare the payload
    payload = {
        "image_data": base64_image,
        "content_type": "image/png"
    }

    # Send the request to the API
    response = client.post(
        "/api/v1/get-components-from-image",
        json=payload
    )

    # Load the expected response
    with open(json_path, "r") as json_file:
        expected_response = json.load(json_file)
    
    print('Response: ', response.json())
    # Assert the response status code
    assert response.status_code == 200, f"API response status code {response.status_code} != 200"
    print(f"the circuit is {test_id}")
    expected_components = [component['type'] for component in expected_response['components']]
    print(f"expected_components: {expected_components}")
    response_components = [component['type'] for component in response.json()]
    print(f"response_components: {response_components}")
    # Assert the response JSON matches the expected response
    assert set(response_components) == set(expected_components), f"API response does not match expected for {test_id}"
