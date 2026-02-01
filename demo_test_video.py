"""
Demo script to visualize motion detection and tracking on test videos
Shows what the system detects and which objects cross the line
"""
import cv2
import sys
from src.motion_detector import MotionDetector
from src.centroid_tracker import CentroidTracker
from src.improved_line_counter import ImprovedLineCrossCounter
from src.visualizer import Visualizer

# Configuration
video_path = sys.argv[1] if len(sys.argv) > 1 else "Dataset/test1.mp4"
output_video = "demo_output.mp4"
line_position = 0.5

print(f"Processing: {video_path}")
print(f"Output: {output_video}")
print(f"Line position: {line_position}")
print("-" * 60)

# Open video
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"Error: Cannot open {video_path}")
    sys.exit(1)

# Get properties
fps = int(cap.get(cv2.CAP_PROP_FPS))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Read first frame to get dimensions
ret, frame = cap.read()
if not ret:
    print("Error: Cannot read first frame")
    sys.exit(1)

# Rotate frame
frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
height, width = frame.shape[:2]

print(f"Video: {width}x{height} @ {fps} FPS, {total_frames} frames")
print(f"Initializing components...")

# Initialize components with optimized parameters
# Larger min_area and tighter thresholds for more stable tracking
detector = MotionDetector(
    min_area=500,      # Increased from 200 - filter small noise
    max_area=20000,    # Reduced from 50000 - focus on person-sized objects  
    history=200,       # More history for stable background
    var_threshold=40   # Higher threshold = less sensitive to small changes
)
tracker = CentroidTracker(max_disappeared=15, max_distance=100)
line_counter = ImprovedLineCrossCounter(frame_height=height, line_position=line_position)
visualizer = Visualizer(frame_width=width, frame_height=height)

# Video writer
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
writer = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

# Reset to beginning
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

# Process video
frame_num = 0
crossings = []

from tqdm import tqdm
print("Processing video... (optimized - no display window for speed)\n")

# Use tqdm progress bar
with tqdm(total=total_frames, desc="Processing", unit="frame") as pbar:
  while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    pbar.update(1)
    
    frame_num += 1
    
    # Rotate
    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    
    # Detect motion
    detections = detector.detect(frame)
    
    # Track objects
    tracked = tracker.update(detections)
    
    # Check for line crossings
    events = line_counter.update(tracked)
    
    # Log crossings
    for event in events:
        crossings.append({
            'frame': frame_num,
            'track_id': event.track_id,
            'direction': event.direction.value
        })
        print(f"Frame {frame_num}: Person {event.track_id} crossed {event.direction.value}")
    
    # Visualize
    stats = line_counter.get_stats()
    annotated = visualizer.draw_all(
        frame, tracked, stats['line_y'], 
        stats['in'], stats['out'], stats['occupancy'],
        fps=fps
    )
    
    # Add frame counter
    cv2.putText(annotated, f"Frame: {frame_num}/{total_frames}", 
                (10, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 
                0.6, (255, 255, 255), 2)
    
    # Write frame
    writer.write(annotated)
    
    # Update progress description with stats (every 100 frames)
    if frame_num % 100 == 0:
        pbar.set_postfix(IN=stats['in'], OUT=stats['out'], 
                         Detections=len(detections), Tracked=len(tracked))

# Cleanup
cap.release()
writer.release()
cv2.destroyAllWindows()

# Summary
print("\n" + "="*60)
print("PROCESSING COMPLETE")
print("="*60)
stats = line_counter.get_stats()
print(f"Total frames processed: {frame_num}")
print(f"Total IN:  {stats['in']}")
print(f"Total OUT: {stats['out']}")
print(f"Occupancy: {stats['occupancy']}")
print(f"Total crossings: {len(crossings)}")
print(f"\nOutput saved to: {output_video}")

if crossings:
    print("\nCrossing Events:")
    for c in crossings[:10]:  # Show first 10
        print(f"  Frame {c['frame']}: Person {c['track_id']} - {c['direction']}")
    if len(crossings) > 10:
        print(f"  ... and {len(crossings)-10} more")
else:
    print("\n⚠ No crossings detected!")
    print("This is normal for these test videos - they show a cafeteria")
    print("with people moving around tables, not crossing an entrance.")

print("\nTo play the output video:")
print(f"  Start-Process {output_video}")
print("="*60)
