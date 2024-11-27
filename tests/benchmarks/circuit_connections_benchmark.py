import os
import json
from collections import defaultdict
from itertools import combinations
from typing import Dict, Set, Tuple

from loguru import logger

from app.services.connection_identifier_service import (
    ConnectionIdentifierService,
)
from app.core.config import Settings
from app.services.llm_client import LLMService


async def run_connection_identifier_benchmark() -> None:
    """
    Run benchmark tests for circuit connection detection across multiple
    test cases.
    """
    settings = Settings()
    llm_service = LLMService(settings)
    connection_service = ConnectionIdentifierService(settings, llm_service)
    stats = defaultdict(lambda: {"correct": 0, "total": 0})

    test_cases = [
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
    ]

    for test_id in test_cases:
        json_path = os.path.join(
            "tests", "benchmarks", "expected_responses", "v0", f"{test_id}.json"
        )
        image_path = os.path.join(
            "tests", "benchmarks", "images", "v0", f"{test_id}.png"
        )

        if not os.path.exists(json_path) or not os.path.exists(image_path):
            logger.warning(f"Skipping {test_id} - missing files")
            continue

        # Read the image
        with open(image_path, "rb") as img_file:
            image_bytes = img_file.read()

        # Load the expected response
        with open(json_path, "r") as json_file:
            expected_response = json.load(json_file)

        # Get components from expected response
        components = expected_response["components"]

        # Get connections using the service
        actual_connections = await connection_service.identify_connections(
            components=components,
            image_bytes=image_bytes
        )

        def get_connection_pairs(
            connections_data: Dict[str, Set[str]]
        ) -> Set[Tuple[str, str]]:
            pairs = set()
            for conn in connections_data:
                component = conn["component"]
                for connected_to in conn["connections"]:
                    pair = tuple(sorted([component, connected_to]))
                    pairs.add(pair)
            return pairs

        actual_pairs = get_connection_pairs(actual_connections)
        expected_pairs = get_connection_pairs(expected_response["connections"])

        # Update statistics for each component pair
        all_components = {"B1", "R1", "L1", "S1"}
        possible_pairs = {
            tuple(sorted(pair)) for pair in combinations(all_components, 2)
        }

        for pair in possible_pairs:
            component_key = f"{pair[0]}-{pair[1]}"
            stats[component_key]["total"] += 1
            if (pair in expected_pairs and pair in actual_pairs) or (
                pair not in expected_pairs and pair not in actual_pairs
            ):
                stats[component_key]["correct"] += 1

        logger.info(
            f"\nTest case: {test_id}\n"
            f"Expected connections: {sorted(expected_pairs)}\n"
            f"Actual connections: {sorted(actual_pairs)}"
        )

    # Print final statistics
    logger.info("\nConnection Detection Accuracy:")
    for connection_pair, connection_stats in stats.items():
        accuracy = (connection_stats["correct"] / connection_stats["total"]) * 100
        logger.info(
            f"{connection_pair}: {accuracy:.1f}% "
            f"({connection_stats['correct']}/{connection_stats['total']} correct)"
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_connection_identifier_benchmark()) 