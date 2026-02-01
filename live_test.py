"""
Live test viewer - shows video with real-time detection and counting
"""
import cv2
import sys
from src.motion_detector import MotionDetector
from src.centroid_tracker import CentroidTracker
from src.improved_line_counter import ImprovedLineCrossCounter
from src.visualizer import Visualizer

video_path = sys.argv[1] if len(sys.argv) > 1 else "Dataset/test1.mp4"

print(f"Live test: {video_path}")
print("Press 'q' to quit, 'r' to reset counts")

cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"Error: Cannot open {video_path}")
    sys.exit(1)

fps = int(cap.get(cv2.CAP_PROP_FPS))
ret, frame = cap.read()
frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
height, width = frame.shape[:2]
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

print(f"Video: {width}x{height} @ {fps} FPS")

# Initialize components
detector = MotionDetector(min_area=500, max_area=20000, history=200, var_threshold=40)
tracker = CentroidTracker(max_disappeared=15, max_distance=100)
counter = ImprovedLineCrossCounter(frame_height=height, line_position=0.5)
visualizer = Visualizer(frame_width=width, frame_height=height)

frame_num = 0
while True:
    ret, frame = cap.read()
    if not ret:
        print("\nVideo ended")
        break
    
    frame_num += 1
    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    
    # Detect, track, count
    detections = detector.detect(frame)
    tracked = tracker.update(detections)
    events = counter.update(tracked)
    
    # Print crossing events
    for event in events:
        print(f"Frame {frame_num}: {event.direction.value} - Person {event.track_id}")
    
    # Visualize
    stats = counter.get_stats()
    annotated = visualizer.draw_all(
        frame, tracked, stats['line_y'],
        stats['in'], stats['out'], stats['occupancy'],
        fps=fps
    )
    
    # Resize for display
    display = cv2.resize(annotated, (960, 540))
    cv2.imshow('EagleEye Live Test', display)
    
    # Handle keys
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        print("\nQuitting...")
        break
    elif key == ord('r'):
        counter.reset_counts()
        print("Counts reset!")

cap.release()
cv2.destroyAllWindows()

print(f"\n=== Final Results ===")
stats = counter.get_stats()
print(f"IN: {stats['in']}")
print(f"OUT: {stats['out']}")
print(f"Occupancy: {stats['occupancy']}")
