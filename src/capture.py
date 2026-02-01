"""
Video capture module for EagleEye People Counting System.

Handles video input from multiple sources:
- Local video files (MP4, AVI, etc.)
- MJPEG streams (ESP32-CAM, IP cameras)
- USB webcams

Includes retry logic for handling dropped frames gracefully.
"""

import cv2
import time
from typing import Optional, Tuple, Generator
from dataclasses import dataclass

from .config import MAX_FRAME_RETRIES, FRAME_RETRY_DELAY, FRAME_SKIP


@dataclass
class FrameData:
    """
    Container for frame data with metadata.
    
    Attributes:
        frame: The actual image frame (numpy array)
        frame_number: Sequential frame count
        timestamp: Time when frame was captured
        fps: Current frames per second
    """
    frame: any  # numpy.ndarray
    frame_number: int
    timestamp: float
    fps: float


class VideoCapture:
    """
    Video capture handler supporting multiple input sources.
    
    Provides a unified interface for reading frames from video files,
    MJPEG streams, or webcams with automatic retry on dropped frames.
    """
    
    def __init__(self, source: str):
        """
        Initialize video capture from the given source.
        
        Args:
            source: Video source - can be:
                    - Path to video file (e.g., "video.mp4")
                    - MJPEG stream URL (e.g., "http://192.168.1.100:81/stream")
                    - Webcam index as string (e.g., "0")
        
        Raises:
            ValueError: If the source cannot be opened
        """
        self.source = source
        self.cap = None
        self.frame_count = 0
        self.start_time = None
        self._fps_counter = 0
        self._fps_start_time = None
        self._current_fps = 0.0
        
        self._open_source()
    
    def _open_source(self) -> None:
        """
        Open the video source.
        
        Determines source type and configures capture accordingly.
        """
        # Check if source is a webcam index
        if self.source.isdigit():
            source = int(self.source)
        else:
            source = self.source
        
        self.cap = cv2.VideoCapture(source)
        
        # For MJPEG streams, set buffer size to minimize latency
        if isinstance(source, str) and source.startswith(('http://', 'https://')):
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        if not self.cap.isOpened():
            raise ValueError(f"Cannot open video source: {self.source}")
        
        self.start_time = time.time()
        self._fps_start_time = time.time()
    
    @property
    def width(self) -> int:
        """Get frame width in pixels."""
        return int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    
    @property
    def height(self) -> int:
        """Get frame height in pixels."""
        return int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    @property
    def source_fps(self) -> float:
        """Get the source video's native FPS (may be 0 for streams)."""
        return self.cap.get(cv2.CAP_PROP_FPS)
    
    @property
    def total_frames(self) -> int:
        """Get total frame count (0 for live streams)."""
        return int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    def _update_fps(self) -> None:
        """Update the FPS calculation."""
        self._fps_counter += 1
        elapsed = time.time() - self._fps_start_time
        
        # Update FPS every second
        if elapsed >= 1.0:
            self._current_fps = self._fps_counter / elapsed
            self._fps_counter = 0
            self._fps_start_time = time.time()
    
    def read_frame(self) -> Optional[FrameData]:
        """
        Read a single frame from the video source.
        
        Implements retry logic for dropped frames. Skips frames
        according to FRAME_SKIP setting for performance tuning.
        
        Returns:
            FrameData object if successful, None if end of stream
            or max retries exceeded.
        """
        retries = 0
        
        while retries < MAX_FRAME_RETRIES:
            ret, frame = self.cap.read()
            
            if ret and frame is not None:
                self.frame_count += 1
                
                # Skip frames if configured (for performance)
                if FRAME_SKIP > 1 and self.frame_count % FRAME_SKIP != 0:
                    continue
                
                self._update_fps()
                
                return FrameData(
                    frame=frame,
                    frame_number=self.frame_count,
                    timestamp=time.time(),
                    fps=self._current_fps
                )
            
            # Frame drop detected - retry
            retries += 1
            if retries < MAX_FRAME_RETRIES:
                time.sleep(FRAME_RETRY_DELAY)
        
        # Check if we've reached end of video file
        if self.total_frames > 0 and self.frame_count >= self.total_frames:
            return None  # End of video
        
        # Max retries exceeded for stream
        print(f"Warning: Dropped {MAX_FRAME_RETRIES} consecutive frames")
        return None
    
    def frames(self) -> Generator[FrameData, None, None]:
        """
        Generator that yields frames continuously.
        
        Yields:
            FrameData objects until end of stream or error
        
        Example:
            capture = VideoCapture("video.mp4")
            for frame_data in capture.frames():
                process(frame_data.frame)
        """
        while True:
            frame_data = self.read_frame()
            if frame_data is None:
                break
            yield frame_data
    
    def release(self) -> None:
        """Release the video capture resources."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures resources are released."""
        self.release()
        return False
    
    def get_info(self) -> dict:
        """
        Get information about the video source.
        
        Returns:
            Dictionary with source properties
        """
        return {
            'source': self.source,
            'width': self.width,
            'height': self.height,
            'source_fps': self.source_fps,
            'total_frames': self.total_frames,
            'is_stream': self.total_frames == 0 or self.source.startswith(('http://', 'https://'))
        }
