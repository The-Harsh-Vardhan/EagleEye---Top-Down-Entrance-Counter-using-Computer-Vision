"""
Test improved line crossing detection
"""
import cv2
from src.motion_detector import MotionDetector
from src.centroid_tracker import CentroidTracker
from src.improved_line_counter import ImprovedLineCrossCounter

video_path = "Dataset/test1.mp4"

cap = cv2.VideoCapture(video_path)
ret, frame = cap.read()
frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
height, width = frame.shape[:2]
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

print(f"Frame: {width}x{height}, Line Y: {height // 2}")

detector = MotionDetector(min_area=500, max_area=20000, history=200, var_threshold=40)
tracker = CentroidTracker(max_disappeared=15, max_distance=100)
counter = ImprovedLineCrossCounter(frame_height=height, line_position=0.5)

frame_num = 0
while frame_num < 500:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame_num += 1
    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    
    detections = detector.detect(frame)
    tracked = tracker.update(detections)
    events = counter.update(tracked)
    
    for event in events:
        print(f"Frame {frame_num}: ID:{event.track_id} crossed {event.direction.value}!")
    
    if frame_num % 100 == 0:
        stats = counter.get_stats()
        print(f"[Frame {frame_num}] IN: {stats['in']}, OUT: {stats['out']}, Occupancy: {stats['occupancy']}")

cap.release()

print("\n=== FINAL RESULTS ===")
stats = counter.get_stats()
print(f"IN: {stats['in']}")
print(f"OUT: {stats['out']}")
print(f"Occupancy: {stats['occupancy']}")
