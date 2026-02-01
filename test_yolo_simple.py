"""
Simple YOLO test - see what it actually detects
"""
import cv2
from ultralytics import YOLO

# Load model
model = YOLO("Dataset/yolov8s.pt")

# Open video
cap = cv2.VideoCapture("Dataset/test1.mp4")
ret, frame = cap.read()

if ret:
    # Rotate
    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    
    print(f"Frame shape: {frame.shape}")
    print("Running YOLO detection with conf=0.15, classes=[0]...")
    
    # Try detection with very low conf
    results = model(frame, classes=[0], conf=0.15, verbose=True)
    
    # Check what we got
    for r in results:
        print(f"\nNumber of detections: {len(r.boxes) if r.boxes else 0}")
        
        if r.boxes and len(r.boxes) > 0:
            for i, box in enumerate(r.boxes):
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                print(f"  Detection {i}: bbox=({x1},{y1},{x2},{y2}) conf={conf:.3f}")
        else:
            print("  No person detections found!")
    
    # Try with ALL classes to see if anything is detected
    print("\n\nTrying with ALL classes (conf=0.15)...")
    results_all = model(frame, conf=0.15, verbose=True)
    
    for r in results_all:
        print(f"\nTotal detections (all classes): {len(r.boxes) if r.boxes else 0}")
        
        if r.boxes and len(r.boxes) > 0:
            # Show first 10
            for i, box in enumerate(r.boxes[:10]):
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                print(f"  Detection {i}: class={cls} conf={conf:.3f}")

cap.release()
