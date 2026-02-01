"""
Simple motion detection test - show what the detector sees
"""
import cv2
import numpy as np
from src.motion_detector import MotionDetector

video_path = "Dataset/test1.mp4"
detector = MotionDetector(min_area=150, max_area=10000)

cap = cv2.VideoCapture(video_path)
frame_num = 0
motion_frames = 0

print("Testing motion detection...")
print("Press 'q' to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame_num += 1
    
    # Rotate
    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    
    # Detect motion
    detections = detector.detect(frame)
    
    if len(detections) > 0:
        motion_frames += 1
        print(f"Frame {frame_num}: {len(detections)} moving objects detected")
        
        # Draw detections
        for det in detections:
            x1, y1, x2, y2 = det.bbox
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Show centroid
            cx, cy = det.center
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
    
    # Draw center line
    h = frame.shape[0]
    line_y = h // 2
    cv2.line(frame, (0, line_y), (frame.shape[1], line_y), (0, 0, 255), 2)
    
    # Resize and display
    display = cv2.resize(frame, (960, 540))
    cv2.imshow('Motion Detection Test', display)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

print(f"\n=== Results ===")
print(f"Total frames: {frame_num}")
print(f"Frames with motion: {motion_frames}")
if frame_num > 0:
    print(f"Motion rate: {100*motion_frames/frame_num:.1f}%")
