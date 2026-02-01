"""
Quick system test for EagleEye
Tests the complete pipeline without requiring video input
"""

import sys
from pathlib import Path

# Test imports
print("🧪 EagleEye System Test")
print("=" * 60)

print("\n1️⃣ Testing imports...")
try:
    from src.config import *
    from src.detector import PersonDetector
    from src.tracker import PersonTracker
    from src.line_counter import LineCrossCounter
    from src.database import Database
    from src.visualizer import Visualizer
    from src.capture import VideoCapture
    print("   ✅ All modules imported successfully")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

print("\n2️⃣ Testing detector initialization...")
try:
    detector = PersonDetector(model_path=YOLO_MODEL)
    print(f"   ✅ Detector initialized with model: {YOLO_MODEL}")
    print(f"   ✅ Confidence threshold: {CONFIDENCE_THRESHOLD}")
except Exception as e:
    print(f"   ❌ Detector initialization failed: {e}")
    sys.exit(1)

print("\n3️⃣ Testing tracker initialization...")
try:
    tracker = PersonTracker()
    print("   ✅ ByteTrack tracker initialized")
except Exception as e:
    print(f"   ❌ Tracker initialization failed: {e}")
    sys.exit(1)

print("\n4️⃣ Testing line counter initialization...")
try:
    # Use a test frame height for line position
    test_frame_height = 1080
    counter = LineCrossCounter(frame_height=test_frame_height)
    print(f"   ✅ Line counter initialized")
    print(f"   ✅ Line position: {counter.line_y}px (ratio: {DEFAULT_LINE_POSITION})")
except Exception as e:
    print(f"   ❌ Line counter initialization failed: {e}")
    sys.exit(1)

print("\n5️⃣ Testing database initialization...")
try:
    db = Database(DATABASE_PATH)
    in_count, out_count = db.get_total_counts()
    occupancy = db.get_current_occupancy()
    print(f"   ✅ Database initialized: {DATABASE_PATH}")
    print(f"   ✅ Total counts - IN: {in_count}, OUT: {out_count}, Occupancy: {occupancy}")
except Exception as e:
    print(f"   ❌ Database initialization failed: {e}")
    sys.exit(1)

print("\n6️⃣ Testing visualizer initialization...")
try:
    test_frame_width = 1920
    test_frame_height = 1080
    visualizer = Visualizer(frame_width=test_frame_width, frame_height=test_frame_height)
    print("   ✅ Visualizer initialized")
except Exception as e:
    print(f"   ❌ Visualizer initialization failed: {e}")
    sys.exit(1)

print("\n7️⃣ Checking available video sources...")
try:
    # Check if webcam is available
    import cv2
    cap = cv2.VideoCapture(0)
    has_webcam = cap.isOpened()
    cap.release()
    
    if has_webcam:
        print("   ✅ Webcam detected (index 0)")
        print("   💡 You can run: python main.py --source 0")
    else:
        print("   ℹ️  No webcam detected")
        print("   💡 You can run with video file: python main.py --source path/to/video.mp4")
except Exception as e:
    print(f"   ⚠️  Could not check webcam: {e}")

print("\n" + "=" * 60)
print("✅ All system tests passed successfully!")
print("\n📝 Next steps:")
print("   1. Run with webcam: python main.py --source 0")
print("   2. Run with video: python main.py --source video.mp4")
print("   3. Run with stream: python main.py --source rtsp://...")
print("\n   For more options: python main.py --help")
print("=" * 60)
