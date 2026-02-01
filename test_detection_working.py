"""
Run the exact detection approach from Dataset/eagleeye_detect.py
"""
import cv2
from ultralytics import YOLO

# Use exact same config as working script
VIDEO_PATH = "Dataset/test1.mp4"
CONF_THRESHOLD = 0.15
MIN_BOX_AREA = 100

# Load model - use the one from Dataset folder
model = YOLO("Dataset/yolov8s.pt")

cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    print("❌ Error: Cannot open video")
    exit(1)

frame_count = 0
detection_count = 0

print("Processing video...")
print("Press 'q' to quit\n")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame_count += 1
    
    # Rotate 90 degrees clockwise
    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    
    # Run detection - class 0 = person
    results = model(
        frame,
        classes=[0],
        conf=CONF_THRESHOLD,
        verbose=False
    )
    
    # Count and draw detections
    frame_detections = 0
    for r in results:
        if r.boxes is not None:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                
                area = (x2 - x1) * (y2 - y1)
                if area < MIN_BOX_AREA:
                    continue
                
                frame_detections += 1
                detection_count += 1
                
                # Draw box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(
                    frame,
                    f"Person {conf:.2f}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2
                )
    
    # Show detection stats
    cv2.putText(
        frame,
        f"Frame: {frame_count} | Detections: {frame_detections}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )
    
    # Print every 100 frames
    if frame_count % 100 == 0:
        print(f"Frame {frame_count}: {frame_detections} people detected")
    
    cv2.imshow("Detection Test", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

print(f"\n✅ Processed {frame_count} frames")
print(f"✅ Total detections: {detection_count}")
print(f"✅ Average: {detection_count/frame_count:.2f} detections per frame")
