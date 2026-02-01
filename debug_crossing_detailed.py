"""
Detailed debug of line crossing detection
"""
import cv2
from src.motion_detector import MotionDetector
from src.centroid_tracker import CentroidTracker
from src.config import MIN_CROSSING_DISTANCE

video_path = "Dataset/test1.mp4"

cap = cv2.VideoCapture(video_path)
ret, frame = cap.read()
frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
height, width = frame.shape[:2]
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

LINE_Y = height // 2  # 540
print(f"Line Y: {LINE_Y}")
print(f"MIN_CROSSING_DISTANCE: {MIN_CROSSING_DISTANCE}")

detector = MotionDetector(min_area=500, max_area=20000, history=200, var_threshold=40)
tracker = CentroidTracker(max_disappeared=15, max_distance=100)

# Track previous positions ourselves
prev_positions = {}
crossed_ids = set()
in_count = 0
out_count = 0

frame_num = 0
print("\nLooking for line crossings...\n")

while frame_num < 500:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame_num += 1
    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    
    detections = detector.detect(frame)
    tracked = tracker.update(detections)
    
    current_ids = set()
    
    for person in tracked:
        track_id = person.track_id
        current_y = person.center_y
        current_ids.add(track_id)
        
        if track_id in prev_positions:
            prev_y = prev_positions[track_id]
            
            # Debug: print when near the line
            if abs(current_y - LINE_Y) < 100 or abs(prev_y - LINE_Y) < 100:
                crossed = False
                direction = None
                
                # Check crossing criteria
                movement = abs(current_y - prev_y)
                
                if movement >= MIN_CROSSING_DISTANCE:
                    # Check if crossed from below to above
                    if prev_y > LINE_Y and current_y <= LINE_Y:
                        crossed = True
                        direction = "IN"
                        if track_id not in crossed_ids:
                            in_count += 1
                            crossed_ids.add(track_id)
                    # Check if crossed from above to below
                    elif prev_y < LINE_Y and current_y >= LINE_Y:
                        crossed = True
                        direction = "OUT"
                        if track_id not in crossed_ids:
                            out_count += 1
                            crossed_ids.add(track_id)
                
                if crossed or frame_num % 50 == 0:
                    print(f"Frame {frame_num}: ID:{track_id} prev_y={prev_y} -> current_y={current_y} "
                          f"(line={LINE_Y}, move={movement}) "
                          f"{'*** CROSSED ' + direction + '! ***' if crossed else ''}")
        
        prev_positions[track_id] = current_y
    
    # Clean up old IDs
    old_ids = set(prev_positions.keys()) - current_ids
    for old_id in old_ids:
        del prev_positions[old_id]
        crossed_ids.discard(old_id)

cap.release()

print(f"\n=== FINAL COUNTS ===")
print(f"IN: {in_count}, OUT: {out_count}")
