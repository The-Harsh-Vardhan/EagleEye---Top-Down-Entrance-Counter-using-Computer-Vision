"""
Line crossing detection module for EagleEye People Counting System.

Detects when tracked persons cross a horizontal counting line and
determines the direction of crossing (IN or OUT).

Convention:
- IN: Person crosses from bottom to top (moving upward)
- OUT: Person crosses from top to bottom (moving downward)
"""

from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum

from .config import DEFAULT_LINE_POSITION, MIN_CROSSING_DISTANCE
from .tracker import TrackedPerson


class CrossingDirection(Enum):
    """Direction of line crossing."""
    IN = "IN"
    OUT = "OUT"


@dataclass
class CrossingEvent:
    """
    Represents a single line crossing event.
    
    Attributes:
        track_id: ID of the person who crossed
        direction: Direction of crossing (IN or OUT)
        position: (x, y) position where crossing occurred
    """
    track_id: int
    direction: CrossingDirection
    position: Tuple[int, int]


class LineCrossCounter:
    """
    Counts persons crossing a horizontal line.
    
    Tracks the previous Y-position of each person and detects when
    they cross the counting line. Each person is counted only once
    per crossing to prevent double-counting.
    """
    
    def __init__(self, 
                 frame_height: int,
                 line_position: float = DEFAULT_LINE_POSITION,
                 min_crossing_distance: int = MIN_CROSSING_DISTANCE):
        """
        Initialize the line crossing counter.
        
        Args:
            frame_height: Height of the video frame in pixels
            line_position: Line position as ratio (0.0=top, 1.0=bottom)
            min_crossing_distance: Minimum Y movement to register crossing
        """
        self.frame_height = frame_height
        self.line_y = int(frame_height * line_position)
        self.min_crossing_distance = min_crossing_distance
        
        # Track previous Y positions for each track ID
        # Key: track_id, Value: previous center_y
        self._prev_positions: Dict[int, int] = {}
        
        # Set of track IDs that have already crossed (prevent double-counting)
        # Once a person crosses, they're added here and won't be counted again
        # until they leave the frame and return with a new ID
        self._crossed_ids: Set[int] = set()
        
        # Counts
        self.in_count = 0
        self.out_count = 0
        
        print(f"Line counter initialized at Y={self.line_y} (frame height: {frame_height})")
    
    @property
    def occupancy(self) -> int:
        """
        Get current occupancy (IN - OUT, minimum 0).
        
        Returns:
            Current number of people inside the monitored area
        """
        return max(0, self.in_count - self.out_count)
    
    def update(self, tracked_persons: List[TrackedPerson]) -> List[CrossingEvent]:
        """
        Update counter with new tracked positions.
        
        Checks each tracked person to see if they've crossed the line
        since their last known position.
        
        Args:
            tracked_persons: List of currently tracked persons
        
        Returns:
            List of CrossingEvent objects for each crossing detected
        """
        events = []
        current_ids = set()
        
        for person in tracked_persons:
            track_id = person.track_id
            current_y = person.center_y
            current_ids.add(track_id)
            
            # Check if we have a previous position for this person
            if track_id in self._prev_positions:
                prev_y = self._prev_positions[track_id]
                
                # Check for line crossing (only if not already counted)
                if track_id not in self._crossed_ids:
                    event = self._check_crossing(
                        track_id, prev_y, current_y, person.center
                    )
                    if event:
                        events.append(event)
                        self._crossed_ids.add(track_id)
                        
                        # Update counts
                        if event.direction == CrossingDirection.IN:
                            self.in_count += 1
                        else:
                            self.out_count += 1
            
            # Update position for next frame
            self._prev_positions[track_id] = current_y
        
        # Clean up old track IDs that are no longer visible
        # This allows re-counting if the same person re-enters
        old_ids = set(self._prev_positions.keys()) - current_ids
        for old_id in old_ids:
            del self._prev_positions[old_id]
            self._crossed_ids.discard(old_id)  # Allow re-counting on re-entry
        
        return events
    
    def _check_crossing(self, track_id: int, prev_y: int, current_y: int,
                        current_pos: Tuple[int, int]) -> Optional[CrossingEvent]:
        """
        Check if a crossing occurred between two Y positions.
        
        A crossing is detected when:
        1. The previous and current Y positions are on opposite sides of the line
        2. The movement distance exceeds the minimum threshold
        
        Args:
            track_id: ID of the tracked person
            prev_y: Previous Y position (center of bbox)
            current_y: Current Y position (center of bbox)
            current_pos: Current (x, y) position for event recording
        
        Returns:
            CrossingEvent if crossing detected, None otherwise
        """
        # Check if crossing threshold is met
        if abs(current_y - prev_y) < self.min_crossing_distance:
            return None
        
        # Check if line was crossed
        # prev_y > line_y and current_y <= line_y means crossed going UP (IN)
        # prev_y < line_y and current_y >= line_y means crossed going DOWN (OUT)
        
        if prev_y > self.line_y and current_y <= self.line_y:
            # Crossed from below to above (bottom to top) = IN
            return CrossingEvent(
                track_id=track_id,
                direction=CrossingDirection.IN,
                position=current_pos
            )
        elif prev_y < self.line_y and current_y >= self.line_y:
            # Crossed from above to below (top to bottom) = OUT
            return CrossingEvent(
                track_id=track_id,
                direction=CrossingDirection.OUT,
                position=current_pos
            )
        
        return None
    
    def reset_counts(self) -> None:
        """Reset IN/OUT counts to zero."""
        self.in_count = 0
        self.out_count = 0
        self._crossed_ids.clear()
        print("Counts reset to zero")
    
    def reset_all(self) -> None:
        """Reset everything including position tracking."""
        self.reset_counts()
        self._prev_positions.clear()
        print("Full reset complete")
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get current counting statistics.
        
        Returns:
            Dictionary with 'in', 'out', and 'occupancy' counts
        """
        return {
            'in': self.in_count,
            'out': self.out_count,
            'occupancy': self.occupancy,
            'line_y': self.line_y
        }
