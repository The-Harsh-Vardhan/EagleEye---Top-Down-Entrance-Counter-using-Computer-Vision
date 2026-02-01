"""
Diagnostic tool to visualize detections and help debug why counting isn't working
"""
import cv2
import sys
from src.detector import PersonDetector
from src.motion_detector import MotionDetector

video_path = "Dataset/test1.mp4" if len(sys.argv) < 2 else sys.argv[1]
use_motion = "--motion" in sys.argv

cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"Error: Cannot open {video_path}")
    sys.exit(1)

# Initialize detector
if use_motion:
    print("Using motion detection")
    detector = MotionDetector(min_area=200, max_area=50000)
else:
    print("Using YOLO detection (confidence=0.1)")
    detector = PersonDetector(confidence_threshold=0.1)

frame_count = 0
detection_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame_count += 1
    
    # Rotate 90 degrees
    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    
    # Detect
    detections = detector.detect(frame)
    
    if len(detections) > 0:
        detection_count += 1
        print(f"Frame {frame_count}: Found {len(detections)} detections")
        
        # Draw detections
        for det in detections:
            x1, y1, x2, y2 = det[0:4]
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        
        # Show frame with detections
        cv2.imshow('Detections', cv2.resize(frame, (960, 540)))
        if cv2.waitKey(100) & 0xFF == ord('q'):
            break
    
    # Sample every 30 frames
    if frame_count % 30 == 0:
        print(f"Processed {frame_count} frames, detections in {detection_count} frames")

cap.release()
cv2.destroyAllWindows()

print(f"\n=== Summary ===")
print(f"Total frames: {frame_count}")
print(f"Frames with detections: {detection_count}")
print(f"Detection rate: {100*detection_count/frame_count if frame_count > 0 else 0:.1f}%")
