# Architecture

```mermaid
flowchart LR
    SRC["Video source<br/>file / MJPEG / RTSP / webcam"] -->|frames| CAP[capture.py]
    CAP --> DET{"--motion?"}
    DET -->|no| YOLO["PersonDetector<br/>YOLOv8"]
    DET -->|yes| MOT["MotionDetector<br/>background subtraction"]
    YOLO -->|boxes| TRK["PersonTracker<br/>ByteTrack"]
    MOT -->|blobs| CTR[CentroidTracker]
    TRK -->|track IDs| LC[Line crossing counter]
    CTR -->|track IDs| LC
    LC -->|IN / OUT events| DB[("SQLite<br/>eagle_eye.db")]
    LC -->|counts, occupancy| VIS["Visualizer<br/>window or output video"]
    DB -->|events| DASH[Streamlit dashboard]
```

GitHub renders this diagram in the repository README; here it is shown as source.

## Pipeline

1. **Capture** (`src/capture.py`) opens a file, MJPEG/RTSP stream or webcam.
2. **Detect**: `PersonDetector` (YOLOv8 with confidence and size filters), or `MotionDetector` when `--motion` is set.
3. **Track**: `PersonTracker` wraps ByteTrack from the supervision library; motion mode uses `CentroidTracker` for steadier IDs.
4. **Count**: `LineCrossCounter` (or `ImprovedLineCrossCounter` in motion mode) classifies a centroid crossing the line as IN (bottom to top) or OUT (top to bottom).
5. **Persist and show**: events go to SQLite via `src/database.py`; `Visualizer` draws boxes, IDs and stats; `dashboard.py` reads the database.
