"""
Configuration constants for EagleEye People Counting System.

This module contains all configurable parameters used throughout the application.
Modify these values to tune the system for your specific use case.
"""

# =============================================================================
# DETECTION SETTINGS
# =============================================================================

# YOLOv8 model to use (nano model for real-time performance on laptops)
# Options: 'yolov8n.pt', 'yolov8s.pt', 'yolov8m.pt', 'yolov8l.pt', 'yolov8x.pt'
YOLO_MODEL = 'yolov8n.pt'

# Minimum confidence threshold for person detection (0.0 - 1.0)
# Lower values detect more people but may include false positives
CONFIDENCE_THRESHOLD = 0.5

# Minimum bounding box size in pixels (width, height)
# Detections smaller than this are considered noise and ignored
# Useful for filtering out distant/partial detections in top-down view
MIN_DETECTION_SIZE = (30, 30)

# YOLO class ID for person (COCO dataset)
PERSON_CLASS_ID = 0


# =============================================================================
# TRACKING SETTINGS
# =============================================================================

# ByteTrack parameters
TRACK_THRESH = 0.25          # Detection threshold for tracking
TRACK_BUFFER = 30            # Frames to keep lost tracks
MATCH_THRESH = 0.8           # IoU threshold for matching


# =============================================================================
# LINE CROSSING SETTINGS
# =============================================================================

# Default line position as ratio of frame height (0.0 = top, 1.0 = bottom)
# 0.5 means the line is at the vertical center of the frame
DEFAULT_LINE_POSITION = 0.5

# Minimum vertical movement (in pixels) required to register as a crossing
# Prevents false crossings from jittery detections
MIN_CROSSING_DISTANCE = 10


# =============================================================================
# VIDEO CAPTURE SETTINGS
# =============================================================================

# Maximum retry attempts for dropped frames before giving up
MAX_FRAME_RETRIES = 5

# Delay between retry attempts in seconds
FRAME_RETRY_DELAY = 0.1

# Frame skip for processing (1 = process every frame, 2 = every other frame, etc.)
# Increase this value if struggling with real-time performance
FRAME_SKIP = 2  # Process every 2nd frame for better performance

# Target frame width for processing (smaller = faster)
# Set to None to process at original resolution
PROCESSING_WIDTH = 960

# Display resize (None = same as processing, or set smaller for faster display)
DISPLAY_WIDTH = 960


# =============================================================================
# DATABASE SETTINGS
# =============================================================================

# SQLite database file path (relative to project root)
DATABASE_PATH = 'eagle_eye.db'


# =============================================================================
# VISUALIZATION SETTINGS
# =============================================================================

# Colors in BGR format (OpenCV uses BGR, not RGB)
COLOR_BOUNDING_BOX = (0, 255, 0)      # Green for tracked persons
COLOR_LINE = (0, 0, 255)               # Red for counting line
COLOR_TEXT = (255, 255, 255)           # White for text
COLOR_TEXT_BG = (0, 0, 0)              # Black background for text

# Font settings
FONT_SCALE = 0.6
FONT_THICKNESS = 2

# Bounding box line thickness
BOX_THICKNESS = 2

# Line thickness for counting line
LINE_THICKNESS = 3
