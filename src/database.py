"""
Database module for EagleEye People Counting System.

Handles SQLite operations for storing and retrieving crossing events.
Each event records when a person crosses the counting line, the direction
(IN or OUT), and the current occupancy at that moment.
"""

import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional
from contextlib import contextmanager

from .config import DATABASE_PATH


class Database:
    """
    SQLite database handler for crossing events.
    
    Provides thread-safe database operations for logging IN/OUT events
    and retrieving statistics.
    """
    
    def __init__(self, db_path: str = DATABASE_PATH):
        """
        Initialize the database connection.
        
        Args:
            db_path: Path to the SQLite database file. 
                     Creates the file if it doesn't exist.
        """
        self.db_path = db_path
        self._init_db()
    
    @contextmanager
    def _get_connection(self):
        """
        Context manager for database connections.
        
        Ensures connections are properly closed after use and
        handles commit/rollback automatically.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_db(self) -> None:
        """
        Initialize the database schema.
        
        Creates the crossing_events table if it doesn't exist.
        Safe to call multiple times.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS crossing_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    direction TEXT NOT NULL CHECK(direction IN ('IN', 'OUT')),
                    occupancy INTEGER NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create index for faster timestamp queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON crossing_events(timestamp)
            ''')
    
    def log_event(self, direction: str, occupancy: int, 
                  timestamp: Optional[datetime] = None) -> int:
        """
        Log a crossing event to the database.
        
        Args:
            direction: 'IN' or 'OUT'
            occupancy: Current occupancy count after this event
            timestamp: Event timestamp (defaults to current time)
        
        Returns:
            The ID of the inserted event record
        
        Raises:
            ValueError: If direction is not 'IN' or 'OUT'
        """
        if direction not in ('IN', 'OUT'):
            raise ValueError(f"Direction must be 'IN' or 'OUT', got: {direction}")
        
        if timestamp is None:
            timestamp = datetime.now()
        
        timestamp_str = timestamp.isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO crossing_events (timestamp, direction, occupancy)
                VALUES (?, ?, ?)
            ''', (timestamp_str, direction, occupancy))
            return cursor.lastrowid
    
    def get_events(self, limit: int = 100, 
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None) -> List[dict]:
        """
        Retrieve crossing events from the database.
        
        Args:
            limit: Maximum number of events to return
            start_time: Filter events after this timestamp
            end_time: Filter events before this timestamp
        
        Returns:
            List of event dictionaries with keys: id, timestamp, direction, occupancy
        """
        query = 'SELECT id, timestamp, direction, occupancy FROM crossing_events'
        params = []
        conditions = []
        
        if start_time:
            conditions.append('timestamp >= ?')
            params.append(start_time.isoformat())
        
        if end_time:
            conditions.append('timestamp <= ?')
            params.append(end_time.isoformat())
        
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        
        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_total_counts(self) -> Tuple[int, int]:
        """
        Get total IN and OUT counts from all recorded events.
        
        Returns:
            Tuple of (total_in, total_out)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    COALESCE(SUM(CASE WHEN direction = 'IN' THEN 1 ELSE 0 END), 0) as total_in,
                    COALESCE(SUM(CASE WHEN direction = 'OUT' THEN 1 ELSE 0 END), 0) as total_out
                FROM crossing_events
            ''')
            
            row = cursor.fetchone()
            return (row['total_in'], row['total_out'])
    
    def get_current_occupancy(self) -> int:
        """
        Calculate current occupancy based on all events.
        
        Returns:
            Current occupancy (total IN - total OUT, minimum 0)
        """
        total_in, total_out = self.get_total_counts()
        return max(0, total_in - total_out)
    
    def clear_events(self) -> int:
        """
        Delete all events from the database.
        
        Returns:
            Number of deleted records
        
        Warning:
            This operation cannot be undone!
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM crossing_events')
            return cursor.rowcount
