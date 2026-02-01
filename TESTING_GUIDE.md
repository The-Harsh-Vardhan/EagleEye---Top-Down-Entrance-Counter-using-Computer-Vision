# EagleEye Testing Guide

## ✅ System Tests Passed

All core components have been successfully tested and verified:

- ✅ **Dependencies**: All required packages installed (OpenCV 4.13.0, Ultralytics 8.4.9, Supervision 0.27.0, NumPy 2.3.4)
- ✅ **YOLOv8 Model**: yolov8n.pt loaded successfully
- ✅ **Detector**: Person detection initialized with 0.5 confidence threshold
- ✅ **Tracker**: ByteTrack initialized with proper parameters
- ✅ **Line Counter**: Crossing detection configured at frame center (50%)
- ✅ **Database**: SQLite database operational (eagle_eye.db)
- ✅ **Visualizer**: Frame rendering working correctly
- ✅ **Webcam**: Camera detected and accessible

## 🧪 Quick System Test

Run the automated test script:

```bash
python test_system.py
```

This will verify all modules without requiring video input.

## 🎥 Live Testing Options

### Option 1: Webcam Test (Recommended for first test)

```bash
python main.py --source 0
```

**What it does:**
- Uses your default webcam
- Displays live feed with bounding boxes
- Shows counting line in the center
- Tracks people crossing the line

**Controls:**
- Press **'q'** to quit
- Press **'r'** to reset counts

### Option 2: Test with Video File

```bash
python main.py --source path/to/video.mp4
```

**Example:**
```bash
python main.py --source test_video.mp4
```

### Option 3: Test with RTSP/MJPEG Stream

```bash
python main.py --source http://192.168.1.100:81/stream
```

## ⚙️ Advanced Testing

### Test with Custom Line Position

Position the counting line at 60% from top:
```bash
python main.py --source 0 --line-position 0.6
```

### Test with Different Confidence

Increase detection confidence to reduce false positives:
```bash
python main.py --source 0 --confidence 0.7
```

### Test Headless Mode (No Display)

Useful for server deployment:
```bash
python main.py --source 0 --no-display
```

### Test with Scheduled Recording

Only record during meal times (see [scheduler.py](src/scheduler.py)):
```bash
python main.py --source 0 --schedule
```

## 🎯 What to Look For

### Successful Detection
- ✅ Green bounding boxes around people
- ✅ Track IDs displayed on each person
- ✅ Red horizontal line at center of frame
- ✅ Count increases when crossing line
- ✅ Direction detected correctly (IN/OUT)

### Expected Behavior
1. **Person enters frame**: Gets assigned a track ID (e.g., #1)
2. **Person crosses line upward**: IN count increases
3. **Person crosses line downward**: OUT count increases
4. **Person leaves frame**: Track ID removed
5. **Person returns**: Gets new track ID

### Performance Metrics
- **Laptop (CPU only)**: 15-30 FPS expected
- **With GPU**: 60-100 FPS expected
- **Frame processing**: < 50ms per frame

## 🔍 Testing Tips

### For Top-Down Camera Setup
1. Mount camera directly above entrance
2. Ensure clear view with minimal occlusion
3. Position line at the entrance threshold
4. Test crossing from both directions
5. Verify people are fully visible

### Testing Direction Detection
The system uses this convention:
- **↑ Bottom → Top**: Counted as **IN**
- **↓ Top → Bottom**: Counted as **OUT**

### Optimal Testing Conditions
- ✅ Good lighting (avoid shadows)
- ✅ Clear background (reduce clutter)
- ✅ Stable camera mount (no vibration)
- ✅ Proper height (2-4 meters recommended)
- ✅ People fully in frame when crossing

## 📊 Check Database

View recorded crossings:

```bash
sqlite3 eagle_eye.db "SELECT * FROM crossings ORDER BY timestamp DESC LIMIT 10;"
```

Or use Python:
```python
from src.database import Database
db = Database('eagle_eye.db')
events = db.get_events(limit=10)
for event in events:
    print(f"{event[0]}: Track {event[1]} - {event[2]} at {event[3]}")
```

## 🐛 Troubleshooting

### Webcam Not Detected
```bash
# Try different camera indices
python main.py --source 1
python main.py --source 2
```

### Low FPS
- Reduce processing resolution in [config.py](src/config.py)
- Increase `FRAME_SKIP` value
- Use smaller YOLO model (already using yolov8n - smallest)

### No Detections
- Lower confidence threshold: `--confidence 0.3`
- Check lighting conditions
- Verify camera angle (should be top-down)

### False Positives
- Increase confidence: `--confidence 0.7`
- Adjust `MIN_DETECTION_SIZE` in config.py

### Counts Not Registering
- Verify line position: `--line-position 0.5`
- Check `MIN_CROSSING_DISTANCE` in config.py
- Ensure people cross the line completely

## 📈 Next Steps After Testing

1. ✅ **Calibrate line position** for your specific setup
2. ✅ **Tune confidence threshold** based on detection accuracy
3. ✅ **Test with real deployment scenario** (actual entrance)
4. ✅ **Monitor database** for crossing events
5. ✅ **Analyze performance** metrics (FPS, accuracy)
6. ✅ **Deploy to production** camera setup

## 🚀 Performance Optimization

If you need better performance:

1. **Enable GPU acceleration**:
   - Install CUDA toolkit
   - Install PyTorch with CUDA support
   - YOLOv8 will automatically use GPU

2. **Adjust config settings**:
   ```python
   # In src/config.py
   FRAME_SKIP = 3           # Process every 3rd frame
   PROCESSING_WIDTH = 640   # Reduce resolution
   CONFIDENCE_THRESHOLD = 0.6  # Higher = faster
   ```

3. **Use larger model for better accuracy** (slower):
   ```python
   YOLO_MODEL = 'yolov8s.pt'  # Small model
   YOLO_MODEL = 'yolov8m.pt'  # Medium model
   ```

## 📝 Test Results Template

Document your test results:

```
Test Date: ___________
Camera Setup: ___________
Lighting: ___________
Line Position: ___________
Confidence: ___________

Results:
- FPS: ___________
- Detection Accuracy: ___________
- Direction Accuracy: ___________
- False Positives: ___________
- Missed Detections: ___________

Notes:
___________
```

---

**System Status**: ✅ All tests passed - Ready for deployment!

For deployment instructions, see [DEPLOY.md](DEPLOY.md)
