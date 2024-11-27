import os
import base64
import json
from typing import Optional

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api_schemas import SchemaImageResponse

client = TestClient(app)


@pytest.mark.parametrize("test_id", ["circuit_5"])
def test_circuit_schema_responses(test_id: str) -> None:
    """
    Test the /retrieve-circuit-schema endpoint with test circuit images.

    Args:
        test_id: The identifier for the test case to run

    Raises:
        AssertionError: If the API response doesn't match expected results
    """
    # Paths to the expected JSON response and corresponding image
    json_path = os.path.join(
        "tests", "benchmarks", "expected_responses", "v1", f"{test_id}.json"
    )
    image_path = os.path.join(
        "tests", "benchmarks", "images", "v1", f"{test_id}.png"
    )

    # Verify files exist
    assert os.path.exists(json_path), (
        f"Expected response file not found: {json_path}"
    )
    assert os.path.exists(image_path), (
        f"Image file not found: {image_path}"
    )

    # Read and encode the image
    with open(image_path, "rb") as img_file:
        image_bytes = img_file.read()
        base64_image = base64.b64encode(image_bytes).decode("utf-8")

    # Prepare the payload
    payload = {
        "image_data": base64_image,
        "content_type": "image/png"
    }

    # Send request to the schema endpoint
    response = client.post(
        "/api/v0/retrieve-circuit-schema",
        json=payload
    )

    # Enhanced error reporting
    if response.status_code != 200:
        print("\nServer Response Status:", response.status_code)
        print("\nServer Headers:", dict(response.headers))
        print("\nServer Response Body:", response.text)
        try:
            error_detail = response.json()
            print("\nDetailed Error:", json.dumps(error_detail, indent=2))
        except json.JSONDecodeError:
            print("\nCould not parse error response as JSON")

    # Load the expected response
    with open(json_path, "r") as json_file:
        expected_response = json.load(json_file)

    # Assert response status
    assert response.status_code == 200, (
        f"API response status code {response.status_code} != 200"
    )

    # Validate response structure
    response_data = response.json()
    assert "components" in response_data, (
        "Response missing 'components' field"
    )
    assert "connections" in response_data, (
        "Response missing 'connections' field"
    )