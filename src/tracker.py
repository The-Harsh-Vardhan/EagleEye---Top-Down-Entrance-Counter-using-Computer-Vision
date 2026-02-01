"""
Person tracking module for EagleEye People Counting System.

Uses ByteTrack algorithm via the supervision library to maintain
persistent IDs for detected persons across frames.
"""

import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass

import supervision as sv

from .config import TRACK_THRESH, TRACK_BUFFER, MATCH_THRESH
from .detector import Detection


@dataclass
class TrackedPerson:
    """
    Container for a tracked person with persistent ID.
    
    Attributes:
        track_id: Unique persistent ID for this person
        bbox: Bounding box as (x1, y1, x2, y2)
        confidence: Detection confidence
        center: Center point of bounding box
    """
    track_id: int
    bbox: Tuple[int, int, int, int]
    confidence: float
    
    @property
    def center(self) -> Tuple[int, int]:
        """Calculate center point of the bounding box."""
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) // 2, (y1 + y2) // 2)
    
    @property
    def center_y(self) -> int:
        """Get Y coordinate of center (used for line crossing)."""
        return self.center[1]


class PersonTracker:
    """
    ByteTrack-based person tracker.
    
    Maintains persistent track IDs across frames, handling occlusions
    and temporary disappearances gracefully.
    """
    
    def __init__(self,
                 track_thresh: float = TRACK_THRESH,
                 track_buffer: int = TRACK_BUFFER,
                 match_thresh: float = MATCH_THRESH):
        """
        Initialize the ByteTrack tracker.
        
        Args:
            track_thresh: Detection confidence threshold for new tracks
            track_buffer: Number of frames to keep lost tracks
            match_thresh: IoU threshold for matching detections to tracks
        """
        # Initialize ByteTrack using supervision library
        self.tracker = sv.ByteTrack(
            track_activation_threshold=track_thresh,
            lost_track_buffer=track_buffer,
            minimum_matching_threshold=match_thresh,
            frame_rate=30  # Approximate, will be adjusted dynamically
        )
        
        print(f"Initialized ByteTrack tracker")
        print(f"Track threshold: {track_thresh}, Buffer: {track_buffer}")
    
    def update(self, detections: List[Detection]) -> List[TrackedPerson]:
        """
        Update tracker with new detections.
        
        Args:
            detections: List of Detection objects from the detector
        
        Returns:
            List of TrackedPerson objects with persistent IDs
        """
        if not detections:
            # Pass empty detections to tracker to maintain track states
            empty_dets = sv.Detections.empty()
            self.tracker.update_with_detections(empty_dets)
            return []
        
        # Convert detections to supervision format
        xyxy = np.array([d.bbox for d in detections])
        confidence = np.array([d.confidence for d in detections])
        
        # Create supervision Detections object
        sv_detections = sv.Detections(
            xyxy=xyxy,
            confidence=confidence
        )
        
        # Update tracker and get tracked detections
        tracked = self.tracker.update_with_detections(sv_detections)
        
        # Convert to TrackedPerson objects
        tracked_persons = []
        
        if tracked.tracker_id is not None:
            for i in range(len(tracked)):
                bbox = tuple(map(int, tracked.xyxy[i]))
                conf = tracked.confidence[i] if tracked.confidence is not None else 0.0
                track_id = int(tracked.tracker_id[i])
                
                tracked_persons.append(TrackedPerson(
                    track_id=track_id,
                    bbox=bbox,
                    confidence=conf
                ))
        
        return tracked_persons
    
    def reset(self) -> None:
        """Reset the tracker, clearing all tracks."""
        self.tracker.reset()
        print("Tracker reset - all tracks cleared")
