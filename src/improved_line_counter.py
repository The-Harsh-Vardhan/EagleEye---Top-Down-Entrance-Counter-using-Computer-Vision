"""
Improved Line crossing detection module for EagleEye People Counting System.

This version tracks the INITIAL position when an object is first seen,
allowing detection of slow-moving objects that cross the line gradually.

Convention:
- IN: Person crosses from bottom to top (moving upward)
- OUT: Person crosses from top to bottom (moving downward)
"""

from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum

from .config import DEFAULT_LINE_POSITION


class CrossingDirection(Enum):
    """Direction of line crossing."""
    IN = "IN"
    OUT = "OUT"


@dataclass
class CrossingEvent:
    """Represents a single line crossing event."""
    track_id: int
    direction: CrossingDirection
    position: Tuple[int, int]


class ImprovedLineCrossCounter:
    """
    Improved line crossing counter that tracks initial positions.
    
    Instead of comparing consecutive frames (which fails for slow movement),
    this tracks where each object was FIRST seen and compares to current position.
    """
    
    def __init__(self, 
                 frame_height: int,
                 line_position: float = DEFAULT_LINE_POSITION):
        """
        Initialize the line crossing counter.
        
        Args:
            frame_height: Height of the video frame in pixels
            line_position: Line position as ratio (0.0=top, 1.0=bottom)
        """
        self.frame_height = frame_height
        self.line_y = int(frame_height * line_position)
        
        # Track INITIAL Y position when object first appeared
        self._initial_positions: Dict[int, int] = {}
        
        # Track which side of line object started on
        # True = started below line, False = started above line
        self._started_below: Dict[int, bool] = {}
        
        # Set of track IDs that have already crossed
        self._crossed_ids: Set[int] = set()
        
        # Counts
        self.in_count = 0
        self.out_count = 0
        
        print(f"Improved line counter initialized at Y={self.line_y}")
    
    @property
    def occupancy(self) -> int:
        """Get current occupancy (IN - OUT, minimum 0)."""
        return max(0, self.in_count - self.out_count)
    
    def update(self, tracked_persons: list) -> List[CrossingEvent]:
        """
        Update counter with new tracked positions.
        
        Args:
            tracked_persons: List of TrackedPerson objects
        
        Returns:
            List of CrossingEvent objects for each crossing detected
        """
        events = []
        current_ids = set()
        
        for person in tracked_persons:
            track_id = person.track_id
            current_y = person.center_y
            current_ids.add(track_id)
            
            # First time seeing this track
            if track_id not in self._initial_positions:
                self._initial_positions[track_id] = current_y
                self._started_below[track_id] = current_y > self.line_y
                continue
            
            # Skip if already crossed
            if track_id in self._crossed_ids:
                continue
            
            # Check for crossing based on initial position
            started_below = self._started_below[track_id]
            currently_below = current_y > self.line_y
            
            # Crossing detected when side of line changes
            if started_below != currently_below:
                if started_below and not currently_below:
                    # Started below, now above = moved UP = IN
                    direction = CrossingDirection.IN
                    self.in_count += 1
                else:
                    # Started above, now below = moved DOWN = OUT
                    direction = CrossingDirection.OUT
                    self.out_count += 1
                
                events.append(CrossingEvent(
                    track_id=track_id,
                    direction=direction,
                    position=person.center
                ))
                self._crossed_ids.add(track_id)
        
        # Clean up old track IDs
        old_ids = set(self._initial_positions.keys()) - current_ids
        for old_id in old_ids:
            del self._initial_positions[old_id]
            del self._started_below[old_id]
            self._crossed_ids.discard(old_id)
        
        return events
    
    def reset_counts(self) -> None:
        """Reset IN/OUT counts to zero."""
        self.in_count = 0
        self.out_count = 0
        self._crossed_ids.clear()
        print("Counts reset to zero")
    
    def reset_all(self) -> None:
        """Reset everything including position tracking."""
        self.reset_counts()
        self._initial_positions.clear()
        self._started_below.clear()
        print("Full reset complete")
    
    def get_stats(self) -> Dict[str, int]:
        """Get current counting statistics."""
        return {
            'in': self.in_count,
            'out': self.out_count,
            'occupancy': self.occupancy,
            'line_y': self.line_y
        }
