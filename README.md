<div align="center">

# 🦅 EagleEye

### Top-Down Vision-Based People Counting System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00FFFF.svg)](https://github.com/ultralytics/ultralytics)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-green.svg)](https://opencv.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*Real-time people counting and occupancy tracking for overhead/top-down camera views*

[Docs site](https://the-harsh-vardhan.github.io/EagleEye---Top-Down-Entrance-Counter-using-Computer-Vision/) • [Quickstart](#quickstart) • [Architecture](#architecture) • [Reference](docs/reference.md) • [Report a bug](https://github.com/The-Harsh-Vardhan/EagleEye---Top-Down-Entrance-Counter-using-Computer-Vision/issues)

</div>

---

**EagleEye** counts people entering and leaving a space from a single overhead camera and keeps a live occupancy figure. Originally built for institutional environments such as college mess halls, it needs no card, tag or interaction: a detector finds people, a tracker keeps their IDs, and a directional line-crossing counter turns movement into IN/OUT events stored in SQLite.

## What it does

- **Detects people** with YOLOv8, or with background-subtraction **motion detection** (`--motion`), which is the mode intended for top-down views.
- **Tracks them** with ByteTrack (YOLO mode) or a centroid tracker (motion mode) so each person keeps one ID.
- **Counts direction**: a person crossing the line bottom to top is IN, top to bottom is OUT; occupancy = IN - OUT.
- **Logs every event** to SQLite (`eagle_eye.db`) with timestamp and occupancy, and shows live boxes, IDs and stats on screen or saves an annotated video.
- **Takes any source**: video file, MJPEG stream (ESP32-CAM), RTSP/IP camera or webcam. Ships with a Streamlit dashboard and a Docker setup.
- **Privacy-first**: no face recognition, no identity tracking, no biometric data; frames are processed live, not stored (unless you pass `--output`).

Use cases: dining halls, retail entrances, libraries and study spaces, event venues, occupancy-based building control.

## Architecture

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

| Module | File | Responsibility |
|--------|------|----------------|
| Video capture | `src/capture.py` | Unified input for files, streams and webcams |
| Person detection | `src/detector.py` | YOLOv8 detection with confidence and size filters |
| Motion detection | `src/motion_detector.py` | Background-subtraction alternative to YOLO |
| Tracking | `src/tracker.py`, `src/centroid_tracker.py` | ByteTrack wrapper; centroid tracker for motion mode |
| Line crossing | `src/line_counter.py`, `src/improved_line_counter.py` | Direction-aware counting and duplicate prevention |
| Database | `src/database.py` | SQLite event logging and queries |
| Visualization | `src/visualizer.py` | Boxes, IDs and stats overlay |
| Config, logging, health | `src/config.py`, `src/logging_config.py`, `src/health.py` | Central constants, logging, health checks |
| Scheduling | `src/scheduler.py` | Optional meal-time scheduling (`--scheduled`) |

## Quickstart

```bash
git clone https://github.com/The-Harsh-Vardhan/EagleEye---Top-Down-Entrance-Counter-using-Computer-Vision.git
cd EagleEye---Top-Down-Entrance-Counter-using-Computer-Vision

python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux/macOS

pip install -r requirements.txt
python main.py --source 0       # webcam; yolov8n.pt (~6 MB) downloads on first run
```

```bash
python main.py --source path/to/video.mp4                      # video file
python main.py --source http://192.168.1.100:81/stream         # MJPEG (ESP32-CAM, IP camera)
python main.py --source rtsp://user:pass@192.168.1.100:554/stream
python main.py --source 0 --motion                             # motion mode for top-down views
python main.py --source stream.mp4 --output result.mp4 --no-display   # headless, save video
```

Dashboard: `streamlit run dashboard.py`, or with Docker `docker-compose up -d dashboard` (see [docs/DOCKER.md](docs/DOCKER.md)). Platform-specific setup: [Installation Guide](docs/INSTALLATION.md).

### Command-line options

| Argument | Short | Default | Description |
|----------|-------|---------|-------------|
| `--source` | `-s` | **required** | Video file, URL or webcam index |
| `--motion` | | off | Use motion detection instead of YOLO (recommended for top-down views) |
| `--rotate` | | `0` | Rotate video (0, 90, 180, 270) |
| `--line-position` | `-l` | `0.5` | Counting line position (0.0 top, 1.0 bottom) |
| `--confidence` | `-c` | `0.5` | Detection confidence threshold |
| `--min-size` | | `30` | Minimum detection size in pixels |
| `--no-display` | | off | Run headless |
| `--output` | `-o` | none | Save annotated video |
| `--reset-db` | | off | Clear the database before starting |
| `--scheduled` | | off | Run only during the configured meal times |

Keys: `q` or `ESC` quit, `r` reset IN/OUT counts (history is kept).

## Counting logic

```
   FRAME TOP
        ↑ IN   (centroid moves bottom → top)
   ═══════════════  counting line (default 50% height)
        ↓ OUT  (centroid moves top → bottom)
   FRAME BOTTOM
```

1. Each track remembers its previous Y position.
2. When the centroid crosses the line (by at least `MIN_CROSSING_DISTANCE`, default 10 px), it is counted IN or OUT by direction.
3. Each track ID is counted once per crossing, and `occupancy = IN - OUT`.

## Status and known limitations

- The repo has a pytest suite (`tests/`, covering the database and line counter) and a Docker setup.
- `TEST_RESULTS.md` records that YOLOv8 (n and s, confidence 0.15 to 0.5) produced **0 person detections** on the top-down cafeteria test clip, where people are seated and heavily occluded. EagleEye works best on people **walking through** doorways, corridors or gates with a clear overhead view; `--motion` exists for such views.
- The dashboard has an opt-in Demo Mode that shows generated sample numbers, not real measurements.
- FPS figures in the docs are indicative, not from a logged benchmark ([details](docs/reference.md#expected-performance)).

## Project structure

```
├── main.py                  # CLI entry point and orchestration
├── dashboard.py             # Streamlit dashboard
├── src/                     # capture, detector, motion_detector, tracker, centroid_tracker,
│                            # line_counter, improved_line_counter, database, visualizer,
│                            # scheduler, time_series, health, config, logging_config
├── tests/                   # test_database.py, test_line_counter.py
├── Dataset/                 # standalone detection / motion scripts
├── docs/                    # installation, API, examples, Docker, reference, Pages site
├── Dockerfile, docker-compose.yml
├── requirements*.txt, pytest.ini, run.bat
├── CHANGELOG.md, CONTRIBUTING.md, DEPLOY.md, TESTING_GUIDE.md, TEST_RESULTS.md
└── documentation.md         # academic project report
```

## Tech stack

Python 3.8+, Ultralytics YOLOv8, ByteTrack via Supervision, OpenCV, NumPy, SQLite, Streamlit, Plotly, pandas, pytest, Docker.

## Documentation

- [Installation Guide](docs/INSTALLATION.md) and [Examples](docs/EXAMPLES.md)
- [API Reference](docs/API_REFERENCE.md) and [Docker guide](docs/DOCKER.md)
- [Reference](docs/reference.md): database schema and SQL queries, configuration, performance tuning, troubleshooting
- [Insights and justification](docs/INSIGHTS_AND_JUSTIFICATION.md), [Academic documentation](documentation.md), [Contributing](CONTRIBUTING.md)
- Docs site: [the-harsh-vardhan.github.io/EagleEye---Top-Down-Entrance-Counter-using-Computer-Vision](https://the-harsh-vardhan.github.io/EagleEye---Top-Down-Entrance-Counter-using-Computer-Vision/)

## Roadmap

Already in the repo: Streamlit dashboard, Docker deployment, unit tests. Still open:

- [ ] Edge deployment (Raspberry Pi, Jetson Nano, Coral Dev Board)
- [ ] Multi-camera support across entrances
- [ ] REST API for IoT / building-management integration
- [ ] Alerts for overcrowding or anomalies
- [ ] Heatmap generation
- [ ] Menu correlation for the mess-hall use case
- [ ] Cloud integration (AWS, Azure, GCP) and a mobile app

Contributions are welcome: fork, branch, commit, open a PR, and see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT, see [LICENSE](LICENSE).

## Acknowledgments

[Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics), [ByteTrack](https://github.com/ifzhang/ByteTrack), [Supervision](https://github.com/roboflow/supervision), [OpenCV](https://opencv.org/).
