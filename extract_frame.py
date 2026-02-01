"""
Extract a sample frame from the video to analyze the content
"""
import cv2
import sys

video_path = sys.argv[1] if len(sys.argv) > 1 else "Dataset/test1.mp4"
output_path = "sample_frame.jpg"

cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"Error: Cannot open {video_path}")
    sys.exit(1)

# Get video properties
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print(f"Total frames: {total_frames}")

# Jump to middle of video
cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames // 2)

ret, frame = cap.read()
if ret:
    # Save original frame
    cv2.imwrite(output_path, frame)
    print(f"✅ Saved frame to {output_path}")
    print(f"   Size: {frame.shape[1]}x{frame.shape[0]}")
    
    # Save rotated version
    frame_rot = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    cv2.imwrite("sample_frame_rotated.jpg", frame_rot)
    print(f"✅ Saved rotated frame to sample_frame_rotated.jpg")
    print(f"   Size: {frame_rot.shape[1]}x{frame_rot.shape[0]}")
else:
    print("Error: Could not read frame")

cap.release()
