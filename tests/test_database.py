"""
Unit tests for the Database module.

Tests CRUD operations, event logging, and query functionality.
"""

import os
import sys
import pytest
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import Database


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    db = Database(db_path)
    yield db
    
    # Cleanup
    try:
        os.unlink(db_path)
    except OSError:
        pass


class TestDatabaseInit:
    """Tests for database initialization."""
    
    def test_creates_database_file(self, temp_db):
        """Test that database file is created."""
        assert Path(temp_db.db_path).exists()
    
    def test_creates_table(self, temp_db):
        """Test that crossing_events table is created."""
        events = temp_db.get_events(limit=1)
        assert isinstance(events, list)


class TestLogEvent:
    """Tests for event logging."""
    
    def test_log_in_event(self, temp_db):
        """Test logging an IN event."""
        event_id = temp_db.log_event(direction="IN", occupancy=1)
        assert event_id is not None
        assert event_id > 0
    
    def test_log_out_event(self, temp_db):
        """Test logging an OUT event."""
        event_id = temp_db.log_event(direction="OUT", occupancy=0)
        assert event_id is not None
    
    def test_log_with_custom_timestamp(self, temp_db):
        """Test logging with custom timestamp."""
        custom_time = datetime(2025, 1, 1, 12, 0, 0)
        event_id = temp_db.log_event(
            direction="IN",
            occupancy=1,
            timestamp=custom_time
        )
        
        events = temp_db.get_events(limit=1)
        assert "2025-01-01" in events[0]["timestamp"]
    
    def test_invalid_direction_raises_error(self, temp_db):
        """Test that invalid direction raises ValueError."""
        with pytest.raises(ValueError):
            temp_db.log_event(direction="INVALID", occupancy=1)
    
    def test_log_multiple_events(self, temp_db):
        """Test logging multiple events."""
        for i in range(5):
            temp_db.log_event(direction="IN", occupancy=i + 1)
        
        events = temp_db.get_events(limit=10)
        assert len(events) == 5


class TestGetEvents:
    """Tests for event retrieval."""
    
    def test_get_events_empty_db(self, temp_db):
        """Test getting events from empty database."""
        events = temp_db.get_events(limit=10)
        assert events == []
    
    def test_get_events_with_limit(self, temp_db):
        """Test that limit is respected."""
        for i in range(10):
            temp_db.log_event(direction="IN", occupancy=i)
        
        events = temp_db.get_events(limit=5)
        assert len(events) == 5
    
    def test_get_events_ordered_desc(self, temp_db):
        """Test that events are ordered by timestamp descending."""
        temp_db.log_event(direction="IN", occupancy=1)
        temp_db.log_event(direction="OUT", occupancy=0)
        temp_db.log_event(direction="IN", occupancy=1)
        
        events = temp_db.get_events(limit=3)
        # Most recent should be first
        assert events[0]["direction"] == "IN"


class TestTotalCounts:
    """Tests for count aggregation."""
    
    def test_total_counts_empty_db(self, temp_db):
        """Test counts on empty database."""
        total_in, total_out = temp_db.get_total_counts()
        assert total_in == 0
        assert total_out == 0
    
    def test_total_counts_after_events(self, temp_db):
        """Test counts after logging events."""
        temp_db.log_event(direction="IN", occupancy=1)
        temp_db.log_event(direction="IN", occupancy=2)
        temp_db.log_event(direction="OUT", occupancy=1)
        
        total_in, total_out = temp_db.get_total_counts()
        assert total_in == 2
        assert total_out == 1


class TestOccupancy:
    """Tests for occupancy calculation."""
    
    def test_current_occupancy_empty(self, temp_db):
        """Test occupancy on empty database."""
        assert temp_db.get_current_occupancy() == 0
    
    def test_current_occupancy_positive(self, temp_db):
        """Test positive occupancy."""
        temp_db.log_event(direction="IN", occupancy=1)
        temp_db.log_event(direction="IN", occupancy=2)
        
        assert temp_db.get_current_occupancy() == 2
    
    def test_current_occupancy_never_negative(self, temp_db):
        """Test that occupancy never goes below 0."""
        temp_db.log_event(direction="OUT", occupancy=0)
        temp_db.log_event(direction="OUT", occupancy=0)
        
        assert temp_db.get_current_occupancy() == 0


class TestClearEvents:
    """Tests for clearing events."""
    
    def test_clear_events(self, temp_db):
        """Test clearing all events."""
        temp_db.log_event(direction="IN", occupancy=1)
        temp_db.log_event(direction="IN", occupancy=2)
        
        deleted = temp_db.clear_events()
        assert deleted == 2
        
        events = temp_db.get_events(limit=10)
        assert len(events) == 0
