"""
Motion detection module for EagleEye People Counting System.

Uses background subtraction to detect moving objects in top-down views.
This approach is more reliable than YOLO for extreme overhead camera angles
where people appear as small dots rather than recognizable human shapes.
"""

import cv2
import numpy as np
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class Detection:
    """
    Container for a single motion detection.
    
    Attributes:
        bbox: Bounding box as (x1, y1, x2, y2) in pixels
        confidence: Detection confidence (based on contour area)
        center: Center point of the bounding box (x, y)
    """
    bbox: Tuple[int, int, int, int]
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


class MotionDetector:
    """
    Motion-based person detector using background subtraction.
    
    Ideal for top-down camera views where YOLO struggles to detect
    people due to the unusual viewing angle.
    """
    
    def __init__(self,
                 min_area: int = 200,
                 max_area: int = 50000,
                 history: int = 100,
                 var_threshold: int = 25,
                 detect_shadows: bool = True):
        """
        Initialize the motion detector.
        
        Args:
            min_area: Minimum contour area to consider as a person
            max_area: Maximum contour area (filter out large noise)
            history: Number of frames for background model
            var_threshold: Variance threshold for background subtraction
            detect_shadows: Whether to detect and remove shadows
        """
        self.min_area = min_area
        self.max_area = max_area
        
        # Background subtractor - MOG2 works well for varying lighting
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=history,
            varThreshold=var_threshold,
            detectShadows=detect_shadows
        )
        
        # Morphological kernel for cleaning up the mask
        self.kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, 
            (5, 5)
        )
        
        print(f"Motion detector initialized")
        print(f"Area range: {min_area} - {max_area} pixels")
    
    def detect(self, frame: np.ndarray, 
               threshold: int = 25) -> List[Detection]:
        """
        Detect moving objects in the given frame.
        
        Args:
            frame: Input image as numpy array (BGR format)
            threshold: Binary threshold for foreground mask
        
        Returns:
            List of Detection objects for each moving object
        """
        height, width = frame.shape[:2]
        
        # Edge margin - ignore detections near borders (walls, static noise)
        # Use 10% of frame dimensions to create a "safe zone"
        edge_margin_x = int(width * 0.10)   # 10% from left/right
        edge_margin_y = int(height * 0.08)  # 8% from top/bottom
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(frame, (5, 5), 0)
        
        # Apply background subtraction
        fg_mask = self.bg_subtractor.apply(blurred)
        
        # Remove shadows (shadows are marked as 127 in MOG2)
        fg_mask[fg_mask == 127] = 0
        
        # Apply threshold to get binary mask
        _, fg_mask = cv2.threshold(fg_mask, threshold, 255, cv2.THRESH_BINARY)
        
        # Morphological operations to clean up the mask
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, self.kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, self.kernel)
        fg_mask = cv2.dilate(fg_mask, self.kernel, iterations=2)
        
        # Store mask for visualization
        self.last_mask = fg_mask
        
        # Find contours (moving objects)
        contours, _ = cv2.findContours(
            fg_mask, 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        detections = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Filter by area
            if area < self.min_area or area > self.max_area:
                continue
            
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            cx, cy = x + w // 2, y + h // 2
            
            # Filter out detections near edges (walls, static objects)
            if cx < edge_margin_x or cx > width - edge_margin_x:
                continue
            if cy < edge_margin_y or cy > height - edge_margin_y:
                continue
            
            # Calculate confidence based on area (normalized)
            confidence = min(1.0, area / 5000)
            
            detections.append(Detection(
                bbox=(x, y, x + w, y + h),
                confidence=confidence
            ))
        
        return detections
    
    def get_mask(self) -> np.ndarray:
        """Get the last computed foreground mask for visualization."""
        return getattr(self, 'last_mask', None)
    
    def reset(self) -> None:
        """Reset the background model."""
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500,
            varThreshold=50,
            detectShadows=True
        )
        print("Motion detector reset")
