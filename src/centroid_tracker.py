"""
Simple centroid-based tracker for motion detection.
More tolerant of noisy detections than ByteTrack.
"""
import numpy as np
from typing import List, Tuple, Dict
from dataclasses import dataclass
from scipy.spatial import distance as dist
from collections import OrderedDict


@dataclass
class TrackedPerson:
    """Container for a tracked person with persistent ID."""
    track_id: int
    bbox: Tuple[int, int, int, int]
    confidence: float
    
    @property
    def center(self) -> Tuple[int, int]:
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) // 2, (y1 + y2) // 2)
    
    @property
    def center_y(self) -> int:
        return self.center[1]


class CentroidTracker:
    """
    Simple centroid-based tracker.
    
    Matches detections to existing tracks based on centroid distance.
    More stable for noisy motion detection than ByteTrack.
    """
    
    def __init__(self, max_disappeared: int = 15, max_distance: int = 80):
        """
        Args:
            max_disappeared: Frames to keep a lost track before removing
            max_distance: Maximum centroid distance for matching (pixels)
        """
        self.next_id = 0
        self.objects: OrderedDict[int, Tuple[int, int, Tuple[int,int,int,int], float]] = OrderedDict()
        self.disappeared: Dict[int, int] = {}
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance
        
        print(f"Initialized Centroid Tracker")
        print(f"Max disappeared: {max_disappeared}, Max distance: {max_distance}")
    
    def _register(self, centroid: Tuple[int, int], bbox: Tuple[int,int,int,int], conf: float):
        """Register a new object with the next available ID."""
        self.objects[self.next_id] = (centroid[0], centroid[1], bbox, conf)
        self.disappeared[self.next_id] = 0
        self.next_id += 1
    
    def _deregister(self, object_id: int):
        """Remove an object from tracking."""
        del self.objects[object_id]
        del self.disappeared[object_id]
    
    def update(self, detections: list) -> List[TrackedPerson]:
        """
        Update tracks with new detections.
        
        Args:
            detections: List of Detection objects with .bbox and .confidence
            
        Returns:
            List of TrackedPerson with persistent IDs
        """
        # Handle empty detections
        if not detections:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self._deregister(object_id)
            return self._get_tracked_persons()
        
        # Get centroids from detections
        input_centroids = []
        input_bboxes = []
        input_confs = []
        
        for det in detections:
            x1, y1, x2, y2 = det.bbox
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            input_centroids.append((cx, cy))
            input_bboxes.append(det.bbox)
            input_confs.append(det.confidence)
        
        input_centroids = np.array(input_centroids)
        
        # If no existing objects, register all new detections
        if len(self.objects) == 0:
            for i in range(len(input_centroids)):
                self._register(input_centroids[i], input_bboxes[i], input_confs[i])
        else:
            # Match existing objects to new detections
            object_ids = list(self.objects.keys())
            object_centroids = np.array([(self.objects[i][0], self.objects[i][1]) for i in object_ids])
            
            # Compute distance matrix
            D = dist.cdist(object_centroids, input_centroids)
            
            # Find minimum distance matches
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]
            
            used_rows = set()
            used_cols = set()
            
            for (row, col) in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue
                
                # Check if distance is within threshold
                if D[row, col] > self.max_distance:
                    continue
                
                # Update existing object
                object_id = object_ids[row]
                self.objects[object_id] = (
                    input_centroids[col][0], 
                    input_centroids[col][1],
                    input_bboxes[col],
                    input_confs[col]
                )
                self.disappeared[object_id] = 0
                
                used_rows.add(row)
                used_cols.add(col)
            
            # Handle unmatched existing objects (mark as disappeared)
            unused_rows = set(range(len(object_ids))) - used_rows
            for row in unused_rows:
                object_id = object_ids[row]
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self._deregister(object_id)
            
            # Register new detections that weren't matched
            unused_cols = set(range(len(input_centroids))) - used_cols
            for col in unused_cols:
                self._register(input_centroids[col], input_bboxes[col], input_confs[col])
        
        return self._get_tracked_persons()
    
    def _get_tracked_persons(self) -> List[TrackedPerson]:
        """Convert internal objects to TrackedPerson list."""
        return [
            TrackedPerson(
                track_id=obj_id,
                bbox=data[2],
                confidence=data[3]
            )
            for obj_id, data in self.objects.items()
        ]
    
    def reset(self):
        """Reset the tracker."""
        self.next_id = 0
        self.objects.clear()
        self.disappeared.clear()
        print("Centroid tracker reset")
