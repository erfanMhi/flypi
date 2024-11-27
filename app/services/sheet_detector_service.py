import cv2
import numpy as np
from typing import Dict, Optional, Tuple
import asyncio
import os
from pydantic import BaseModel
from app.services.llm_client import LLMService
from app.prompt_schemas.circuit_location_schema import CircuitLocation

class SheetDetectorService:
    """Service for detecting and processing circuit diagrams in images.
    
    This service uses a two-stage approach to detect and extract circuit diagrams:
    1. Coarse Location: Uses LLM vision model to approximately locate the circuit
       diagram within the image. This approach was chosen over traditional sheet
       detection because paper sheets are often partially obstructed by hands
       or other objects, making corner detection unreliable.
    2. Fine Detection: Uses computer vision techniques (contour detection,
       morphological operations) to precisely identify and extract the circuit
       diagram from the region of interest.

    The service includes debug capabilities that can save intermediate processing
    steps as images for troubleshooting and optimization.

    Attributes:
        debug (bool): When True, saves intermediate processing steps as images
        _debug_dir (str): Directory where debug images are saved
        llm_service (LLMService): Service for LLM-based image analysis

    Note:
        While named 'SheetDetector', this service actually focuses on detecting
        the circuit diagram itself rather than the sheet boundaries, as this
        proves more reliable in real-world usage where sheets may be partially
        obscured or held by users.
    """

    def __init__(self, llm_service: LLMService, debug: bool = False):
        self.debug = debug
        self._debug_dir = "debug_images"
        self.llm_service = llm_service
        if debug:
            os.makedirs(self._debug_dir, exist_ok=True)

    async def _get_circuit_location(self, image_bytes: bytes) -> CircuitLocation:
        """Use LLM to identify the approximate location of the circuit."""
        prompt = """
        Analyze this image and identify the approximate location of the hand-drawn circuit diagram.
        Provide the relative position as coordinates where:
        - relative_x: 0.0 is leftmost, 1.0 is rightmost
        - relative_y: 0.0 is topmost, 1.0 is bottommost
        - confidence: how confident you are in this location (0.0 to 1.0)
        
        Focus on finding black drawings on white paper. Ignore tables, furniture, or other objects.
        """
        
        location = await self.llm_service.communicate(
            prompt=prompt,
            image_bytes=image_bytes,
            schema=CircuitLocation
        )
        return CircuitLocation(**location)

    def _get_region_of_interest(self, image: np.ndarray, location: CircuitLocation) -> Tuple[np.ndarray, Tuple[int, int]]:
        """Get the region of interest based on LLM-provided location."""
        height, width = image.shape[:2]
        
        # Calculate the center point of the region
        center_x = int(location.relative_x * width)
        center_y = int(location.relative_y * height)
        
        # Define region size based on confidence
        # Lower confidence = larger search area
        region_size = int(min(width, height) * (1.0 - location.confidence * 0.5))
        
        # Calculate region boundaries
        x_start = max(0, center_x - region_size // 2)
        y_start = max(0, center_y - region_size // 2)
        x_end = min(width, center_x + region_size // 2)
        y_end = min(height, center_y + region_size // 2)
        
        # Extract region of interest
        roi = image[y_start:y_end, x_start:x_end]
        return roi, (x_start, y_start)

    def _save_debug_image(self, image: np.ndarray, name: str) -> None:
        """Saves an image for debugging purposes if debug mode is enabled."""
        if self.debug:
            path = os.path.join(self._debug_dir, f"{name}.jpg")
            cv2.imwrite(path, image)

    async def process_uploaded_image(self, image_bytes: bytes) -> Dict[str, Optional[bytes]]:
        """Processes the uploaded image to detect and extract the circuit diagram."""
        image = self._read_image(image_bytes)
        self._save_debug_image(image, "1_original")
        
        # Get circuit location from LLM
        location = await self._get_circuit_location(image_bytes)
        
        # Get region of interest
        roi, (x_offset, y_offset) = self._get_region_of_interest(image, location)
        self._save_debug_image(roi, "2_roi")
        
        # Process the ROI
        preprocessed_roi = self._preprocess_image(roi)
        self._save_debug_image(preprocessed_roi, "3_preprocessed")
        
        circuit_contour = self._find_circuit_contour(preprocessed_roi)
        
        if circuit_contour is None:
            return {
                "status": "Circuit diagram not found.",
                "cropped_image": None
            }
        
        # Adjust contour coordinates to original image space
        circuit_contour += np.array([x_offset, y_offset])
        
        # Save image with contour drawn
        contour_image = image.copy()
        cv2.drawContours(contour_image, [circuit_contour], -1, (0, 255, 0), 2)
        self._save_debug_image(contour_image, "4_circuit_contour")
        
        warped_image = self._warp_perspective(image, circuit_contour)
        self._save_debug_image(warped_image, "5_warped")
        
        cropped_image_bytes = self._encode_image(warped_image)
        
        return {
            "status": "Circuit diagram detected and cropped successfully.",
            "cropped_image": cropped_image_bytes
        }

    def _read_image(self, image_bytes: bytes) -> np.ndarray:
        """Converts image bytes to OpenCV image."""
        image_np = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
        return image

    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess the image for contour detection."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 50, 150)
        
        # Apply morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)
        
        return closed

    def _find_circuit_contour(self, edged: np.ndarray) -> Optional[np.ndarray]:
        """Finds the contour of the circuit diagram."""
        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None

        # Filter contours by size and aspect ratio
        circuit_contours = [
            c for c in contours if self._is_circuit_contour(c)
        ]

        if not circuit_contours:
            return None

        # Sort by area to find the largest likely circuit
        circuit_contours = sorted(circuit_contours, key=cv2.contourArea, reverse=True)
        
        return circuit_contours[0]

    def _is_circuit_contour(self, contour: np.ndarray) -> bool:
        """Checks if the contour is likely a circuit diagram."""
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / h if h != 0 else 0
        area = cv2.contourArea(contour)
        return 0.5 <= aspect_ratio <= 2.0 and area > 1000  # Adjust thresholds as needed

    def _warp_perspective(self, image: np.ndarray, contour: np.ndarray) -> np.ndarray:
        """Applies perspective transform to get a top-down view of the circuit."""
        rect = cv2.boundingRect(contour)
        x, y, w, h = rect
        
        # Define a larger margin
        margin = 50  # Adjust this value as needed for a wider area
        
        # Calculate new coordinates with margin
        x_start = max(x - margin, 0)
        y_start = max(y - margin, 0)
        x_end = min(x + w + margin, image.shape[1])
        y_end = min(y + h + margin, image.shape[0])
        
        # Crop the image with the new coordinates
        cropped = image[y_start:y_end, x_start:x_end]
        return cropped

    def _encode_image(self, image: np.ndarray) -> bytes:
        """Encodes the image to bytes."""
        _, buffer = cv2.imencode('.jpg', image)
        return buffer.tobytes()
