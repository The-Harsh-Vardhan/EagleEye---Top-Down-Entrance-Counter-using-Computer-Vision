# Changelog

All notable changes to the EagleEye project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned Features
- Web dashboard for real-time monitoring
- Multi-camera support with synchronized counting
- REST API for integration
- Edge deployment for Raspberry Pi / Jetson Nano
- Alert system for overcrowding
- Heatmap generation
- Docker containerization

## [1.0.0] - 2026-02-01

### Added
- Initial release of EagleEye People Counting System
- YOLOv8-based person detection with configurable confidence threshold
- ByteTrack multi-object tracking for persistent IDs
- Direction-aware line crossing detection (IN/OUT)
- SQLite database logging for all crossing events
- Real-time visualization with bounding boxes and statistics overlay
- Support for multiple input sources:
  - Video files (MP4, AVI, etc.)
  - MJPEG streams (ESP32-CAM, IP cameras)
  - RTSP streams
  - Webcams (USB and built-in)
- Command-line interface with comprehensive options
- Configurable counting line position
- Minimum detection size filtering
- Headless mode for server deployment
- Video output recording capability
- Database reset functionality
- Keyboard controls (q=quit, r=reset)
- Comprehensive documentation:
  - README with installation and usage guide
  - API reference documentation
  - Installation guide for all platforms
  - Contributing guidelines
  - Academic project documentation
- Privacy-first design (no facial recognition or identity tracking)
- Cross-platform support (Windows, Linux, macOS)
- GPU acceleration support (CUDA)

### Features

#### Detection & Tracking
- YOLOv8 model support (n, s, m, l, x variants)
- Configurable confidence threshold (0.0 - 1.0)
- Minimum bounding box size filtering
- ByteTrack algorithm for robust tracking
- Handles occlusions and temporary disappearances
- Track buffer for lost tracks

#### Counting Logic
- Horizontal line crossing detection
- Direction classification (bottom→top = IN, top→bottom = OUT)
- Duplicate prevention (one count per track per crossing)
- Configurable minimum crossing distance (anti-jitter)
- Real-time occupancy calculation (IN - OUT)

#### Database
- SQLite database for event persistence
- Timestamp recording for all events
- Occupancy tracking
- Indexed queries for performance
- Export capabilities (CSV)
- Statistical analysis queries

#### Visualization
- Bounding box rendering with track IDs
- Counting line overlay
- Statistics panel (IN, OUT, Occupancy, FPS)
- Color-coded display
- Configurable fonts and colors

### Documentation
- Comprehensive README with architecture diagrams
- API reference for all modules and classes
- Platform-specific installation guides
- Troubleshooting section
- Database query examples
- Contributing guidelines
- MIT License

### Performance
- 15-30 FPS on laptop CPU (with yolov8n)
- 60-100 FPS on modern GPU
- Optimized for real-time processing
- Minimal memory footprint

## [0.9.0] - 2026-01-20 (Beta)

### Added
- Beta release for testing
- Core detection and tracking functionality
- Basic counting logic
- Database logging
- Simple visualization

### Changed
- Improved tracking stability
- Enhanced line crossing detection accuracy
- Optimized database queries

### Fixed
- Double counting issues
- Track ID reuse bugs
- Database locking problems

## [0.5.0] - 2026-01-10 (Alpha)

### Added
- Initial proof-of-concept
- YOLOv8 integration
- Basic tracking
- Prototype counting logic

---

## Version History Summary

- **v1.0.0** (2026-02-01) - First stable release
- **v0.9.0** (2026-01-20) - Beta release
- **v0.5.0** (2026-01-10) - Alpha proof-of-concept

---

## How to Contribute

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on proposing changes and new features.

---

## Links

- [GitHub Repository](https://github.com/The-Harsh-Vardhan/EagleEye-Top_Down_Entrance_Counter_Using_Computer_Vision)
- [Issue Tracker](https://github.com/The-Harsh-Vardhan/EagleEye-Top_Down_Entrance_Counter_Using_Computer_Vision/issues)
- [Documentation](README.md)
