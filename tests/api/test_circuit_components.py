import os
import base64
import json
from collections import defaultdict
from typing import Dict, Set

import pytest
from fastapi.testclient import TestClient
from loguru import logger

from app.main import app
from app.api_schemas import ComponentsImageResponse

client = TestClient(app)


@pytest.mark.parametrize("test_id", ["circuit_5"])
def test_circuit_components_responses(test_id: str) -> None:
    """
    Test the /retrieve-circuit-components endpoint with test circuit images.

    Args:
        test_id: The identifier for the test case to run

    Raises:
        AssertionError: If the API response doesn't match expected results
    """
    # Paths to the expected JSON response and corresponding image
    json_path = os.path.join(
        "tests", "benchmarks", "expected_responses", "v0", f"{test_id}.json"
    )
    image_path = os.path.join(
        "tests", "benchmarks", "images", "v0", f"{test_id}.png"
    )

    # Verify that the expected JSON file exists
    assert os.path.exists(json_path), (
        f"Expected response file not found: {json_path}"
    )

    # Verify that the corresponding image exists
    assert os.path.exists(image_path), (
        f"Image file not found for test {test_id}: {image_path}"
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

    # Send the request to the correct API endpoint
    response = client.post(
        "/api/v0/retrieve-circuit-components",
        json=payload
    )

    # Load the expected response
    with open(json_path, "r") as json_file:
        expected_response = json.load(json_file)

    # Assert the response status code
    assert response.status_code == 200, (
        f"API response status code {response.status_code} != 200"
    )

    # Validate response matches ComponentsImageResponse schema
    response_data = response.json()
    assert "components" in response_data, (
        "Response missing 'components' field"
    )

    # Compare components and update statistics
    actual_components = {comp["type"] for comp in response_data["components"]}
    expected_components = {comp["type"] for comp in expected_response["components"]}

    # Original assertion
    logger.info(
        f"Expected: {sorted(expected_components)}\n" +
        f"Actual: {sorted(actual_components)}"
    )

    logger.info(f"Test case: {test_id}")

    assert actual_components == expected_components, (
        f"Component mismatch for {test_id}:\n"
        f"Expected: {sorted(expected_components)}\n"
        f"Got: {sorted(actual_components)}"
    )