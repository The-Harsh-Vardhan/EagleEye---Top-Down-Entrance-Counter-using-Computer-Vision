<div align="center">

# 🦅 EagleEye

### Top-Down Vision-Based People Counting System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00FFFF.svg)](https://github.com/ultralytics/ultralytics)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-green.svg)](https://opencv.org/)

*Real-time people counting and occupancy tracking using computer vision for overhead/top-down camera views*

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Documentation](#-documentation) • [Architecture](#-architecture)

[⭐ Star on GitHub](https://github.com/The-Harsh-Vardhan/EagleEye-Top_Down_Entrance_Counter_Using_Computer_Vision) • [🐛 Report Bug](https://github.com/The-Harsh-Vardhan/EagleEye-Top_Down_Entrance_Counter_Using_Computer_Vision/issues) • [💡 Request Feature](https://github.com/The-Harsh-Vardhan/EagleEye-Top_Down_Entrance_Counter_Using_Computer_Vision/issues)

</div>

---

## 📋 Overview

**EagleEye** is an automated, non-intrusive people counting system designed for monitoring entrances and tracking occupancy in real-time. Originally developed for institutional environments like college mess halls, it uses computer vision to accurately count people entering and exiting a space without requiring any user interaction or identification.

The system employs a **top-down camera perspective** to minimize occlusion, combined with **YOLOv8 detection**, **ByteTrack multi-object tracking**, and **directional line-crossing detection** to provide accurate, privacy-preserving occupancy analytics.

### 🎯 Key Use Cases

- **Institutional Dining Halls**: Track student participation and correlate with food quality/menu
- **Retail Stores**: Monitor customer traffic and peak hours
- **Libraries & Study Spaces**: Track occupancy for capacity management
- **Event Venues**: Real-time attendance monitoring
- **Smart Buildings**: Occupancy-based HVAC and lighting control

---

## ⚡ Quick Start

Get up and running in 5 minutes:

```bash
# 1. Clone the repository
git clone https://github.com/The-Harsh-Vardhan/EagleEye-Top_Down_Entrance_Counter_Using_Computer_Vision.git
cd EagleEye-Top_Down_Entrance_Counter_Using_Computer_Vision

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run with webcam
python main.py --source 0
```

**That's it!** The YOLOv8 model will download automatically on first run.

💡 **Next steps**: See [Installation Guide](docs/INSTALLATION.md) for platform-specific details or [Examples](docs/EXAMPLES.md) for more usage scenarios.

## ✨ Features

### Core Capabilities

- 🎯 **YOLOv8 Person Detection** - State-of-the-art real-time object detection
- 🔄 **ByteTrack Multi-Object Tracking** - Persistent IDs across frames
- ↔️ **Direction-Aware Line Crossing** - Accurate IN/OUT classification
- 📹 **Multiple Input Sources** - Video files, MJPEG streams (ESP32-CAM), webcams
- 💾 **SQLite Database Logging** - All events stored with timestamps
- 📊 **Real-Time Visualization** - Bounding boxes, track IDs, and live statistics
- 🔒 **Privacy-First Design** - No facial recognition or identity tracking
- ⚡ **Optimized Performance** - Runs on CPU or GPU (CUDA supported)

### Anti-Features (What EagleEye Doesn't Do)

- ❌ **No Facial Recognition** - Preserves privacy and complies with regulations
- ❌ **No Identity Tracking** - Anonymous counting only
- ❌ **No Video Recording** - Processes frames in real-time, no storage
- ❌ **No Biometric Data** - Only motion and position information

---

## 🏗️ Architecture

EagleEye follows a modular pipeline architecture for maintainability and extensibility:

```
┌─────────────────────────────────────────────────────────────────┐
│                        VIDEO INPUT LAYER                         │
│  ┌──────────────┐  ┌───────────────┐  ┌───────────────────┐    │
│  │  Video File  │  │  MJPEG Stream │  │  Webcam (USB/IP)  │    │
│  └──────┬───────┘  └───────┬───────┘  └─────────┬─────────┘    │
│         └────────────┬─────┴──────────────────┬──┘              │
│                      │   capture.py           │                 │
└──────────────────────┼────────────────────────┼─────────────────┘
                       ▼                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DETECTION & TRACKING LAYER                    │
│                                                                  │
│  ┌──────────────────────┐         ┌─────────────────────────┐  │
│  │   YOLOv8 Detector    │────────▶│   ByteTrack Tracker     │  │
│  │   (detector.py)      │ Boxes   │   (tracker.py)          │  │
│  │                      │         │                         │  │
│  │ • Person detection   │         │ • Persistent track IDs  │  │
│  │ • Confidence filter  │         │ • Handle occlusions     │  │
│  │ • Size filter        │         │ • Track lifecycle mgmt  │  │
│  └──────────────────────┘         └────────┬────────────────┘  │
└─────────────────────────────────────────────┼──────────────────┘
                                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   COUNTING & ANALYTICS LAYER                     │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         Line Crossing Counter (line_counter.py)         │   │
│  │                                                          │   │
│  │  ╔═══════════════════════════════════╗                  │   │
│  │  ║         FRAME TOP (0,0)           ║                  │   │
│  │  ║                                   ║                  │   │
│  │  ║            ↑ IN Direction         ║                  │   │
│  │  ║                                   ║                  │   │
│  │  ║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║  ← Counting Line │   │
│  │  ║                                   ║                  │   │
│  │  ║           ↓ OUT Direction         ║                  │   │
│  │  ║                                   ║                  │   │
│  │  ║         FRAME BOTTOM              ║                  │   │
│  │  ╚═══════════════════════════════════╝                  │   │
│  │                                                          │   │
│  │  • Direction detection (bottom→top = IN)                │   │
│  │  • Duplicate prevention                                 │   │
│  │  • Occupancy calculation (IN - OUT)                     │   │
│  └─────────────┬────────────────────────────────────────────┘   │
└────────────────┼────────────────────────────────────────────────┘
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                  PERSISTENCE & OUTPUT LAYER                      │
│                                                                  │
│  ┌─────────────────────┐         ┌─────────────────────────┐   │
│  │  SQLite Database    │         │     Visualizer          │   │
│  │  (database.py)      │         │  (visualizer.py)        │   │
│  │                     │         │                         │   │
│  │ • Event logging     │         │ • Draw bounding boxes   │   │
│  │ • Timestamps        │         │ • Display track IDs     │   │
│  │ • Occupancy history │         │ • Overlay statistics    │   │
│  │ • Analytics queries │         │ • Real-time feedback    │   │
│  └─────────────────────┘         └────────┬────────────────┘   │
└─────────────────────────────────────────────┼──────────────────┘
                                              ▼
                                     ┌──────────────┐
                                     │ Display/File │
                                     └──────────────┘
```

### Module Overview

| Module | File | Responsibility |
|--------|------|----------------|
| **Video Capture** | `capture.py` | Unified interface for video files, streams, and webcams |
| **Person Detection** | `detector.py` | YOLOv8-based person detection with filtering |
| **Multi-Object Tracking** | `tracker.py` | ByteTrack wrapper for persistent ID assignment |
| **Line Crossing** | `line_counter.py` | Direction-aware crossing detection and counting |
| **Database** | `database.py` | SQLite operations for event logging |
| **Visualization** | `visualizer.py` | Rendering bounding boxes, stats, and annotations |
| **Configuration** | `config.py` | Centralized configuration constants |
| **Scheduler** | `scheduler.py` | Meal time scheduling (optional) |
| **Main** | `main.py` | CLI and orchestration |

---

## 🚀 Installation

### Prerequisites

- **Python**: 3.8 or higher (3.10+ recommended)
- **Operating System**: Windows, Linux, or macOS
- **Hardware**: 
  - **CPU**: Any modern processor (Intel i5/AMD Ryzen 5 or better)
  - **RAM**: 4GB minimum, 8GB+ recommended
  - **GPU**: Optional but recommended for real-time performance
    - NVIDIA GPU with CUDA support for 3-5x faster inference
    - See [CUDA Installation Guide](https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/)

### Quick Start

1. **Clone the repository**

   ```bash
   git clone https://github.com/The-Harsh-Vardhan/EagleEye-Top_Down_Entrance_Counter_Using_Computer_Vision.git
   cd EagleEye-Top_Down_Entrance_Counter_Using_Computer_Vision
   ```

2. **Create and activate virtual environment**

   **Windows:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

   **Linux/macOS:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Run the application**

   ```bash
   # Use webcam
   python main.py --source 0
   
   # Use video file
   python main.py --source demo.mp4
   
   # Use MJPEG stream (e.g., ESP32-CAM)
   python main.py --source http://192.168.1.100:81/stream
   ```

The YOLOv8 model (`yolov8n.pt`) will be downloaded automatically on first run (~6MB).

> 📚 **Detailed Setup**: For troubleshooting and advanced installation options, see [Installation Guide](docs/INSTALLATION.md)

---

## 📖 Usage

### Basic Commands

```bash
# Use webcam (index 0)
python main.py --source 0

# Use video file
python main.py --source path/to/video.mp4

# Use MJPEG stream (ESP32-CAM, IP camera)
python main.py --source http://192.168.1.100:81/stream

# Use RTSP stream
python main.py --source rtsp://username:password@192.168.1.100:554/stream
```

### Command-Line Options

| Argument | Short | Type | Default | Description |
|----------|-------|------|---------|-------------|
| `--source` | `-s` | str | **Required** | Video source (file path, URL, or webcam index) |
| `--line-position` | `-l` | float | `0.5` | Counting line position (0.0=top, 1.0=bottom) |
| `--confidence` | `-c` | float | `0.5` | Detection confidence threshold (0.0-1.0) |
| `--min-size` | | int | `30` | Minimum detection size in pixels |
| `--no-display` | | flag | `false` | Run headless without video window |
| `--output` | `-o` | str | `None` | Save annotated video to file |
| `--reset-db` | | flag | `false` | Clear database before starting |

### Usage Examples

```bash
# Place counting line at 60% from top (entrance threshold)
python main.py --source video.mp4 --line-position 0.6

# Higher confidence to reduce false positives
python main.py --source 0 --confidence 0.7

# Headless mode - save output without display (server deployment)
python main.py --source stream.mp4 --output result.mp4 --no-display

# Fresh start - reset all counts
python main.py --source 0 --reset-db

# Complete example - IP camera with custom settings
python main.py \
  --source http://192.168.1.100:81/stream \
  --line-position 0.55 \
  --confidence 0.6 \
  --min-size 40
```

### Keyboard Controls

| Key | Action |
|-----|--------|
| `q` | Quit the application |
| `r` | Reset IN/OUT counts (keeps history) |
| `ESC` | Quit the application |

---

## 🧮 Counting Logic

EagleEye uses **directional line crossing detection** to determine entry and exit events:

```
        ┌─────────────────────────────────────┐
        │           FRAME TOP                 │
        │                                     │
        │              ↑ IN                   │
        │      Person moving UPWARD           │
        │      (bottom → top)                 │
        │                                     │
        ├═════════════════════════════════════┤  ← COUNTING LINE
        │                                     │    (default: 50% height)
        │              ↓ OUT                  │
        │      Person moving DOWNWARD         │
        │      (top → bottom)                 │
        │                                     │
        │          FRAME BOTTOM               │
        └─────────────────────────────────────┘
```

### How It Works

1. **Track Position History**: System remembers previous Y-coordinate of each tracked person
2. **Line Crossing Detection**: When centroid crosses the line threshold:
   - **Bottom → Top** (Y decreasing): Counted as **IN**
   - **Top → Bottom** (Y increasing): Counted as **OUT**
3. **Duplicate Prevention**: Each track ID is counted only once per crossing
4. **Occupancy Calculation**: `Current Occupancy = IN Count - OUT Count`

### Configuration

Adjust counting behavior in [src/config.py](src/config.py):

```python
# Minimum vertical movement to register as crossing (prevents jitter)
MIN_CROSSING_DISTANCE = 10  # pixels

# Line position (0.0 = top, 0.5 = center, 1.0 = bottom)
DEFAULT_LINE_POSITION = 0.5
```

---

## 💾 Database

All crossing events are logged to `eagle_eye.db` (SQLite) for historical analysis.

### Schema

```sql
CREATE TABLE crossing_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,        -- ISO 8601 format (YYYY-MM-DD HH:MM:SS)
    direction TEXT NOT NULL,        -- 'IN' or 'OUT'
    occupancy INTEGER NOT NULL,     -- Current occupancy after event
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_timestamp ON crossing_events(timestamp);
CREATE INDEX idx_direction ON crossing_events(direction);
```

### Query Examples

**Open the database:**
```bash
sqlite3 eagle_eye.db
```

**View recent events:**
```sql
SELECT * FROM crossing_events 
ORDER BY timestamp DESC 
LIMIT 10;
```

**Today's traffic summary:**
```sql
SELECT 
    direction, 
    COUNT(*) as count,
    MIN(timestamp) as first_event,
    MAX(timestamp) as last_event
FROM crossing_events 
WHERE date(timestamp) = date('now')
GROUP BY direction;
```

**Hourly breakdown:**
```sql
SELECT 
    strftime('%Y-%m-%d', timestamp) as date,
    strftime('%H:00', timestamp) as hour,
    direction,
    COUNT(*) as count
FROM crossing_events
WHERE date(timestamp) >= date('now', '-7 days')
GROUP BY date, hour, direction
ORDER BY date, hour;
```

**Peak hours analysis:**
```sql
SELECT 
    strftime('%H:00', timestamp) as hour,
    SUM(CASE WHEN direction = 'IN' THEN 1 ELSE 0 END) as entries,
    SUM(CASE WHEN direction = 'OUT' THEN 1 ELSE 0 END) as exits
FROM crossing_events
WHERE date(timestamp) = date('now')
GROUP BY hour
ORDER BY entries DESC;
```

**Average daily occupancy:**
```sql
SELECT 
    date(timestamp) as date,
    AVG(occupancy) as avg_occupancy,
    MAX(occupancy) as peak_occupancy
FROM crossing_events
GROUP BY date
ORDER BY date DESC;
```

### Data Export

**Export to CSV:**
```bash
sqlite3 -header -csv eagle_eye.db "SELECT * FROM crossing_events;" > events.csv
```

**Export today's data:**
```bash
sqlite3 -header -csv eagle_eye.db \
  "SELECT * FROM crossing_events WHERE date(timestamp) = date('now');" \
  > today_events.csv
```

---

## 📁 Project Structure

```
EagleEye/
├── 📄 main.py                    # Entry point with CLI
├── 📄 requirements.txt           # Python dependencies
├── 📄 README.md                  # This file
├── 📄 CONTRIBUTING.md            # Contribution guidelines
├── 📄 CHANGELOG.md               # Version history
├── 📄 LICENSE                    # MIT License
├── 📄 .gitignore                 # Git ignore rules
├── 📄 documentation.md           # Academic project documentation
│
├── 💾 eagle_eye.db               # SQLite database (created on first run)
├── 🔧 yolov8n.pt                 # YOLOv8 model weights (auto-downloaded)
│
├── 📂 docs/                      # Documentation
│   ├── INSTALLATION.md           # Detailed setup guide
│   ├── API_REFERENCE.md          # Module documentation
│   └── EXAMPLES.md               # Usage examples and scenarios
│
├── 📂 src/                       # Source code modules
│   ├── __init__.py               # Package initialization
│   ├── config.py                 # Configuration constants
│   ├── capture.py                # Video input handling
│   ├── detector.py               # YOLOv8 person detection
│   ├── tracker.py                # ByteTrack tracking
│   ├── line_counter.py           # Line crossing detection
│   ├── database.py               # SQLite operations
│   ├── visualizer.py             # Rendering and annotation
│   ├── motion_detector.py        # Motion detection
│   └── scheduler.py              # Meal time scheduling
│
└── 📂 Extras/                    # Additional resources
    └── ...                       # Guides and references
```

---

## ⚙️ Configuration

EagleEye's behavior can be customized by editing [src/config.py](src/config.py):

### Detection Settings

```python
# YOLOv8 model selection (trade-off: speed vs accuracy)
YOLO_MODEL = 'yolov8n.pt'          # Options: n, s, m, l, x
                                    # n = fastest, x = most accurate

# Detection confidence threshold
CONFIDENCE_THRESHOLD = 0.5          # Range: 0.0 - 1.0
                                    # Higher = fewer false positives

# Minimum bounding box size (width, height) in pixels
MIN_DETECTION_SIZE = (30, 30)      # Filters out distant/partial detections
```

### Tracking Settings

```python
# ByteTrack parameters
TRACK_THRESH = 0.25                 # Detection threshold for tracking
TRACK_BUFFER = 30                   # Frames to keep lost tracks alive
MATCH_THRESH = 0.8                  # IoU threshold for matching
```

### Line Crossing Settings

```python
# Default counting line position
DEFAULT_LINE_POSITION = 0.5         # Range: 0.0 (top) - 1.0 (bottom)

# Minimum vertical movement to count as crossing
MIN_CROSSING_DISTANCE = 10          # Pixels - prevents jitter false positives
```

### Performance Settings

```python
# Video processing resolution
PROCESSING_WIDTH = None             # Set to 640 or 1280 to resize input
                                    # None = use original resolution

# Frame skip (process every N frames)
FRAME_SKIP = 1                      # Higher = faster but less accurate
```

---

## 🎯 Performance Tips

### Optimization Strategies

1. **Use GPU Acceleration**
   - Install CUDA toolkit for NVIDIA GPUs
   - 3-5x faster inference compared to CPU
   - See [CUDA Installation Guide](https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/)

2. **Choose the Right Model**
   ```python
   # Fast (15-30 FPS on laptop CPU)
   YOLO_MODEL = 'yolov8n.pt'
   
   # Balanced (10-20 FPS)
   YOLO_MODEL = 'yolov8s.pt'
   
   # Accurate (5-15 FPS, requires GPU)
   YOLO_MODEL = 'yolov8m.pt'
   ```

3. **Reduce Input Resolution**
   ```python
   # In config.py - resize input to 640px width
   PROCESSING_WIDTH = 640
   ```

4. **Skip Frames** (for pre-recorded videos)
   ```python
   # Process every 2nd frame
   FRAME_SKIP = 2
   ```

5. **Optimize Detection Thresholds**
   ```bash
   # Reduce false positives (less CPU load)
   python main.py --source 0 --confidence 0.6 --min-size 40
   ```

### Expected Performance

| Hardware | Model | Resolution | FPS |
|----------|-------|------------|-----|
| Laptop CPU (i5/i7) | yolov8n | 640x480 | 15-25 |
| Laptop CPU | yolov8s | 640x480 | 10-15 |
| Desktop CPU (Ryzen 5) | yolov8n | 1280x720 | 20-30 |
| NVIDIA GTX 1650 | yolov8n | 1280x720 | 60-80 |
| NVIDIA RTX 3060 | yolov8s | 1920x1080 | 80-100 |

---

## 🐛 Troubleshooting

| Issue | Possible Cause | Solution |
|-------|----------------|----------|
| **Low FPS / Lag** | Heavy model or CPU bottleneck | Use `yolov8n.pt`, enable GPU, reduce resolution |
| **False Detections** | Low confidence threshold | Increase `--confidence` to 0.6 or 0.7 |
| **Double Counting** | Tracking instability | Increase `MIN_CROSSING_DISTANCE` in config |
| **Missed Detections** | High confidence threshold | Lower `--confidence` to 0.4 or 0.45 |
| **Stream Lag/Buffering** | Network issues | Check camera stream, reduce buffer size |
| **No detections at all** | Wrong camera view | Ensure top-down perspective, check lighting |
| **Import errors** | Missing dependencies | Re-run `pip install -r requirements.txt` |
| **CUDA errors** | GPU driver mismatch | Update NVIDIA drivers, reinstall PyTorch |
| **Database locked** | Multiple instances | Close other EagleEye instances |

### Common Installation Issues

**Windows: `No module named 'cv2'`**
```bash
pip uninstall opencv-python opencv-python-headless
pip install opencv-python
```

**Linux: `libGL.so.1: cannot open shared object file`**
```bash
sudo apt-get install libgl1-mesa-glx
```

**macOS: Permission denied on webcam**
```bash
# Grant Terminal camera access in System Preferences > Security & Privacy
```

For more help, see [Installation Guide](docs/INSTALLATION.md) or [open an issue](https://github.com/The-Harsh-Vardhan/EagleEye-Top_Down_Entrance_Counter_Using_Computer_Vision/issues).

---

## 📚 Documentation

- **[Installation Guide](docs/INSTALLATION.md)** - Detailed setup instructions and troubleshooting
- **[API Reference](docs/API_REFERENCE.md)** - Complete module and function documentation
- **[Examples & Use Cases](docs/EXAMPLES.md)** - Real-world usage scenarios
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to the project
- **[Academic Documentation](documentation.md)** - Project report and research context

---

## 🤝 Contributing

Contributions are welcome! Whether it's bug fixes, new features, documentation improvements, or testing.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Areas for Contribution

- 🎨 Web dashboard for visualization
- 📱 Mobile app integration
- 🔌 Multi-camera support
- 🧠 Edge device deployment (Raspberry Pi, Jetson Nano)
- 📊 Advanced analytics and reporting
- 🌐 REST API for integration
- 🧪 Unit tests and CI/CD

---

## 🔮 Future Enhancements

- [ ] **Edge Deployment**: Port to Raspberry Pi, Jetson Nano, or Coral Dev Board
- [ ] **Multi-Camera Support**: Synchronized counting across multiple entrances
- [ ] **Web Dashboard**: Real-time visualization and historical analytics
- [ ] **REST API**: Integration with other systems (IoT, building management)
- [ ] **Alert System**: Notifications for overcrowding or anomalies
- [ ] **Heatmap Generation**: Spatial occupancy density visualization
- [ ] **Menu Correlation**: Link occupancy with meal schedules (college mess use case)
- [ ] **Cloud Integration**: Upload data to cloud platforms (AWS, Azure, GCP)
- [ ] **Mobile App**: iOS/Android app for monitoring
- [ ] **Docker Support**: Containerized deployment

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License - Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, subject to the conditions in the LICENSE file.
```

---

## 🙏 Acknowledgments

- **[Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)** - Object detection framework
- **[ByteTrack](https://github.com/ifzhang/ByteTrack)** - Multi-object tracking algorithm
- **[Supervision](https://github.com/roboflow/supervision)** - Computer vision utilities
- **[OpenCV](https://opencv.org/)** - Computer vision library

---

## 📧 Contact & Support

- **Issues & Bug Reports**: [GitHub Issues](https://github.com/The-Harsh-Vardhan/EagleEye-Top_Down_Entrance_Counter_Using_Computer_Vision/issues)
- **Questions & Discussions**: [GitHub Discussions](https://github.com/The-Harsh-Vardhan/EagleEye-Top_Down_Entrance_Counter_Using_Computer_Vision/discussions)
- **Documentation**: See [docs/](docs/) folder

---

## ⭐ Star History

If you find EagleEye useful, please consider giving it a [star on GitHub](https://github.com/The-Harsh-Vardhan/EagleEye-Top_Down_Entrance_Counter_Using_Computer_Vision)!

---

<div align="center">

**Made with ❤️ for institutional analytics and smart spaces**

[⬆ Back to Top](#-eagleeye)

</div>
