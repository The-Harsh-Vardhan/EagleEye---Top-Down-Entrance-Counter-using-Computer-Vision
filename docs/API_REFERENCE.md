# EagleEye API Reference

Complete module and function documentation for EagleEye People Counting System.

## Table of Contents

- [Module Overview](#module-overview)
- [capture.py](#capturepy) - Video Input Handling
- [detector.py](#detectorpy) - Person Detection
- [tracker.py](#trackerpy) - Multi-Object Tracking
- [line_counter.py](#line_counterpy) - Line Crossing Detection
- [database.py](#databasepy) - Data Persistence
- [visualizer.py](#visualizerpy) - Rendering & Annotation
- [config.py](#configpy) - Configuration Constants
- [main.py](#mainpy) - Entry Point

---

## Module Overview

| Module | Purpose | Key Classes |
|--------|---------|-------------|
| `capture.py` | Video input abstraction | `VideoCapture` |
| `detector.py` | YOLOv8 person detection | `PersonDetector`, `Detection` |
| `tracker.py` | ByteTrack multi-object tracking | `PersonTracker`, `TrackedPerson` |
| `line_counter.py` | Direction-aware crossing detection | `LineCrossCounter`, `CrossingEvent` |
| `database.py` | SQLite event logging | `Database` |
| `visualizer.py` | Frame annotation | `Visualizer` |
| `config.py` | Configuration constants | N/A (constants only) |
| `scheduler.py` | Meal time scheduling | `is_meal_time()`, `get_meal_info()` |

---

## capture.py

Unified video input handling for files, streams, and webcams.

### Class: `VideoCapture`

Wrapper around OpenCV VideoCapture with enhanced error handling and stream support.

#### Constructor

```python
VideoCapture(source: Union[str, int], processing_width: Optional[int] = None)
```

**Parameters:**
- `source` (str | int): Video source
  - File path: `"video.mp4"`
  - MJPEG URL: `"http://192.168.1.100:81/stream"`
  - RTSP URL: `"rtsp://..."`
  - Webcam index: `0` (integer)
- `processing_width` (int, optional): Resize frames to this width. Maintains aspect ratio.

**Example:**
```python
# Video file
cap = VideoCapture("demo.mp4")

# ESP32-CAM stream
cap = VideoCapture("http://192.168.1.100:81/stream", processing_width=640)

# Webcam
cap = VideoCapture(0)
```

#### Methods

##### `read() -> Tuple[bool, Optional[np.ndarray]]`

Read the next frame from the video source.

**Returns:**
- `success` (bool): True if frame was read successfully
- `frame` (np.ndarray | None): Video frame as BGR numpy array, or None if failed

**Example:**
```python
success, frame = cap.read()
if success:
    # Process frame
    pass
```

##### `release() -> None`

Release the video capture resource.

**Example:**
```python
cap.release()
```

##### `get_fps() -> float`

Get the frame rate of the video source.

**Returns:**
- `fps` (float): Frames per second

##### `get_frame_count() -> int`

Get total number of frames (for video files only).

**Returns:**
- `count` (int): Total frames, or 0 for streams

---

## detector.py

YOLOv8-based person detection with configurable filtering.

### Class: `Detection`

Container for a single person detection.

#### Attributes

- `bbox` (Tuple[int, int, int, int]): Bounding box as `(x1, y1, x2, y2)` in pixels
- `confidence` (float): Detection confidence score (0.0 - 1.0)

#### Properties

##### `center -> Tuple[int, int]`

Calculate center point of the bounding box.

**Returns:**
- `(center_x, center_y)` (Tuple[int, int])

##### `width -> int`

Get bounding box width in pixels.

##### `height -> int`

Get bounding box height in pixels.

#### Methods

##### `to_xyxy() -> np.ndarray`

Convert bbox to numpy array `[x1, y1, x2, y2]`.

##### `to_xywh() -> Tuple[int, int, int, int]`

Convert to `(center_x, center_y, width, height)` format.

---

### Class: `PersonDetector`

YOLOv8 wrapper for person detection.

#### Constructor

```python
PersonDetector(
    model_path: str = "yolov8n.pt",
    confidence_threshold: float = 0.5,
    min_size: Tuple[int, int] = (30, 30)
)
```

**Parameters:**
- `model_path` (str): YOLOv8 model path or name (auto-downloads if not found)
  - Options: `yolov8n.pt`, `yolov8s.pt`, `yolov8m.pt`, `yolov8l.pt`, `yolov8x.pt`
- `confidence_threshold` (float): Minimum confidence to keep detection (0.0 - 1.0)
- `min_size` (Tuple[int, int]): Minimum `(width, height)` to filter noise

**Example:**
```python
detector = PersonDetector(
    model_path="yolov8n.pt",
    confidence_threshold=0.6,
    min_size=(40, 40)
)
```

#### Methods

##### `detect(frame: np.ndarray) -> List[Detection]`

Detect persons in a video frame.

**Parameters:**
- `frame` (np.ndarray): Input BGR frame

**Returns:**
- `detections` (List[Detection]): List of person detections

**Example:**
```python
detections = detector.detect(frame)
for det in detections:
    x1, y1, x2, y2 = det.bbox
    print(f"Person at ({det.center}) with confidence {det.confidence:.2f}")
```

---

## tracker.py

ByteTrack multi-object tracking for persistent IDs.

### Class: `TrackedPerson`

Container for a tracked person with persistent ID.

#### Attributes

- `track_id` (int): Unique persistent ID for this person
- `bbox` (Tuple[int, int, int, int]): Bounding box as `(x1, y1, x2, y2)`
- `confidence` (float): Detection confidence

#### Properties

##### `center -> Tuple[int, int]`

Center point of the bounding box.

##### `center_y -> int`

Y-coordinate of center (used for line crossing).

---

### Class: `PersonTracker`

ByteTrack-based person tracker.

#### Constructor

```python
PersonTracker(
    track_thresh: float = 0.25,
    track_buffer: int = 30,
    match_thresh: float = 0.8
)
```

**Parameters:**
- `track_thresh` (float): Detection confidence threshold for new tracks
- `track_buffer` (int): Number of frames to keep lost tracks alive
- `match_thresh` (float): IoU threshold for matching detections to tracks

**Example:**
```python
tracker = PersonTracker(
    track_thresh=0.25,
    track_buffer=30,
    match_thresh=0.8
)
```

#### Methods

##### `update(detections: List[Detection]) -> List[TrackedPerson]`

Update tracker with new detections.

**Parameters:**
- `detections` (List[Detection]): Detections from current frame

**Returns:**
- `tracked_persons` (List[TrackedPerson]): List with persistent track IDs

**Example:**
```python
detections = detector.detect(frame)
tracks = tracker.update(detections)

for track in tracks:
    print(f"Track ID: {track.track_id}, Position: {track.center}")
```

---

## line_counter.py

Direction-aware line crossing detection.

### Enum: `CrossingDirection`

Direction of line crossing.

**Values:**
- `CrossingDirection.IN`: Person crossed from bottom to top
- `CrossingDirection.OUT`: Person crossed from top to bottom

---

### Class: `CrossingEvent`

Represents a single line crossing event.

#### Attributes

- `track_id` (int): ID of the person who crossed
- `direction` (CrossingDirection): Direction of crossing
- `position` (Tuple[int, int]): `(x, y)` position where crossing occurred

---

### Class: `LineCrossCounter`

Counts persons crossing a horizontal line with direction awareness.

#### Constructor

```python
LineCrossCounter(
    frame_height: int,
    line_position: float = 0.5,
    min_crossing_distance: int = 10
)
```

**Parameters:**
- `frame_height` (int): Height of video frame in pixels
- `line_position` (float): Line position as ratio (0.0=top, 1.0=bottom)
- `min_crossing_distance` (int): Minimum Y movement to register crossing (prevents jitter)

**Example:**
```python
# Place line at 60% from top
counter = LineCrossCounter(
    frame_height=720,
    line_position=0.6,
    min_crossing_distance=15
)
```

#### Methods

##### `update(tracked_persons: List[TrackedPerson]) -> List[CrossingEvent]`

Update counter with current frame's tracks.

**Parameters:**
- `tracked_persons` (List[TrackedPerson]): Current frame tracks

**Returns:**
- `events` (List[CrossingEvent]): New crossing events in this frame

**Example:**
```python
events = counter.update(tracks)
for event in events:
    print(f"Track {event.track_id} crossed {event.direction.value}")
    if event.direction == CrossingDirection.IN:
        print("Person entered!")
```

##### `reset() -> None`

Reset IN and OUT counts to zero. Clears crossing history.

**Example:**
```python
counter.reset()
```

##### `get_occupancy() -> int`

Get current occupancy (IN count - OUT count).

**Returns:**
- `occupancy` (int): Current number of people inside

#### Properties

- `in_count` (int): Total IN crossings
- `out_count` (int): Total OUT crossings
- `line_y` (int): Y-coordinate of counting line in pixels

---

## database.py

SQLite database operations for event logging.

### Class: `Database`

SQLite database handler for crossing events.

#### Constructor

```python
Database(db_path: str = "eagle_eye.db")
```

**Parameters:**
- `db_path` (str): Path to SQLite database file

**Example:**
```python
db = Database("eagle_eye.db")
```

#### Methods

##### `log_event(direction: str, occupancy: int, timestamp: Optional[datetime] = None) -> int`

Log a crossing event to the database.

**Parameters:**
- `direction` (str): `"IN"` or `"OUT"`
- `occupancy` (int): Current occupancy after this event
- `timestamp` (datetime, optional): Event timestamp (defaults to now)

**Returns:**
- `event_id` (int): Database ID of inserted event

**Raises:**
- `ValueError`: If direction is not `"IN"` or `"OUT"`

**Example:**
```python
event_id = db.log_event("IN", occupancy=15)
print(f"Logged event ID: {event_id}")
```

##### `get_events(limit: int = 100, direction: Optional[str] = None) -> List[dict]`

Retrieve recent crossing events.

**Parameters:**
- `limit` (int): Maximum number of events to return
- `direction` (str, optional): Filter by `"IN"` or `"OUT"`, or None for all

**Returns:**
- `events` (List[dict]): List of event dictionaries with keys:
  - `id` (int)
  - `timestamp` (str)
  - `direction` (str)
  - `occupancy` (int)

**Example:**
```python
# Get last 50 IN events
in_events = db.get_events(limit=50, direction="IN")
for event in in_events:
    print(f"{event['timestamp']}: {event['direction']}")
```

##### `get_statistics(start_date: Optional[str] = None, end_date: Optional[str] = None) -> dict`

Get traffic statistics for a date range.

**Parameters:**
- `start_date` (str, optional): Start date as `"YYYY-MM-DD"`
- `end_date` (str, optional): End date as `"YYYY-MM-DD"`

**Returns:**
- `stats` (dict): Statistics dictionary with keys:
  - `total_in` (int)
  - `total_out` (int)
  - `peak_occupancy` (int)
  - `avg_occupancy` (float)

**Example:**
```python
stats = db.get_statistics(start_date="2026-02-01", end_date="2026-02-07")
print(f"Week traffic: IN={stats['total_in']}, OUT={stats['total_out']}")
```

##### `clear_events() -> None`

Delete all events from the database.

**Warning:** This is irreversible!

##### `close() -> None`

Close the database connection.

---

## visualizer.py

Frame rendering and annotation.

### Class: `Visualizer`

Handles all drawing operations on video frames.

#### Constructor

```python
Visualizer(frame_width: int, frame_height: int)
```

**Parameters:**
- `frame_width` (int): Width of video frames
- `frame_height` (int): Height of video frames

#### Methods

##### `draw_tracks(frame: np.ndarray, tracked_persons: List[TrackedPerson]) -> np.ndarray`

Draw bounding boxes and IDs for all tracked persons.

**Parameters:**
- `frame` (np.ndarray): Input frame
- `tracked_persons` (List[TrackedPerson]): Tracks to draw

**Returns:**
- `frame` (np.ndarray): Annotated frame

##### `draw_line(frame: np.ndarray, line_y: int) -> np.ndarray`

Draw the counting line.

**Parameters:**
- `frame` (np.ndarray): Input frame
- `line_y` (int): Y-coordinate of line

**Returns:**
- `frame` (np.ndarray): Frame with line

##### `draw_stats(frame: np.ndarray, in_count: int, out_count: int, occupancy: int, fps: float = 0.0) -> np.ndarray`

Draw statistics overlay.

**Parameters:**
- `frame` (np.ndarray): Input frame
- `in_count` (int): Total IN count
- `out_count` (int): Total OUT count
- `occupancy` (int): Current occupancy
- `fps` (float, optional): Current FPS

**Returns:**
- `frame` (np.ndarray): Frame with stats overlay

**Example:**
```python
vis = Visualizer(1280, 720)

# Draw everything
frame = vis.draw_tracks(frame, tracks)
frame = vis.draw_line(frame, line_y=360)
frame = vis.draw_stats(frame, in_count=10, out_count=5, occupancy=5, fps=25.0)
```

---

## config.py

Configuration constants for system tuning.

### Detection Settings

```python
YOLO_MODEL = 'yolov8n.pt'           # Model: n, s, m, l, x
CONFIDENCE_THRESHOLD = 0.5          # 0.0 - 1.0
MIN_DETECTION_SIZE = (30, 30)       # (width, height) pixels
PERSON_CLASS_ID = 0                 # COCO class for person
```

### Tracking Settings

```python
TRACK_THRESH = 0.25                 # New track confidence
TRACK_BUFFER = 30                   # Frames to keep lost tracks
MATCH_THRESH = 0.8                  # IoU matching threshold
```

### Line Crossing Settings

```python
DEFAULT_LINE_POSITION = 0.5         # 0.0 (top) - 1.0 (bottom)
MIN_CROSSING_DISTANCE = 10          # Pixels
```

### Database Settings

```python
DATABASE_PATH = 'eagle_eye.db'      # SQLite file path
```

### Display Settings

```python
COLOR_BOUNDING_BOX = (0, 255, 0)    # Green
COLOR_LINE = (0, 0, 255)            # Red
COLOR_TEXT = (255, 255, 255)        # White
FONT_SCALE = 0.6
BOX_THICKNESS = 2
LINE_THICKNESS = 2
```

---

## main.py

Entry point and orchestration.

### Function: `parse_arguments() -> argparse.Namespace`

Parse command-line arguments.

**Returns:**
- Namespace with: `source`, `line_position`, `confidence`, `min_size`, `no_display`, `output`, `reset_db`

### Function: `main() -> int`

Main application loop. Orchestrates capture → detect → track → count → visualize → log.

**Returns:**
- Exit code (0 = success)

---

## Usage Examples

### Complete Pipeline

```python
from src.capture import VideoCapture
from src.detector import PersonDetector
from src.tracker import PersonTracker
from src.line_counter import LineCrossCounter, CrossingDirection
from src.database import Database
from src.visualizer import Visualizer

# Initialize components
cap = VideoCapture("video.mp4")
detector = PersonDetector()
tracker = PersonTracker()
counter = LineCrossCounter(frame_height=720, line_position=0.5)
db = Database()
vis = Visualizer(1280, 720)

# Process frames
while True:
    success, frame = cap.read()
    if not success:
        break
    
    # Detection
    detections = detector.detect(frame)
    
    # Tracking
    tracks = tracker.update(detections)
    
    # Counting
    events = counter.update(tracks)
    for event in events:
        db.log_event(event.direction.value, counter.get_occupancy())
    
    # Visualization
    frame = vis.draw_tracks(frame, tracks)
    frame = vis.draw_line(frame, counter.line_y)
    frame = vis.draw_stats(frame, counter.in_count, counter.out_count, counter.get_occupancy())
    
    cv2.imshow("EagleEye", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

---

## Type Definitions

### Common Types

```python
from typing import Tuple, List, Optional
import numpy as np

# Bounding box
BBox = Tuple[int, int, int, int]  # (x1, y1, x2, y2)

# Point
Point = Tuple[int, int]  # (x, y)

# Frame
Frame = np.ndarray  # BGR image
```

---

For more information, see the [README](../README.md) or [CONTRIBUTING](../CONTRIBUTING.md) guide.

[⭐ Star on GitHub](https://github.com/The-Harsh-Vardhan/EagleEye)
