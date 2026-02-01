"""
Debug script to trace tracking and line crossing pipeline
"""
import cv2
from src.motion_detector import MotionDetector
from src.centroid_tracker import CentroidTracker, TrackedPerson
from src.line_counter import LineCrossCounter

video_path = "Dataset/test1.mp4"

cap = cv2.VideoCapture(video_path)
ret, frame = cap.read()
frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
height, width = frame.shape[:2]
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

print(f"Frame size: {width}x{height}")
print(f"Line Y position: {height // 2}")

detector = MotionDetector(min_area=500, max_area=20000, history=200, var_threshold=40)
tracker = CentroidTracker(max_disappeared=15, max_distance=100)
line_counter = LineCrossCounter(frame_height=height, line_position=0.5)

frame_num = 0
total_detections = 0
total_tracked = 0
track_ids_seen = set()

print("\n--- Frame-by-frame tracking analysis ---\n")

while frame_num < 500:  # First 500 frames
    ret, frame = cap.read()
    if not ret:
        break
    
    frame_num += 1
    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    
    detections = detector.detect(frame)
    tracked = tracker.update(detections)
    events = line_counter.update(tracked)
    
    total_detections += len(detections)
    total_tracked += len(tracked)
    
    for t in tracked:
        track_ids_seen.add(t.track_id)
    
    # Print detailed info every 50 frames
    if frame_num % 50 == 0:
        print(f"Frame {frame_num}: {len(detections)} detections -> {len(tracked)} tracked")
        if tracked:
            for t in tracked[:3]:  # Show first 3
                print(f"  ID:{t.track_id} center_y={t.center_y} (line_y={line_counter.line_y})")
    
    # Print all crossing events
    for event in events:
        print(f"*** CROSSING: Frame {frame_num} - Track ID {event.track_id} -> {event.direction.value}")

cap.release()

print("\n--- Summary ---")
print(f"Total frames: {frame_num}")
print(f"Total detections: {total_detections} (avg: {total_detections/frame_num:.1f}/frame)")
print(f"Total tracked: {total_tracked} (avg: {total_tracked/frame_num:.1f}/frame)")
print(f"Unique track IDs seen: {len(track_ids_seen)}")
print(f"Sample IDs: {list(track_ids_seen)[:20]}")
print(f"\nFinal counts: IN={line_counter.in_count}, OUT={line_counter.out_count}")

if line_counter.in_count == 0 and line_counter.out_count == 0:
    print("\n⚠️  No crossings detected!")
    print("Possible causes:")
    print("  1. Track IDs not stable across frames")
    print("  2. Objects not crossing the center line")
    print("  3. MIN_CROSSING_DISTANCE threshold too high")
