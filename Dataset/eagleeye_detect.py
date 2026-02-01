import cv2
import time
from ultralytics import YOLO

# ================= CONFIG =================
VIDEO_PATH = "test1.mp4"
CONF_THRESHOLD = 0.15      # very low for difficult top-down angle
MIN_BOX_AREA = 100         # minimal filter
# ==========================================

def main():
    # Load YOLOv8 model - using 'small' model for better detection
    # The larger model has more capacity to detect unusual angles
    model = YOLO("yolov8s.pt")

    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print("❌ Error: Cannot open video")
        return

    prev_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Rotate 90 degrees clockwise to fix orientation
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

        # NO resize - process at full resolution for better detection

        # Run person detection (class 0 = person)
        results = model(
            frame,
            classes=[0],
            conf=CONF_THRESHOLD,
            verbose=False
        )

        # Draw detections
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])

                area = (x2 - x1) * (y2 - y1)
                if area < MIN_BOX_AREA:
                    continue

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    frame,
                    f"Person {conf:.2f}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2
                )

        # FPS calculation
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time)
        prev_time = curr_time

        cv2.putText(
            frame,
            f"FPS: {int(fps)}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2
        )

        cv2.imshow("EagleEye - Person Detection", frame)

        # ESC to quit
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
