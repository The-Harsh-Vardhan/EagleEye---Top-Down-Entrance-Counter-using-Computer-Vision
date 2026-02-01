"""
EagleEye - Motion-based Person Detection for Top-down View

Uses background subtraction to detect moving objects, then treats
each moving blob as a person. Much more reliable for overhead cameras
where people appear as small moving dots.
"""

import cv2
import time
import numpy as np

# ================= CONFIG =================
VIDEO_PATH = "test1.mp4"
MIN_CONTOUR_AREA = 500      # Minimum area to consider as a person
MAX_CONTOUR_AREA = 50000    # Maximum area (filter out large noise)
BLUR_SIZE = 5               # Gaussian blur kernel size
MORPH_KERNEL_SIZE = 5       # Morphological operations kernel
DETECTION_THRESHOLD = 25    # Background subtraction threshold
# ==========================================


def main():
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print("❌ Error: Cannot open video")
        return

    # Background subtractor - MOG2 works well for varying lighting
    bg_subtractor = cv2.createBackgroundSubtractorMOG2(
        history=500,
        varThreshold=50,
        detectShadows=True
    )

    # Morphological kernel for cleaning up the mask
    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE, 
        (MORPH_KERNEL_SIZE, MORPH_KERNEL_SIZE)
    )

    prev_time = time.time()
    person_id = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Rotate 90 degrees clockwise to fix orientation
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        
        # Resize for speed while keeping aspect ratio
        scale = 960 / frame.shape[1]
        frame = cv2.resize(frame, None, fx=scale, fy=scale)
        display_frame = frame.copy()

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(frame, (BLUR_SIZE, BLUR_SIZE), 0)

        # Apply background subtraction
        fg_mask = bg_subtractor.apply(blurred)

        # Remove shadows (shadows are marked as 127 in MOG2)
        fg_mask[fg_mask == 127] = 0

        # Apply threshold to get binary mask
        _, fg_mask = cv2.threshold(fg_mask, DETECTION_THRESHOLD, 255, cv2.THRESH_BINARY)

        # Morphological operations to clean up the mask
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)   # Remove noise
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)  # Fill gaps
        fg_mask = cv2.dilate(fg_mask, kernel, iterations=2)           # Expand blobs

        # Find contours (moving objects)
        contours, _ = cv2.findContours(
            fg_mask, 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )

        # Process each contour as a potential person
        detections = []
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Filter by area
            if area < MIN_CONTOUR_AREA or area > MAX_CONTOUR_AREA:
                continue

            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Calculate center point
            cx, cy = x + w // 2, y + h // 2
            
            detections.append({
                'bbox': (x, y, x + w, y + h),
                'center': (cx, cy),
                'area': area
            })

        # Draw detections
        for i, det in enumerate(detections):
            x1, y1, x2, y2 = det['bbox']
            cx, cy = det['center']

            # Draw bounding box
            cv2.rectangle(
                display_frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            # Draw label
            label = f"Person {i+1}"
            cv2.putText(
                display_frame,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

            # Draw center point
            cv2.circle(display_frame, (cx, cy), 5, (0, 0, 255), -1)

        # FPS calculation
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
        prev_time = curr_time

        # Draw FPS and detection count
        cv2.putText(
            display_frame,
            f"FPS: {int(fps)}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2
        )

        cv2.putText(
            display_frame,
            f"Detected: {len(detections)}",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        # Show both the original with detections and the mask
        cv2.imshow("EagleEye - Motion Detection", display_frame)
        cv2.imshow("Motion Mask", fg_mask)

        # ESC to quit
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    print("✅ Detection complete")


if __name__ == "__main__":
    main()
