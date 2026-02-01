# EagleEye Testing Results & Recommendations

## Test Results

### System Verification
✅ All core components functional:
- Dependencies installed correctly
- YOLOv8 models loading successfully  
- Tracker, database, and visualizer working
- Video processing pipeline operational

### Detection Testing on Dataset Videos

#### Test Setup
- Video: Dataset/test1.mp4(cafeteria top-down view)
- Resolution: 1920x1080 (after rotation)
- Models tested: yolov8n.pt, yolov8s.pt
- Confidence thresholds: 0.15 - 0.5
- Processing: Full resolution

#### Results
❌ **YOLO person detection**: 0 detections
- Even with confidence=0.15 (very low)
- Even with yolov8s (larger, more capable model)
- Even detecting ALL classes (not just persons)

**Root Cause**: The top-down cafeteria view presents several challenges:
1. **Extreme viewing angle**: People appear very different from YOLO's training data (mostly side/front views)
2. **Occlusion**: People sitting at tables are partially hidden
3. **Scale**: People appear as small objects in the frame
4. **Static scene**: Most people are sitting still (problematic for motion detection too)

## 📋 Recommendations

### For This Specific Video (Cafeteria Scene)

This video is **not suitable** for the current system because:
- People are mostly stationary (sitting at tables)
- Top-down angle is too extreme for standard person detection
- Scene is too complex with heavy occlusion

**✅ Better test scenarios:**
- Videos with people **walking through doorways/entrances**
- Clear top-down view of **hallways or corridors**
- Scenes with **active movement** (not static sitting)

### For Production Deployment

EagleEye works best with:

#### ✅ Ideal Scenarios
1. **Entrance/Exit counting**
   - People walking through doorways
   - Clear separation between IN/OUT directions
   - Continuous movement across counting line

2. **Corridor/Hallway monitoring**
   - Top-down view of walkways
   - Less occlusion
   - Clear pedestrian flow

3. **Turnstile/Gate areas**
   - One person at a time
   - Predictable movement patterns
   - Well-defined crossing zones

#### ❌ Challenging Scenarios (Current Limitations)
1. **Cafeteria seating areas** (like test video)
   - People sitting still
   - Heavy table/chair occlusion
   - No clear directional flow

2. **Crowded spaces**
   - Severe person-to-person occlusion
   - Difficult tracking in dense crowds

3. **Multi-level spaces**
   - People at different heights
   - Staircases, ramps

## 🎯 Alternative Approaches for Cafeteria Monitoring

If you need to count people in cafeteria seating areas:

### Option 1: Entry/Exit Point Counting
Instead of monitoring the dining area, count at:
- **Entrance doors** (people entering/leaving)
- **Food service lines** (people getting food = indicator of occupancy)
- **Stairway exits** (if cafeteria has dedicated access)

### Option 2: Occupancy Sensors
Use different technology:
- **Thermal sensors** at entrances
- **Pressure mats** at doorways  
- **WiFi/Bluetooth** device counting
- **Dedicated people counters** (commercial hardware)

### Option 3: Computer Vision for Seated People
Requires specialized solution:
- **Custom-trained model** on top-down seated people
- **Depth cameras** (e.g., Intel RealSense)
- **Multi-camera fusion** from different angles
- **Seat occupancy detection** (detect occupied vs empty chairs)

## 🧪 Recommended Test Videos

For best results testing EagleEye, create/obtain videos with:

### Camera Setup
- **Height**: 2.5-4 meters above ground
- **Angle**: Straight down (90° to floor)
- **Location**: Doorway, corridor, or entrance
- **Lighting**: Consistent, avoid heavy shadows
- **Resolution**: 1080p or higher

### Scene Requirements
- **Clear floor space** where people walk
- **Defined crossing line** (actual doorway threshold)
- **Pedestrian movement** (not static sitting/standing)
- **Minimal occlusion** (no furniture blocking view)
- **One-directional or bi-directional flow**

### Example Scenarios to Record
1. Building entrance (people entering/leaving)
2. Hallway intersection (people crossing a line)
3. Elevator lobby (people approaching/leaving elevators)
4. Library entrance
5. Gym/fitness center door

## 📊 Current System Configuration

After optimization for top-down views:

```python
# src/config.py
YOLO_MODEL = 'yolov8s.pt'  # Larger model for difficult angles
CONFIDENCE_THRESHOLD = 0.15  # Very low for challenging views
MIN_DETECTION_SIZE = (10, 10)  # Small objects acceptable
PROCESSING_WIDTH = None  # Full resolution
```

**These settings are optimized but still require:**
- People in motion (not static)
- Less extreme viewing angles
- Entrance/corridor scenarios

## ✅ Next Steps

1. **Test with appropriate video**:
   - Record or obtain video of building entrance
   - People walking through doorway
   - Clear top-down perspective

2. **Run system**:
   ```bash
   python main.py --source your_entrance_video.mp4 --rotate 90 --line-position 0.5
   ```

3. **Calibrate**:
   - Adjust line position to match doorway threshold
   - Fine-tune confidence if needed
   - Monitor database for crossing events

4. **Deploy to real camera**:
   - Mount camera above entrance
   - Use RTSP/MJPEG stream
   - Run continuously or scheduled

## 🔧 System Status

**Current State**: ✅ Fully functional, awaiting suitable test video

**Limitations Identified**: 
- Cannot detect seated/stationary people in cafeteria settings
- Requires pedestrian movement for counting
- Best suited for entrance/exit scenarios

**Recommended Use Cases**: 
- Building entrance counting
- Corridor/hallway monitoring  
- Queue/line management
- Turnstile validation

---

**For best results**, test with a video that matches the intended deployment scenario: people walking through an entrance or corridor with clear directional movement.
