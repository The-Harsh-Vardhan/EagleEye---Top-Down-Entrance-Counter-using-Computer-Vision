"""
Visualization module for EagleEye People Counting System.

Draws bounding boxes, track IDs, counting line, and statistics
overlay on video frames.
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional

from .config import (
    COLOR_BOUNDING_BOX,
    COLOR_LINE,
    COLOR_TEXT,
    COLOR_TEXT_BG,
    FONT_SCALE,
    FONT_THICKNESS,
    BOX_THICKNESS,
    LINE_THICKNESS
)
from .tracker import TrackedPerson


class Visualizer:
    """
    Handles all drawing operations on video frames.
    
    Provides methods to draw bounding boxes, track IDs, the counting
    line, and statistics overlay. Optimized for real-time display.
    """
    
    def __init__(self, frame_width: int, frame_height: int):
        """
        Initialize the visualizer.
        
        Args:
            frame_width: Width of video frames
            frame_height: Height of video frames
        """
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.font = cv2.FONT_HERSHEY_SIMPLEX
    
    def draw_tracks(self, frame: np.ndarray,
                    tracked_persons: List[TrackedPerson]) -> np.ndarray:
        """
        Draw bounding boxes for all tracked persons.
        
        Args:
            frame: Input frame (will be modified in place)
            tracked_persons: List of tracked persons to draw
        
        Returns:
            Frame with drawings (same array as input)
        """
        for person in tracked_persons:
            x1, y1, x2, y2 = person.bbox
            
            # Draw bounding box
            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                COLOR_BOUNDING_BOX,
                BOX_THICKNESS
            )
            
            # Draw center point
            center = person.center
            cv2.circle(frame, center, 4, (0, 0, 255), -1)  # Red center dot
        
        return frame
    
    def draw_counting_line(self, frame: np.ndarray, 
                           line_y: int,
                           color: Tuple[int, int, int] = COLOR_LINE) -> np.ndarray:
        """
        Draw the horizontal counting line.
        
        Args:
            frame: Input frame (will be modified in place)
            line_y: Y-coordinate for the line
            color: Line color in BGR format
        
        Returns:
            Frame with line drawn
        """
        # Draw the main line
        cv2.line(
            frame,
            (0, line_y),
            (self.frame_width, line_y),
            color,
            LINE_THICKNESS
        )
        
        # Add small indicators at intervals
        indicator_spacing = 50
        for x in range(0, self.frame_width, indicator_spacing):
            cv2.line(
                frame,
                (x, line_y - 8),
                (x, line_y + 8),
                color,
                2
            )
        
        # Draw direction labels
        cv2.putText(
            frame,
            "IN",
            (10, line_y - 15),
            self.font,
            0.7,
            color,
            2
        )
        cv2.putText(
            frame,
            "OUT",
            (10, line_y + 30),
            self.font,
            0.7,
            color,
            2
        )
        
        return frame
    
    def draw_stats(self, frame: np.ndarray,
                   in_count: int,
                   out_count: int,
                   occupancy: int,
                   fps: float = 0.0) -> np.ndarray:
        """
        Draw statistics overlay on the frame.
        
        Args:
            frame: Input frame (will be modified in place)
            in_count: Total IN count
            out_count: Total OUT count
            occupancy: Current occupancy
            fps: Current frames per second
        
        Returns:
            Frame with stats overlay
        """
        # Stats panel background
        panel_height = 120
        panel_width = 200
        
        # Create semi-transparent overlay
        overlay = frame.copy()
        cv2.rectangle(
            overlay,
            (self.frame_width - panel_width - 10, 10),
            (self.frame_width - 10, panel_height),
            (50, 50, 50),
            -1
        )
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Draw stats text
        x_pos = self.frame_width - panel_width
        y_start = 35
        line_height = 25
        
        stats = [
            (f"IN: {in_count}", (0, 255, 0)),       # Green
            (f"OUT: {out_count}", (0, 0, 255)),     # Red
            (f"OCCUPANCY: {occupancy}", (255, 255, 0)),  # Cyan
            (f"FPS: {fps:.1f}", (255, 255, 255))    # White
        ]
        
        for i, (text, color) in enumerate(stats):
            cv2.putText(
                frame,
                text,
                (x_pos, y_start + i * line_height),
                self.font,
                0.6,
                color,
                2
            )
        
        return frame
    
    def draw_event_notification(self, frame: np.ndarray,
                                 event_text: str,
                                 color: Tuple[int, int, int]) -> np.ndarray:
        """
        Draw a temporary event notification (e.g., "Person crossed IN").
        
        Args:
            frame: Input frame
            event_text: Text to display
            color: Text color
        
        Returns:
            Frame with notification
        """
        # Get text size
        (text_width, text_height), _ = cv2.getTextSize(
            event_text, self.font, 1.0, 2
        )
        
        # Center the notification
        x = (self.frame_width - text_width) // 2
        y = 50
        
        # Draw background
        cv2.rectangle(
            frame,
            (x - 10, y - text_height - 10),
            (x + text_width + 10, y + 10),
            (0, 0, 0),
            -1
        )
        
        # Draw text
        cv2.putText(
            frame,
            event_text,
            (x, y),
            self.font,
            1.0,
            color,
            2
        )
        
        return frame
    
    def draw_all(self, frame: np.ndarray,
                 tracked_persons: List[TrackedPerson],
                 line_y: int,
                 in_count: int,
                 out_count: int,
                 occupancy: int,
                 fps: float = 0.0) -> np.ndarray:
        """
        Draw all visualizations on the frame.
        
        Convenience method that calls all drawing functions.
        
        Args:
            frame: Input frame
            tracked_persons: Tracked persons to draw
            line_y: Y-coordinate for counting line
            in_count: Total IN count
            out_count: Total OUT count
            occupancy: Current occupancy
            fps: Current FPS
        
        Returns:
            Fully annotated frame
        """
        frame = self.draw_counting_line(frame, line_y)
        frame = self.draw_tracks(frame, tracked_persons)
        frame = self.draw_stats(frame, in_count, out_count, occupancy, fps)
        return frame
