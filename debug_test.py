"""
Debug script to test detection on video
"""

import cv2
from src.detector import PersonDetector
from src.config import YOLO_MODEL

# Initialize detector with very low confidence
detector = PersonDetector(
    model_path=YOLO_MODEL,
    confidence_threshold=0.2,  # Very low threshold
    min_size=(10, 10)  # Very small minimum size
)

# Open video
video_path = "Dataset/test1.mp4"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print(f"Error: Could not open video {video_path}")
    exit(1)

print(f"Video opened: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
print(f"Total frames: {int(cap.get(cv2.CAP_PROP_FRAME_COUNT))}")
print(f"FPS: {cap.get(cv2.CAP_PROP_FPS)}")
print("\nProcessing frames... Press 'q' to quit, 'p' to pause")
print("-" * 60)

frame_count = 0
paused = False

while True:
    if not paused:
        ret, frame = cap.read()
        if not ret:
            print("End of video")
            break
        
        frame_count += 1
        
        # Rotate frame 90 degrees
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        
        # Detect persons
        detections = detector.detect(frame)
        
        # Print detection info
        if frame_count % 30 == 0:  # Every 30 frames
            print(f"Frame {frame_count}: {len(detections)} detections")
        
        # Draw detections
        for det in detections:
            x1, y1, x2, y2 = det.bbox
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"Person: {det.confidence:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Add info overlay
        info_text = f"Frame: {frame_count} | Detections: {len(detections)}"
        cv2.putText(frame, info_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Display
    cv2.imshow('Debug - Detection Test', frame)
    
    # Handle keys
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('p'):
        paused = not paused
        print("PAUSED" if paused else "RESUMED")

cap.release()
cv2.destroyAllWindows()

print("\nProcessing complete!")
print(f"Total frames processed: {frame_count}")
