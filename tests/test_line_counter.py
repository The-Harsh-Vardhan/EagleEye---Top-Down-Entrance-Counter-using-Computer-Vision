"""
Unit tests for the LineCrossCounter module.

Tests crossing detection, direction classification, and edge cases.
"""

import sys
import pytest
from pathlib import Path
from dataclasses import dataclass
from typing import Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.line_counter import LineCrossCounter, CrossingDirection


@dataclass
class MockTrackedPerson:
    """Mock tracked person for testing."""
    track_id: int
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    
    @property
    def center(self) -> Tuple[int, int]:
        """Calculate center from bbox."""
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) // 2, (y1 + y2) // 2)
    
    @property
    def center_y(self) -> int:
        """Get Y coordinate of center."""
        return self.center[1]


@pytest.fixture
def counter():
    """Create a line counter with frame height of 1000px."""
    return LineCrossCounter(frame_height=1000, line_position=0.5)


class TestLineCrossCounterInit:
    """Tests for counter initialization."""
    
    def test_default_line_position(self):
        """Test default line position at 50%."""
        counter = LineCrossCounter(frame_height=1000)
        assert counter.line_y == 500
    
    def test_custom_line_position(self):
        """Test custom line position."""
        counter = LineCrossCounter(frame_height=1000, line_position=0.3)
        assert counter.line_y == 300
    
    def test_initial_counts_zero(self, counter):
        """Test that initial counts are zero."""
        assert counter.in_count == 0
        assert counter.out_count == 0
        assert counter.occupancy == 0


class TestCrossingDetection:
    """Tests for crossing detection."""
    
    def test_no_crossing_when_above_line(self, counter):
        """Test no crossing when person stays above line."""
        person = MockTrackedPerson(track_id=1, bbox=(100, 100, 150, 150))
        
        events = counter.update([person])
        assert len(events) == 0
    
    def test_no_crossing_when_below_line(self, counter):
        """Test no crossing when person stays below line."""
        person = MockTrackedPerson(track_id=1, bbox=(100, 600, 150, 650))
        
        events = counter.update([person])
        assert len(events) == 0
    
    def test_in_crossing_bottom_to_top(self, counter):
        """Test IN crossing (bottom to top)."""
        # First frame: below line
        person_below = MockTrackedPerson(track_id=1, bbox=(100, 600, 150, 650))
        counter.update([person_below])
        
        # Second frame: above line (crossed upward = IN)
        person_above = MockTrackedPerson(track_id=1, bbox=(100, 400, 150, 450))
        events = counter.update([person_above])
        
        assert len(events) == 1
        assert events[0].direction == CrossingDirection.IN
        assert counter.in_count == 1
    
    def test_out_crossing_top_to_bottom(self, counter):
        """Test OUT crossing (top to bottom)."""
        # First frame: above line
        person_above = MockTrackedPerson(track_id=1, bbox=(100, 400, 150, 450))
        counter.update([person_above])
        
        # Second frame: below line (crossed downward = OUT)
        person_below = MockTrackedPerson(track_id=1, bbox=(100, 600, 150, 650))
        events = counter.update([person_below])
        
        assert len(events) == 1
        assert events[0].direction == CrossingDirection.OUT
        assert counter.out_count == 1


class TestOccupancy:
    """Tests for occupancy tracking."""
    
    def test_occupancy_increases_on_in(self, counter):
        """Test occupancy increases on IN crossing."""
        # Simulate IN crossing
        counter.in_count = 5
        counter.out_count = 2
        
        stats = counter.get_stats()
        assert stats['occupancy'] == 3
    
    def test_occupancy_property(self, counter):
        """Test occupancy property calculation."""
        counter.in_count = 10
        counter.out_count = 7
        
        assert counter.occupancy == 3


class TestDuplicatePrevention:
    """Tests for duplicate crossing prevention."""
    
    def test_same_track_counted_once_per_crossing(self, counter):
        """Test that same track is only counted once per crossing."""
        # First crossing
        person_below = MockTrackedPerson(track_id=1, bbox=(100, 600, 150, 650))
        counter.update([person_below])
        
        person_above = MockTrackedPerson(track_id=1, bbox=(100, 400, 150, 450))
        events = counter.update([person_above])
        assert len(events) == 1
        
        # Same position - should not trigger again
        events = counter.update([person_above])
        assert len(events) == 0


class TestMultiplePersons:
    """Tests for multiple person tracking."""
    
    def test_multiple_persons_tracked_separately(self, counter):
        """Test multiple persons are tracked separately."""
        # Two persons below line
        person1 = MockTrackedPerson(track_id=1, bbox=(100, 600, 150, 650))
        person2 = MockTrackedPerson(track_id=2, bbox=(200, 600, 250, 650))
        counter.update([person1, person2])
        
        # Both cross to above line
        person1_above = MockTrackedPerson(track_id=1, bbox=(100, 400, 150, 450))
        person2_above = MockTrackedPerson(track_id=2, bbox=(200, 400, 250, 450))
        events = counter.update([person1_above, person2_above])
        
        assert len(events) == 2
        assert counter.in_count == 2


class TestResetCounts:
    """Tests for count reset functionality."""
    
    def test_reset_counts(self, counter):
        """Test resetting counts."""
        counter.in_count = 10
        counter.out_count = 5
        
        counter.reset_counts()
        
        assert counter.in_count == 0
        assert counter.out_count == 0


class TestGetStats:
    """Tests for statistics method."""
    
    def test_get_stats_returns_dict(self, counter):
        """Test that get_stats returns a dictionary."""
        stats = counter.get_stats()
        
        assert isinstance(stats, dict)
        assert 'in' in stats
        assert 'out' in stats
        assert 'occupancy' in stats
        assert 'line_y' in stats
    
    def test_get_stats_values(self, counter):
        """Test get_stats values."""
        counter.in_count = 15
        counter.out_count = 8
        
        stats = counter.get_stats()
        
        assert stats['in'] == 15
        assert stats['out'] == 8
        assert stats['occupancy'] == 7
        assert stats['line_y'] == 500
