"""Sheet detector benchmark module.

This module provides functionality to benchmark the accuracy of sheet detection
across multiple test cases.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, Any

import cv2
import numpy as np
from loguru import logger

from app.services.sheet_detector_service import SheetDetectorService
from app.services.llm_client import LLMService
from app.core.config import get_settings

# Constants
TEST_CASES = [f"circuit_{i}" for i in range(1, 12)]


async def run_sheet_detection_benchmark() -> None:
    """Run benchmark tests for sheet detection across multiple test cases."""
    # Initialize services
    settings = get_settings()
    llm_service = LLMService(settings)
    detector = SheetDetectorService(llm_service=llm_service, debug=True)

    success_count = 0
    total_count = 0

    # Create output directory for cropped images
    output_dir = Path("tests/benchmarks/images/v1/cropped_images")
    output_dir.mkdir(parents=True, exist_ok=True)

    for test_id in TEST_CASES:
        # Construct image path
        image_path = Path(f"tests/benchmarks/images/v1/{test_id}.png")

        if not image_path.exists():
            logger.warning(f"Skipping {test_id} - image file not found")
            continue

        total_count += 1
        logger.info(f"\nProcessing test case: {test_id}")

        # Read and process image
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        try:
            result: Dict[str, Any] = await detector.process_uploaded_image(
                image_bytes
            )

            if result["cropped_image"]:
                # Convert bytes back to image for saving
                np_arr = cv2.imdecode(
                    np.frombuffer(result["cropped_image"], np.uint8),
                    cv2.IMREAD_COLOR
                )

                # Save the result in benchmarks directory
                output_path = output_dir / f"{test_id}_cropped.png"
                cv2.imwrite(str(output_path), np_arr)

                logger.info(f"Processed image saved to: {output_path}")
                logger.info(f"Status: {result['status']}")
                success_count += 1
            else:
                logger.error(f"Failed to detect sheet: {result['status']}")

        except Exception as e:
            logger.error(f"Error processing {test_id}: {str(e)}")

    # Print final statistics
    accuracy = (success_count / total_count * 100) if total_count > 0 else 0
    logger.info("\nSheet Detection Results:")
    logger.info(
        f"Success Rate: {accuracy:.1f}% "
        f"({success_count}/{total_count} successful)"
    )


if __name__ == "__main__":
    # Clear the LRU cache to ensure fresh settings
    get_settings.cache_clear()
    asyncio.run(run_sheet_detection_benchmark()) 