"""
EagleEye - Top-down People Counting System

Main entry point for the application. Orchestrates video capture,
person detection, tracking, line crossing detection, and visualization.

Usage:
    python main.py --source video.mp4
    python main.py --source http://192.168.1.100:81/stream
    python main.py --source 0  # Webcam
"""

import argparse
import cv2
import sys
from datetime import datetime
from tqdm import tqdm

from src.config import (
    CONFIDENCE_THRESHOLD,
    DEFAULT_LINE_POSITION,
    MIN_DETECTION_SIZE,
    PROCESSING_WIDTH,
    VERSION,
    LOG_LEVEL,
    LOG_TO_FILE
)
from src.logging_config import setup_logging, get_logger
from src.capture import VideoCapture
from src.detector import PersonDetector
from src.motion_detector import MotionDetector
from src.tracker import PersonTracker
from src.centroid_tracker import CentroidTracker
from src.line_counter import LineCrossCounter, CrossingDirection
from src.improved_line_counter import ImprovedLineCrossCounter
from src.database import Database
from src.visualizer import Visualizer
from src.scheduler import is_meal_time, get_meal_info, print_schedule

# Initialize logger
logger = setup_logging(level=LOG_LEVEL, log_to_file=LOG_TO_FILE)


def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        Namespace object with parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='EagleEye - Top-down People Counting System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
    python main.py --source video.mp4
    python main.py --source http://192.168.1.100:81/stream
    python main.py --source 0 --line-position 0.6
    python main.py --source video.mp4 --confidence 0.6 --no-display
        '''
    )
    
    parser.add_argument(
        '--source', '-s',
        type=str,
        required=True,
        help='Video source: file path, MJPEG URL, or webcam index'
    )
    
    parser.add_argument(
        '--line-position', '-l',
        type=float,
        default=DEFAULT_LINE_POSITION,
        help=f'Line position as ratio (0=top, 1=bottom). Default: {DEFAULT_LINE_POSITION}'
    )
    
    parser.add_argument(
        '--confidence', '-c',
        type=float,
        default=CONFIDENCE_THRESHOLD,
        help=f'Detection confidence threshold (0-1). Default: {CONFIDENCE_THRESHOLD}'
    )
    
    parser.add_argument(
        '--min-size',
        type=int,
        default=MIN_DETECTION_SIZE[0],
        help=f'Minimum detection size in pixels. Default: {MIN_DETECTION_SIZE[0]}'
    )
    
    parser.add_argument(
        '--no-display',
        action='store_true',
        help='Run without displaying video (headless mode)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default=None,
        help='Output video file path (optional)'
    )
    
    parser.add_argument(
        '--reset-db',
        action='store_true',
        help='Reset the database before starting'
    )
    
    parser.add_argument(
        '--motion',
        action='store_true',
        help='Use motion detection instead of YOLO (better for top-down views)'
    )
    
    parser.add_argument(
        '--rotate',
        type=int,
        default=0,
        choices=[0, 90, 180, 270],
        help='Rotate video by degrees (0, 90, 180, 270)'
    )
    
    parser.add_argument(
        '--scheduled',
        action='store_true',
        help='Only run during meal times (7:30-10am, 12-2pm, 5:30-6:30pm, 7:30-10pm)'
    )
    
    return parser.parse_args()


def main():
    """
    Main application loop.
    
    Coordinates all components:
    1. Video capture
    2. Person detection (YOLOv8)
    3. Tracking (ByteTrack)
    4. Line crossing detection
    5. Database logging
    6. Visualization
    """
    args = parse_arguments()
    
    logger.info("=" * 60)
    logger.info(f"🦅 EagleEye v{VERSION} - People Counting System")
    logger.info("=" * 60)
    
    # Check meal schedule if --scheduled flag is used
    if args.scheduled:
        print_schedule()
        meal_info = get_meal_info()
        
        if not meal_info['active']:
            print(f"⏸️  System is PAUSED - outside meal hours")
            print(f"   {meal_info['message']}")
            print("\nRun without --scheduled flag to override.")
            sys.exit(0)
        else:
            print(f"✅ {meal_info['message']}")
            print(f"   Active until {meal_info['end_time']}")
    
    logger.info(f"Source: {args.source}")
    logger.info(f"Line position: {args.line_position}")
    logger.info(f"Confidence threshold: {args.confidence}")
    logger.info("=" * 60)
    
    # Initialize database
    db = Database()
    if args.reset_db:
        logger.warning("Resetting database...")
        db.clear_events()
    
    # Load any existing counts from database
    total_in, total_out = db.get_total_counts()
    logger.info(f"Previous counts - IN: {total_in}, OUT: {total_out}")
    
    # Initialize video capture
    try:
        capture = VideoCapture(args.source)
        info = capture.get_info()
        print(f"Video opened: {info['width']}x{info['height']}")
        if info['is_stream']:
            print("Mode: Live stream")
        else:
            print(f"Mode: Video file ({info['total_frames']} frames)")
    except ValueError as e:
        logger.error(f"Failed to open video source: {e}")
        sys.exit(1)
    
    # Calculate dimensions after rotation
    if args.rotate in [90, 270]:
        # Width and height swap when rotating 90 or 270 degrees
        frame_width = capture.height
        frame_height = capture.width
    else:
        frame_width = capture.width
        frame_height = capture.height
    
    # Apply processing resize to dimensions
    if PROCESSING_WIDTH and frame_width > PROCESSING_WIDTH:
        scale = PROCESSING_WIDTH / frame_width
        frame_width = PROCESSING_WIDTH
        frame_height = int(frame_height * scale)
    
    print(f"Processing dimensions: {frame_width}x{frame_height}")
    
    # Initialize detector based on mode
    if args.motion:
        print("Detection mode: Motion-based (background subtraction)")
        detector = MotionDetector(
            min_area=500,      # Increased for more stable tracking
            max_area=20000,    # Person-sized objects
            history=200,       # Stable background model
            var_threshold=40   # Less sensitive to noise
        )
    else:
        print("Detection mode: YOLOv8")
        detector = PersonDetector(
            confidence_threshold=args.confidence,
            min_size=(args.min_size, args.min_size)
        )
    
    # Initialize tracker - use CentroidTracker for motion mode (more stable IDs)
    if args.motion:
        tracker = CentroidTracker(max_disappeared=15, max_distance=100)
    else:
        tracker = PersonTracker()
    
    # Initialize line counter - use ImprovedLineCrossCounter for motion mode
    # (tracks initial position for slow-moving objects)
    if args.motion:
        line_counter = ImprovedLineCrossCounter(
            frame_height=frame_height,
            line_position=args.line_position
        )
    else:
        line_counter = LineCrossCounter(
            frame_height=frame_height,
            line_position=args.line_position
        )
    
    # Set initial counts from database
    line_counter.in_count = total_in
    line_counter.out_count = total_out
    
    # Initialize visualizer with rotated dimensions
    visualizer = Visualizer(frame_width, frame_height)
    
    # Initialize video writer if output is specified
    video_writer = None
    if args.output:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(
            args.output,
            fourcc,
            30.0,  # FPS
            (frame_width, frame_height)
        )
        print(f"Saving output to: {args.output}")
    
    print("\nStarting processing...")
    print("Press 'q' to quit, 'r' to reset counts")
    print("-" * 60)
    
    # Create progress bar for video files (not streams)
    total_frames = capture.total_frames if not info['is_stream'] else None
    progress_bar = tqdm(
        capture.frames(),
        total=total_frames,
        desc="Processing",
        unit="frame",
        disable=info['is_stream'],  # Disable for live streams
        ncols=80
    )
    
    try:
        # Main processing loop
        for frame_data in progress_bar:
            frame = frame_data.frame
            fps = frame_data.fps
            
            # Apply rotation if specified
            if args.rotate == 90:
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            elif args.rotate == 180:
                frame = cv2.rotate(frame, cv2.ROTATE_180)
            elif args.rotate == 270:
                frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            
            # Resize frame for faster processing
            if PROCESSING_WIDTH and frame.shape[1] > PROCESSING_WIDTH:
                scale = PROCESSING_WIDTH / frame.shape[1]
                frame = cv2.resize(frame, None, fx=scale, fy=scale)
            
            # Step 1: Detect persons
            detections = detector.detect(frame)
            
            # Step 2: Update tracker
            tracked_persons = tracker.update(detections)
            
            # Step 3: Check for line crossings
            events = line_counter.update(tracked_persons)
            
            # Step 4: Log crossing events to database
            for event in events:
                db.log_event(
                    direction=event.direction.value,
                    occupancy=line_counter.occupancy,
                    timestamp=datetime.now()
                )
                logger.info(
                    f"ID:{event.track_id} crossed {event.direction.value} "
                    f"| IN:{line_counter.in_count} OUT:{line_counter.out_count} "
                    f"| Occupancy:{line_counter.occupancy}"
                )
            
            # Step 5: Visualize
            stats = line_counter.get_stats()
            annotated_frame = visualizer.draw_all(
                frame,
                tracked_persons,
                stats['line_y'],
                stats['in'],
                stats['out'],
                stats['occupancy'],
                fps
            )
            
            # Draw event notifications (flash briefly on crossing)
            for event in events:
                color = (0, 255, 0) if event.direction == CrossingDirection.IN else (0, 0, 255)
                annotated_frame = visualizer.draw_event_notification(
                    annotated_frame,
                    f"Person {event.track_id} - {event.direction.value}",
                    color
                )
            
            # Write to output video if specified
            if video_writer:
                video_writer.write(annotated_frame)
            
            # Display frame (unless headless mode)
            if not args.no_display:
                cv2.imshow('EagleEye - People Counter', annotated_frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    print("\nQuitting...")
                    break
                elif key == ord('r'):
                    print("\nResetting counts...")
                    line_counter.reset_counts()
                    db.clear_events()
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    finally:
        # Cleanup
        capture.release()
        if video_writer:
            video_writer.release()
        cv2.destroyAllWindows()
        
        # Print final statistics
        print("\n" + "=" * 60)
        print("Final Statistics")
        print("=" * 60)
        stats = line_counter.get_stats()
        print(f"Total IN:     {stats['in']}")
        print(f"Total OUT:    {stats['out']}")
        print(f"Occupancy:    {stats['occupancy']}")
        print("=" * 60)
        
        # Show database summary
        events = db.get_events(limit=10)
        if events:
            print(f"\nLast {len(events)} events in database:")
            for event in events:
                print(f"  {event['timestamp']} | {event['direction']:3s} | Occupancy: {event['occupancy']}")


if __name__ == '__main__':
    main()
