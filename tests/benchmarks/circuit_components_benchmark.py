"""Circuit component detection benchmark module.

This module provides functionality to benchmark the accuracy of circuit
component detection across multiple test cases.
"""
from collections import defaultdict
import base64
import json
import os
import sys
from typing import Dict, List, Set, DefaultDict

from fastapi.testclient import TestClient
from loguru import logger

# Add project root to path
project_root = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from app.main import app 

# Constants
COMPONENT_TYPES = {"switch", "resistor", "led", "battery"}
TEST_CASES = [f"circuit_{i}" for i in range(1, 11)]


def load_test_files(
    test_id: str,
    version: str = "v0"
) -> tuple[dict | None, str | None]:
    """Load test files for a given test case.

    Args:
        test_id: The identifier for the test case.
        version: API version string. Defaults to "v0".

    Returns:
        Tuple containing the expected response and base64 encoded image,
        or (None, None) if files are missing.
    """
    json_path = os.path.join(
        "tests", "benchmarks", "expected_responses", 
        version, f"{test_id}.json"
    )
    image_path = os.path.join(
        "tests", "benchmarks", "images",
        version, f"{test_id}.png"
    )

    if not os.path.exists(json_path) or not os.path.exists(image_path):
        logger.warning(f"Skipping {test_id} - missing files")
        return None, None

    with open(json_path, "r") as json_file:
        expected_response = json.load(json_file)

    with open(image_path, "rb") as img_file:
        image_bytes = img_file.read()
        base64_image = base64.b64encode(image_bytes).decode("utf-8")

    return expected_response, base64_image


def get_component_sets(
    response_data: dict,
    expected_response: dict
) -> tuple[Set[str], Set[str]]:
    """Extract component sets from response and expected data.

    Args:
        response_data: The actual API response data.
        expected_response: The expected response data.

    Returns:
        Tuple of (actual_components, expected_components) sets.
    """
    actual_components = {
        comp["type"] for comp in response_data.get("components", [])
    }
    expected_components = {
        comp["type"] for comp in expected_response.get("components", [])
    }
    return actual_components, expected_components


def update_statistics(
    stats: DefaultDict[str, Dict[str, int]],
    actual_components: Set[str],
    expected_components: Set[str]
) -> None:
    """Update detection statistics for each component type.

    Args:
        stats: Statistics dictionary to update.
        actual_components: Set of detected components.
        expected_components: Set of expected components.
    """
    for component in COMPONENT_TYPES:
        if ((component in expected_components and 
             component in actual_components) or
            (component not in expected_components and 
             component not in actual_components)):
            stats[component]["correct"] += 1


def print_results(
    test_id: str,
    expected_components: Set[str],
    actual_components: Set[str],
    stats: DefaultDict[str, Dict[str, int]],
    test_cases: List[str]
) -> None:
    """Print test results and final statistics.

    Args:
        test_id: The identifier for the test case.
        expected_components: Set of expected components.
        actual_components: Set of detected components.
        stats: Statistics dictionary.
        test_cases: List of all test cases.
    """
    logger.info(
        f"\nTest case: {test_id}\n"
        f"Expected: {sorted(expected_components)}\n"
        f"Actual: {sorted(actual_components)}"
    )

    if test_id == test_cases[-1]:  # Print final stats after last test
        logger.info("\nComponent Detection Accuracy:")
        for component, component_stats in stats.items():
            accuracy = (component_stats["correct"] / len(test_cases)) * 100
            logger.info(
                f"{component}: {accuracy:.1f}% "
                f"({component_stats['correct']}/{len(test_cases)} correct)"
            )


def run_component_identifier_benchmark() -> None:
    """Run benchmark tests for circuit component detection."""
    client = TestClient(app)
    stats: DefaultDict[str, Dict[str, int]] = defaultdict(
        lambda: {"correct": 0, "total": 0}
    )

    for test_id in TEST_CASES:
        expected_response, base64_image = load_test_files(test_id)
        if not expected_response or not base64_image:
            continue

        # Send request to API
        response = client.post(
            "/api/v0/retrieve-circuit-components",
            json={"image_data": base64_image, "content_type": "image/png"}
        )

        if response.status_code != 200:
            logger.error(
                f"Failed test case {test_id}: Status code {response.status_code}"
            )
            continue

        response_data = response.json()
        if "components" not in response_data:
            logger.error(f"Failed test case {test_id}: Missing 'components' field")
            continue

        # Process results
        actual_components, expected_components = get_component_sets(
            response_data, expected_response
        )
        update_statistics(stats, actual_components, expected_components)
        print_results(
            test_id, expected_components, actual_components, stats, TEST_CASES
        )


if __name__ == "__main__":
    run_component_identifier_benchmark() 