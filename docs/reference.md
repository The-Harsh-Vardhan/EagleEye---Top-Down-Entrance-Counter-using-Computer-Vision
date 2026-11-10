# Reference

Detailed reference moved out of the README: database schema and queries, configuration, performance tuning and troubleshooting.

## Database

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

## Configuration

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

## Performance tips

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

### Expected performance

> These figures come from the project docs (`docs/EXAMPLES.md`) and are indicative. They are not backed by a logged benchmark run in this repository (see issue #3).

| Hardware | Model | Resolution | FPS |
|----------|-------|------------|-----|
| Laptop CPU (i5/i7) | yolov8n | 640x480 | 15-25 |
| Laptop CPU | yolov8s | 640x480 | 10-15 |
| Desktop CPU (Ryzen 5) | yolov8n | 1280x720 | 20-30 |
| NVIDIA GTX 1650 | yolov8n | 1280x720 | 60-80 |
| NVIDIA RTX 3060 | yolov8s | 1920x1080 | 80-100 |

## Troubleshooting

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
