"""
Configuration constants for EagleEye People Counting System.

This module contains all configurable parameters used throughout the application.
Settings can be overridden via environment variables (see .env.example).
"""

import os
from pathlib import Path

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    # Load from project root
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # python-dotenv not installed, use environment variables directly


def _get_env_int(key: str, default: int) -> int:
    """Get integer from environment variable with default."""
    value = os.environ.get(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _get_env_float(key: str, default: float) -> float:
    """Get float from environment variable with default."""
    value = os.environ.get(key)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _get_env_bool(key: str, default: bool) -> bool:
    """Get boolean from environment variable with default."""
    value = os.environ.get(key)
    if value is None:
        return default
    return value.lower() in ("true", "1", "yes", "on")


# =============================================================================
# LOGGING SETTINGS
# =============================================================================

# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = os.environ.get("EAGLEEYE_LOG_LEVEL", "INFO")

# Enable file logging
LOG_TO_FILE = _get_env_bool("EAGLEEYE_LOG_TO_FILE", True)


# =============================================================================
# DETECTION SETTINGS
# =============================================================================

# YOLOv8 model to use (nano model for speed)
# Options: 'yolov8n.pt', 'yolov8s.pt', 'yolov8m.pt', 'yolov8l.pt', 'yolov8x.pt'
YOLO_MODEL = os.environ.get("EAGLEEYE_YOLO_MODEL", "yolov8n.pt")

# Minimum confidence threshold for person detection (0.0 - 1.0)
# Lower values detect more people but may include false positives
CONFIDENCE_THRESHOLD = _get_env_float("EAGLEEYE_CONFIDENCE", 0.3)

# Minimum bounding box size in pixels (width, height)
# Detections smaller than this are considered noise and ignored
_min_size = _get_env_int("EAGLEEYE_MIN_SIZE", 10)
MIN_DETECTION_SIZE = (_min_size, _min_size)

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
DEFAULT_LINE_POSITION = _get_env_float("EAGLEEYE_LINE_POSITION", 0.5)

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
FRAME_SKIP = _get_env_int("EAGLEEYE_FRAME_SKIP", 3)

# Target frame width for processing (smaller = faster)
# Set to None to process at original resolution
_proc_width = os.environ.get("EAGLEEYE_PROCESSING_WIDTH")
PROCESSING_WIDTH = int(_proc_width) if _proc_width else 960

# Display resize (None = same as processing, or set smaller for faster display)
DISPLAY_WIDTH = 1280


# =============================================================================
# DATABASE SETTINGS
# =============================================================================

# SQLite database file path (relative to project root)
DATABASE_PATH = os.environ.get("EAGLEEYE_DATABASE_PATH", "eagle_eye.db")


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


# =============================================================================
# VERSION INFO
# =============================================================================

VERSION = "1.1.0"
