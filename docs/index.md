# EagleEye

Top-down, vision-based people counting. A single overhead camera feeds a detector (YOLOv8 or motion detection), a tracker (ByteTrack or centroid) and a directional line-crossing counter. Every IN/OUT event is stored in SQLite and can be viewed in a Streamlit dashboard.

- [Architecture](architecture.html)
- [Installation](INSTALLATION.html)
- [Examples](EXAMPLES.html)
- [API reference](API_REFERENCE.html)
- [Docker](DOCKER.html)
- [Reference](reference.html): database, configuration, performance tuning, troubleshooting
- [Insights and justification](INSIGHTS_AND_JUSTIFICATION.html)
- [Source on GitHub](https://github.com/The-Harsh-Vardhan/EagleEye---Top-Down-Entrance-Counter-using-Computer-Vision)

Known limitation: see the README section "Status and known limitations" (top-down seated scenes produced no YOLO detections in the recorded test).
