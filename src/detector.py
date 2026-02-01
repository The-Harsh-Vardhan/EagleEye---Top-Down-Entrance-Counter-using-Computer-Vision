"""
Person detection module for EagleEye People Counting System.

Uses YOLOv8 for real-time person detection with filtering for
confidence threshold and minimum detection size.
"""

import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass

from ultralytics import YOLO

from .config import (
    YOLO_MODEL,
    CONFIDENCE_THRESHOLD,
    MIN_DETECTION_SIZE,
    PERSON_CLASS_ID
)


@dataclass
class Detection:
    """
    Container for a single person detection.
    
    Attributes:
        bbox: Bounding box as (x1, y1, x2, y2) in pixels
        confidence: Detection confidence score (0.0 - 1.0)
        center: Center point of the bounding box (x, y)
    """
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    confidence: float
    
    @property
    def center(self) -> Tuple[int, int]:
        """Calculate center point of the bounding box."""
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) // 2, (y1 + y2) // 2)
    
    @property
    def width(self) -> int:
        """Get bounding box width."""
        return self.bbox[2] - self.bbox[0]
    
    @property
    def height(self) -> int:
        """Get bounding box height."""
        return self.bbox[3] - self.bbox[1]
    
    def to_xyxy(self) -> np.ndarray:
        """Convert bbox to numpy array [x1, y1, x2, y2]."""
        return np.array(self.bbox)
    
    def to_xywh(self) -> Tuple[int, int, int, int]:
        """Convert bbox to (x_center, y_center, width, height) format."""
        x1, y1, x2, y2 = self.bbox
        w = x2 - x1
        h = y2 - y1
        return (x1 + w // 2, y1 + h // 2, w, h)


class PersonDetector:
    """
    YOLOv8-based person detector.
    
    Wraps the Ultralytics YOLO model to provide a clean interface
    for person detection with configurable filtering.
    """
    
    def __init__(self, 
                 model_path: str = YOLO_MODEL,
                 confidence_threshold: float = CONFIDENCE_THRESHOLD,
                 min_size: Tuple[int, int] = MIN_DETECTION_SIZE):
        """
        Initialize the person detector.
        
        Args:
            model_path: Path to YOLO model weights or model name
                       (e.g., 'yolov8n.pt' will auto-download)
            confidence_threshold: Minimum confidence for detections
            min_size: Minimum (width, height) for valid detections
        """
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold
        self.min_width, self.min_height = min_size
        
        print(f"Loaded YOLOv8 model: {model_path}")
        print(f"Confidence threshold: {confidence_threshold}")
        print(f"Minimum detection size: {min_size}")
    
    def detect(self, frame: np.ndarray, 
               verbose: bool = False) -> List[Detection]:
        """
        Detect persons in the given frame.
        
        Args:
            frame: Input image as numpy array (BGR format)
            verbose: If True, print YOLO inference details
        
        Returns:
            List of Detection objects for each detected person
        """
        # Run YOLOv8 inference
        # classes=[PERSON_CLASS_ID] filters to only detect persons
        results = self.model(
            frame,
            classes=[PERSON_CLASS_ID],
            conf=self.confidence_threshold,
            verbose=verbose
        )
        
        detections = []
        
        # Process results (there's only one result for single image)
        for result in results:
            boxes = result.boxes
            
            if boxes is None or len(boxes) == 0:
                continue
            
            # Extract bounding boxes and confidences
            for i in range(len(boxes)):
                # Get bounding box coordinates
                xyxy = boxes.xyxy[i].cpu().numpy()
                x1, y1, x2, y2 = map(int, xyxy)
                
                # Get confidence score
                conf = float(boxes.conf[i].cpu().numpy())
                
                # Filter by minimum size (noise reduction)
                width = x2 - x1
                height = y2 - y1
                
                if width < self.min_width or height < self.min_height:
                    continue  # Skip small detections (noise)
                
                detections.append(Detection(
                    bbox=(x1, y1, x2, y2),
                    confidence=conf
                ))
        
        return detections
    
    def detect_batch(self, frames: List[np.ndarray]) -> List[List[Detection]]:
        """
        Detect persons in multiple frames (batch processing).
        
        Args:
            frames: List of input images
        
        Returns:
            List of detection lists, one per frame
        """
        all_detections = []
        
        # Process each frame (could be optimized with true batch inference)
        for frame in frames:
            detections = self.detect(frame)
            all_detections.append(detections)
        
        return all_detections
    
    def get_detections_array(self, detections: List[Detection]) -> np.ndarray:
        """
        Convert list of detections to numpy array for tracking.
        
        Args:
            detections: List of Detection objects
        
        Returns:
            Array of shape (N, 5) with columns [x1, y1, x2, y2, confidence]
            Returns empty array with shape (0, 5) if no detections
        """
        if not detections:
            return np.empty((0, 5))
        
        result = np.zeros((len(detections), 5))
        for i, det in enumerate(detections):
            result[i, :4] = det.bbox
            result[i, 4] = det.confidence
        
        return result
