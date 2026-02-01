"""
Save a frame to see what we're working with
"""
import cv2

# Open video
cap = cv2.VideoCapture("Dataset/test1.mp4")

# Skip to middle of video
cap.set(cv2.CAP_PROP_POS_FRAMES, 500)

ret, frame = cap.read()

if ret:
    # Save original
    cv2.imwrite("frame_original.jpg", frame)
    print("Saved: frame_original.jpg")
    
    # Save rotated
    frame_rotated = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    cv2.imwrite("frame_rotated.jpg", frame_rotated)
    print("Saved: frame_rotated.jpg")
    
    print(f"\nOriginal shape: {frame.shape}")
    print(f"Rotated shape: {frame_rotated.shape}")
    print(f"Pixel value range: {frame.min()} - {frame.max()}")

cap.release()
