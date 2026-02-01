"""
Motion detection with IN/OUT counting
"""
import cv2
import numpy as np
from src.motion_detector import MotionDetector
from src.tracker import PersonTracker
from src.line_counter import LineCrossCounter, CrossingDirection

# Initialize motion detector
detector = MotionDetector(
    min_area=200,
    max_area=50000,
    history=100,
    var_threshold=25
)

# Initialize tracker
tracker = PersonTracker()

# Open video
cap = cv2.VideoCapture("Dataset/test1.mp4")
if not cap.isOpened():
    print("Error: Cannot open video")
    exit(1)

frame_count = 0
line_counter = None

print("Processing video with IN/OUT counting...")
print("="*60)
print("Green boxes = tracked people")
print("Red dots = center point")
print("Red line = counting line (middle)")
print("↑ Bottom to Top = IN")
print("↓ Top to Bottom = OUT")
print("="*60)
print("\nGive it 10-20 frames to build background model")
print("Press 'q' to quit\n")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame_count += 1
    
    # Rotate 90 degrees
    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    
    # Resize to higher resolution
    scale = 1280 / frame.shape[1]
    frame = cv2.resize(frame, None, fx=scale, fy=scale)
    
    # Calculate line position
    frame_height = frame.shape[0]
    line_y = frame_height // 2
    
    # Initialize line counter on first frame
    if line_counter is None:
        line_counter = LineCrossCounter(frame_height=frame_height, line_position=0.5)
        print(f"Line counter initialized at Y={line_y}\n")
    
    # Detect motion
    detections = detector.detect(frame)
    
    # Update tracker
    tracked_persons = tracker.update(detections)
    
    # Check for line crossings
    crossing_events = line_counter.update(tracked_persons)
    
    # Print crossing events immediately
    for event in crossing_events:
        direction_symbol = "↑" if event.direction == CrossingDirection.IN else "↓"
        print(f"[Frame {frame_count:4d}] {direction_symbol} Person #{event.track_id} crossed {event.direction.value:3s} | IN: {line_counter.in_count:3d} OUT: {line_counter.out_count:3d} | Occupancy: {line_counter.occupancy:3d}")
    
    # Draw counting line
    cv2.line(frame, (0, line_y), (frame.shape[1], line_y), (0, 0, 255), 3)
    
    # Line labels
    cv2.putText(frame, "IN (bottom -> top)", (10, line_y - 30),
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(frame, "OUT (top -> bottom)", (10, line_y + 30),
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    
    # Draw tracked persons
    for person in tracked_persons:
        x1, y1, x2, y2 = person.bbox
        
        # Green bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Red center dot
        center_x, center_y = person.center
        cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)
        
        # Track ID
        label = f"ID: {person.track_id}"
        cv2.putText(frame, label, (x1, y1 - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    # Stats overlay
    stats_y = 30
    cv2.putText(frame, f"Frame: {frame_count}", (10, stats_y),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    cv2.putText(frame, f"IN: {line_counter.in_count}", (10, stats_y + 35),
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    
    cv2.putText(frame, f"OUT: {line_counter.out_count}", (10, stats_y + 70),
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    
    cv2.putText(frame, f"Occupancy: {line_counter.occupancy}", (10, stats_y + 105),
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
    
    cv2.putText(frame, f"Tracked: {len(tracked_persons)}", (10, stats_y + 140),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Display
    cv2.imshow("EagleEye - IN/OUT Counter", frame)
    
    # Print progress every 100 frames
    if frame_count % 100 == 0:
        print(f"[Frame {frame_count:4d}] Progress - Tracked: {len(tracked_persons)} | IN: {line_counter.in_count} | OUT: {line_counter.out_count} | Occupancy: {line_counter.occupancy}")
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

print(f"\n" + "="*60)
print(f"Processing Complete!")
print(f"="*60)
print(f"Total frames: {frame_count}")
print(f"Total IN:     {line_counter.in_count}")
print(f"Total OUT:    {line_counter.out_count}")
print(f"Final Occupancy: {line_counter.occupancy}")
print(f"="*60)
