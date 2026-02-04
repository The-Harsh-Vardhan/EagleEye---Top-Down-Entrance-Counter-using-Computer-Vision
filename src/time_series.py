"""
Time Series Analysis Module for EagleEye People Counting System.

Provides advanced analytics including:
- Trend analysis (hourly, daily, weekly patterns)
- Peak detection and anomaly identification
- Simple forecasting using moving averages
- Statistical summaries
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from .config import DATABASE_PATH


@dataclass
class TrafficStats:
    """Statistical summary for a time period."""
    period: str
    total_in: int
    total_out: int
    net_flow: int
    avg_occupancy: float
    max_occupancy: int
    min_occupancy: int
    peak_hour: str
    peak_count: int


@dataclass
class PeakPeriod:
    """Represents a detected peak period."""
    start_time: datetime
    end_time: datetime
    total_entries: int
    avg_rate: float  # entries per minute


@dataclass
class MealStats:
    """Statistics for a specific meal period."""
    meal_name: str
    start_time: str
    end_time: str
    total_entries: int
    total_exits: int
    avg_occupancy: float
    max_occupancy: int
    is_active: bool


# Meal time definitions (hour, minute) tuples
MEAL_TIMES = {
    'Breakfast': {'start': (7, 30), 'end': (9, 30), 'emoji': '🌅'},
    'Lunch': {'start': (12, 0), 'end': (14, 0), 'emoji': '☀️'},
    'Snacks': {'start': (17, 30), 'end': (18, 30), 'emoji': '🍪'},
    'Dinner': {'start': (19, 30), 'end': (21, 30), 'emoji': '🌙'},
}


class TimeSeriesAnalyzer:
    """
    Analyzes time series data from the EagleEye people counting system.
    
    Provides methods for trend analysis, peak detection, forecasting,
    and statistical summaries.
    """
    
    def __init__(self, db_path: str = DATABASE_PATH):
        """Initialize with database path."""
        self.db_path = db_path
    
    def _get_dataframe(self, start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Load events from database into a pandas DataFrame.
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            DataFrame with timestamp, direction, occupancy columns
        """
        conn = sqlite3.connect(self.db_path)
        
        query = "SELECT timestamp, direction, occupancy FROM crossing_events"
        conditions = []
        params = []
        
        if start_date:
            conditions.append("timestamp >= ?")
            params.append(start_date.isoformat())
        
        if end_date:
            conditions.append("timestamp <= ?")
            params.append(end_date.isoformat())
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY timestamp"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['date'] = df['timestamp'].dt.date
            df['day_of_week'] = df['timestamp'].dt.day_name()
            df['minute'] = df['timestamp'].dt.minute
        
        return df
    
    # ==================== TREND ANALYSIS ====================
    
    def get_hourly_trend(self, days: int = 7) -> pd.DataFrame:
        """
        Get hourly traffic trend aggregated over specified days.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            DataFrame with columns: hour, entries, exits, net_flow, avg_occupancy
        """
        start_date = datetime.now() - timedelta(days=days)
        df = self._get_dataframe(start_date=start_date)
        
        if df.empty:
            return pd.DataFrame(columns=['hour', 'entries', 'exits', 'net_flow', 'avg_occupancy'])
        
        # Aggregate by hour
        entries = df[df['direction'] == 'IN'].groupby('hour').size()
        exits = df[df['direction'] == 'OUT'].groupby('hour').size()
        avg_occ = df.groupby('hour')['occupancy'].mean()
        
        result = pd.DataFrame({
            'hour': range(24),
            'entries': [entries.get(h, 0) for h in range(24)],
            'exits': [exits.get(h, 0) for h in range(24)],
        })
        result['net_flow'] = result['entries'] - result['exits']
        result['avg_occupancy'] = [avg_occ.get(h, 0) for h in range(24)]
        
        return result
    
    def get_daily_trend(self, days: int = 30) -> pd.DataFrame:
        """
        Get daily traffic trend.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            DataFrame with columns: date, day_of_week, entries, exits, net_flow, max_occupancy
        """
        start_date = datetime.now() - timedelta(days=days)
        df = self._get_dataframe(start_date=start_date)
        
        if df.empty:
            return pd.DataFrame(columns=['date', 'day_of_week', 'entries', 'exits', 'net_flow', 'max_occupancy'])
        
        # Aggregate by date
        daily = df.groupby(['date', 'day_of_week']).agg({
            'direction': lambda x: (x == 'IN').sum(),
            'occupancy': 'max'
        }).reset_index()
        daily.columns = ['date', 'day_of_week', 'entries', 'max_occupancy']
        
        # Get exits separately
        exits = df[df['direction'] == 'OUT'].groupby('date').size()
        daily['exits'] = daily['date'].map(exits).fillna(0).astype(int)
        daily['net_flow'] = daily['entries'] - daily['exits']
        
        return daily
    
    def get_weekly_pattern(self, weeks: int = 4) -> pd.DataFrame:
        """
        Get average traffic pattern by day of week.
        
        Args:
            weeks: Number of weeks to analyze
            
        Returns:
            DataFrame with columns: day_of_week, avg_entries, avg_exits, avg_occupancy
        """
        start_date = datetime.now() - timedelta(weeks=weeks)
        df = self._get_dataframe(start_date=start_date)
        
        if df.empty:
            return pd.DataFrame(columns=['day_of_week', 'avg_entries', 'avg_exits', 'avg_occupancy'])
        
        # Days in order
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        # Count entries/exits per day
        entries_by_day = df[df['direction'] == 'IN'].groupby(['date', 'day_of_week']).size().reset_index(name='entries')
        exits_by_day = df[df['direction'] == 'OUT'].groupby(['date', 'day_of_week']).size().reset_index(name='exits')
        occ_by_day = df.groupby(['date', 'day_of_week'])['occupancy'].mean().reset_index(name='avg_occupancy')
        
        # Average per day of week
        result = entries_by_day.groupby('day_of_week')['entries'].mean().reset_index()
        result.columns = ['day_of_week', 'avg_entries']
        
        avg_exits = exits_by_day.groupby('day_of_week')['exits'].mean()
        avg_occ = occ_by_day.groupby('day_of_week')['avg_occupancy'].mean()
        
        result['avg_exits'] = result['day_of_week'].map(avg_exits).fillna(0)
        result['avg_occupancy'] = result['day_of_week'].map(avg_occ).fillna(0)
        
        # Sort by day order
        result['day_order'] = result['day_of_week'].map({d: i for i, d in enumerate(day_order)})
        result = result.sort_values('day_order').drop('day_order', axis=1).reset_index(drop=True)
        
        return result
    
    def get_moving_average(self, window_days: int = 7) -> pd.DataFrame:
        """
        Calculate moving average of daily traffic.
        
        Args:
            window_days: Window size in days
            
        Returns:
            DataFrame with date, entries, exits, ma_entries, ma_exits
        """
        daily = self.get_daily_trend(days=window_days * 5)  # Get enough data
        
        if daily.empty or len(daily) < window_days:
            return pd.DataFrame()
        
        daily['ma_entries'] = daily['entries'].rolling(window=window_days, min_periods=1).mean()
        daily['ma_exits'] = daily['exits'].rolling(window=window_days, min_periods=1).mean()
        
        return daily[['date', 'entries', 'exits', 'ma_entries', 'ma_exits']]
    
    # ==================== PEAK DETECTION ====================
    
    def detect_peak_hours(self, percentile: int = 75) -> List[int]:
        """
        Detect peak hours based on entry count percentile.
        
        Args:
            percentile: Threshold percentile for peak detection
            
        Returns:
            List of peak hours (0-23)
        """
        hourly = self.get_hourly_trend(days=30)
        
        if hourly.empty:
            return []
        
        threshold = np.percentile(hourly['entries'], percentile)
        peak_hours = hourly[hourly['entries'] >= threshold]['hour'].tolist()
        
        return sorted(peak_hours)
    
    def detect_anomalies(self, std_threshold: float = 2.0) -> pd.DataFrame:
        """
        Detect anomalous days with unusually high or low traffic.
        
        Args:
            std_threshold: Number of standard deviations for anomaly detection
            
        Returns:
            DataFrame with anomalous dates and their traffic
        """
        daily = self.get_daily_trend(days=90)
        
        if daily.empty or len(daily) < 7:
            return pd.DataFrame()
        
        mean_entries = daily['entries'].mean()
        std_entries = daily['entries'].std()
        
        upper = mean_entries + std_threshold * std_entries
        lower = mean_entries - std_threshold * std_entries
        
        anomalies = daily[(daily['entries'] > upper) | (daily['entries'] < lower)].copy()
        anomalies['anomaly_type'] = anomalies['entries'].apply(
            lambda x: 'HIGH' if x > upper else 'LOW'
        )
        anomalies['deviation'] = ((anomalies['entries'] - mean_entries) / std_entries).round(2)
        
        return anomalies[['date', 'day_of_week', 'entries', 'anomaly_type', 'deviation']]
    
    def get_peak_periods_today(self, min_gap_minutes: int = 30) -> List[PeakPeriod]:
        """
        Identify distinct peak periods from today's data.
        
        Args:
            min_gap_minutes: Minimum gap between separate peak periods
            
        Returns:
            List of PeakPeriod objects
        """
        today = datetime.now().date()
        df = self._get_dataframe(
            start_date=datetime.combine(today, datetime.min.time()),
            end_date=datetime.now()
        )
        
        if df.empty:
            return []
        
        entries = df[df['direction'] == 'IN'].copy()
        if entries.empty:
            return []
        
        # Resample to 5-minute buckets
        entries.set_index('timestamp', inplace=True)
        bucket_counts = entries.resample('5T').size()
        
        # Find high-traffic buckets (above median)
        median_rate = bucket_counts.median()
        if median_rate == 0:
            median_rate = 1
        
        high_traffic = bucket_counts[bucket_counts > median_rate]
        
        if high_traffic.empty:
            return []
        
        # Group into periods
        periods = []
        current_start = None
        current_end = None
        current_count = 0
        
        for time, count in high_traffic.items():
            if current_start is None:
                current_start = time
                current_end = time
                current_count = count
            elif (time - current_end).total_seconds() <= min_gap_minutes * 60:
                current_end = time
                current_count += count
            else:
                # Save current period and start new one
                duration = (current_end - current_start).total_seconds() / 60 + 5
                periods.append(PeakPeriod(
                    start_time=current_start.to_pydatetime(),
                    end_time=current_end.to_pydatetime(),
                    total_entries=int(current_count),
                    avg_rate=round(current_count / max(duration, 1), 2)
                ))
                current_start = time
                current_end = time
                current_count = count
        
        # Don't forget the last period
        if current_start is not None:
            duration = (current_end - current_start).total_seconds() / 60 + 5
            periods.append(PeakPeriod(
                start_time=current_start.to_pydatetime(),
                end_time=current_end.to_pydatetime(),
                total_entries=int(current_count),
                avg_rate=round(current_count / max(duration, 1), 2)
            ))
        
        return periods
    
    # ==================== FORECASTING ====================
    
    def forecast_next_hour(self) -> Dict[str, float]:
        """
        Predict traffic for the next hour using historical patterns.
        
        Returns:
            Dict with predicted_entries, predicted_exits, confidence
        """
        next_hour = (datetime.now().hour + 1) % 24
        hourly = self.get_hourly_trend(days=30)
        
        if hourly.empty:
            return {'predicted_entries': 0, 'predicted_exits': 0, 'confidence': 0}
        
        # Get historical data for this hour
        hour_data = hourly[hourly['hour'] == next_hour]
        
        if hour_data.empty:
            return {'predicted_entries': 0, 'predicted_exits': 0, 'confidence': 0}
        
        # Use average as prediction
        predicted_entries = hour_data['entries'].mean()
        predicted_exits = hour_data['exits'].mean()
        
        # Confidence based on data availability
        confidence = min(1.0, len(hourly) / 168)  # Full week = 100% confidence
        
        return {
            'predicted_entries': round(predicted_entries, 1),
            'predicted_exits': round(predicted_exits, 1),
            'confidence': round(confidence, 2)
        }
    
    def forecast_day(self, target_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Predict hourly traffic for a specific day.
        
        Args:
            target_date: Date to forecast (defaults to tomorrow)
            
        Returns:
            DataFrame with hour, predicted_entries, predicted_exits
        """
        if target_date is None:
            target_date = datetime.now() + timedelta(days=1)
        
        target_dow = target_date.strftime('%A')
        
        # Get historical data for this day of week
        start_date = datetime.now() - timedelta(days=90)
        df = self._get_dataframe(start_date=start_date)
        
        if df.empty:
            return pd.DataFrame()
        
        # Filter for same day of week
        dow_data = df[df['day_of_week'] == target_dow]
        
        if dow_data.empty:
            # Fall back to all data
            dow_data = df
        
        # Aggregate by hour
        entries = dow_data[dow_data['direction'] == 'IN'].groupby('hour').size()
        exits = dow_data[dow_data['direction'] == 'OUT'].groupby('hour').size()
        
        # Normalize by number of unique dates
        n_dates = dow_data['date'].nunique()
        
        result = pd.DataFrame({
            'hour': range(24),
            'predicted_entries': [round(entries.get(h, 0) / max(n_dates, 1), 1) for h in range(24)],
            'predicted_exits': [round(exits.get(h, 0) / max(n_dates, 1), 1) for h in range(24)]
        })
        
        return result
    
    # ==================== STATISTICAL SUMMARIES ====================
    
    def get_statistics(self, days: int = 7) -> TrafficStats:
        """
        Get comprehensive statistics for the specified period.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            TrafficStats object with all statistics
        """
        start_date = datetime.now() - timedelta(days=days)
        df = self._get_dataframe(start_date=start_date)
        
        if df.empty:
            return TrafficStats(
                period=f"Last {days} days",
                total_in=0, total_out=0, net_flow=0,
                avg_occupancy=0, max_occupancy=0, min_occupancy=0,
                peak_hour="N/A", peak_count=0
            )
        
        total_in = (df['direction'] == 'IN').sum()
        total_out = (df['direction'] == 'OUT').sum()
        
        # Find peak hour
        entries_by_hour = df[df['direction'] == 'IN'].groupby('hour').size()
        if not entries_by_hour.empty:
            peak_hour_num = entries_by_hour.idxmax()
            peak_hour = f"{peak_hour_num:02d}:00"
            peak_count = entries_by_hour.max()
        else:
            peak_hour = "N/A"
            peak_count = 0
        
        return TrafficStats(
            period=f"Last {days} days",
            total_in=int(total_in),
            total_out=int(total_out),
            net_flow=int(total_in - total_out),
            avg_occupancy=round(df['occupancy'].mean(), 1),
            max_occupancy=int(df['occupancy'].max()),
            min_occupancy=int(df['occupancy'].min()),
            peak_hour=peak_hour,
            peak_count=int(peak_count)
        )
    
    def get_percentile_stats(self, days: int = 30) -> Dict[str, float]:
        """
        Get percentile-based statistics.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict with various percentile values
        """
        start_date = datetime.now() - timedelta(days=days)
        df = self._get_dataframe(start_date=start_date)
        
        if df.empty:
            return {}
        
        occupancy = df['occupancy']
        
        return {
            'p25_occupancy': float(np.percentile(occupancy, 25)),
            'p50_occupancy': float(np.percentile(occupancy, 50)),
            'p75_occupancy': float(np.percentile(occupancy, 75)),
            'p90_occupancy': float(np.percentile(occupancy, 90)),
            'p95_occupancy': float(np.percentile(occupancy, 95)),
            'std_occupancy': float(occupancy.std()),
        }
    
    def get_hourly_heatmap_data(self, weeks: int = 4) -> pd.DataFrame:
        """
        Get data for hour x day-of-week heatmap.
        
        Args:
            weeks: Number of weeks to analyze
            
        Returns:
            Pivot table with hours as rows, days as columns, entries as values
        """
        start_date = datetime.now() - timedelta(weeks=weeks)
        df = self._get_dataframe(start_date=start_date)
        
        if df.empty:
            return pd.DataFrame()
        
        # Count entries per hour and day of week
        entries = df[df['direction'] == 'IN'].copy()
        entries['count'] = 1
        
        heatmap = entries.groupby(['hour', 'day_of_week']).size().reset_index(name='entries')
        
        # Pivot for heatmap
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        pivot = heatmap.pivot(index='hour', columns='day_of_week', values='entries').fillna(0)
        
        # Reorder columns
        pivot = pivot.reindex(columns=[d for d in day_order if d in pivot.columns])
        
        return pivot
    
    # ==================== EXPORT ====================
    
    def export_to_csv(self, filepath: str, start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None) -> int:
        """
        Export events to CSV file.
        
        Args:
            filepath: Output file path
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Number of records exported
        """
        df = self._get_dataframe(start_date=start_date, end_date=end_date)
        
        if df.empty:
            return 0
        
        df.to_csv(filepath, index=False)
        return len(df)
    
    # ==================== MEAL TIME ANALYSIS ====================
    
    def _is_in_meal_period(self, timestamp: datetime, meal_name: str) -> bool:
        """Check if a timestamp falls within a meal period."""
        meal = MEAL_TIMES.get(meal_name)
        if not meal:
            return False
        
        start_h, start_m = meal['start']
        end_h, end_m = meal['end']
        
        time_minutes = timestamp.hour * 60 + timestamp.minute
        start_minutes = start_h * 60 + start_m
        end_minutes = end_h * 60 + end_m
        
        return start_minutes <= time_minutes <= end_minutes
    
    def _get_current_meal(self) -> Optional[str]:
        """Get the name of the current meal period, if any."""
        now = datetime.now()
        for meal_name in MEAL_TIMES:
            if self._is_in_meal_period(now, meal_name):
                return meal_name
        return None
    
    def get_meal_stats(self, meal_name: str, days: int = 7) -> MealStats:
        """
        Get statistics for a specific meal period.
        
        Args:
            meal_name: Name of the meal (Breakfast, Lunch, Snacks, Dinner)
            days: Number of days to analyze
            
        Returns:
            MealStats object with meal-specific statistics
        """
        meal = MEAL_TIMES.get(meal_name)
        if not meal:
            return MealStats(
                meal_name=meal_name,
                start_time="N/A",
                end_time="N/A",
                total_entries=0,
                total_exits=0,
                avg_occupancy=0,
                max_occupancy=0,
                is_active=False
            )
        
        start_h, start_m = meal['start']
        end_h, end_m = meal['end']
        
        start_date = datetime.now() - timedelta(days=days)
        df = self._get_dataframe(start_date=start_date)
        
        if df.empty:
            return MealStats(
                meal_name=meal_name,
                start_time=f"{start_h:02d}:{start_m:02d}",
                end_time=f"{end_h:02d}:{end_m:02d}",
                total_entries=0,
                total_exits=0,
                avg_occupancy=0,
                max_occupancy=0,
                is_active=self._is_in_meal_period(datetime.now(), meal_name)
            )
        
        # Filter for meal time hours
        df['time_minutes'] = df['hour'] * 60 + df['minute']
        start_minutes = start_h * 60 + start_m
        end_minutes = end_h * 60 + end_m
        
        meal_df = df[(df['time_minutes'] >= start_minutes) & (df['time_minutes'] <= end_minutes)]
        
        if meal_df.empty:
            return MealStats(
                meal_name=meal_name,
                start_time=f"{start_h:02d}:{start_m:02d}",
                end_time=f"{end_h:02d}:{end_m:02d}",
                total_entries=0,
                total_exits=0,
                avg_occupancy=0,
                max_occupancy=0,
                is_active=self._is_in_meal_period(datetime.now(), meal_name)
            )
        
        total_entries = (meal_df['direction'] == 'IN').sum()
        total_exits = (meal_df['direction'] == 'OUT').sum()
        
        return MealStats(
            meal_name=meal_name,
            start_time=f"{start_h:02d}:{start_m:02d}",
            end_time=f"{end_h:02d}:{end_m:02d}",
            total_entries=int(total_entries),
            total_exits=int(total_exits),
            avg_occupancy=round(meal_df['occupancy'].mean(), 1),
            max_occupancy=int(meal_df['occupancy'].max()),
            is_active=self._is_in_meal_period(datetime.now(), meal_name)
        )
    
    def get_all_meals_stats(self, days: int = 7) -> Dict[str, MealStats]:
        """
        Get statistics for all meal periods.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict mapping meal names to MealStats objects
        """
        return {
            meal_name: self.get_meal_stats(meal_name, days)
            for meal_name in MEAL_TIMES
        }
    
    def get_meal_comparison(self, days: int = 7) -> pd.DataFrame:
        """
        Get a comparison table of all meal periods.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            DataFrame with meal comparison data
        """
        all_stats = self.get_all_meals_stats(days)
        
        data = []
        for meal_name, stats in all_stats.items():
            emoji = MEAL_TIMES[meal_name]['emoji']
            data.append({
                'Meal': f"{emoji} {meal_name}",
                'Time': f"{stats.start_time} - {stats.end_time}",
                'Entries': stats.total_entries,
                'Exits': stats.total_exits,
                'Avg Occupancy': stats.avg_occupancy,
                'Max Occupancy': stats.max_occupancy,
                'Status': '🟢 Active' if stats.is_active else '⚪ Inactive'
            })
        
        return pd.DataFrame(data)
    
    def get_meal_hourly_breakdown(self, meal_name: str, days: int = 7) -> pd.DataFrame:
        """
        Get hourly breakdown within a meal period.
        
        Args:
            meal_name: Name of the meal
            days: Number of days to analyze
            
        Returns:
            DataFrame with hourly entries/exits within the meal period
        """
        meal = MEAL_TIMES.get(meal_name)
        if not meal:
            return pd.DataFrame()
        
        start_h, start_m = meal['start']
        end_h, end_m = meal['end']
        
        start_date = datetime.now() - timedelta(days=days)
        df = self._get_dataframe(start_date=start_date)
        
        if df.empty:
            return pd.DataFrame()
        
        # Filter for meal time hours (using full hours that overlap with meal)
        meal_hours = list(range(start_h, end_h + 1))
        meal_df = df[df['hour'].isin(meal_hours)]
        
        if meal_df.empty:
            return pd.DataFrame()
        
        # Aggregate by hour
        entries = meal_df[meal_df['direction'] == 'IN'].groupby('hour').size()
        exits = meal_df[meal_df['direction'] == 'OUT'].groupby('hour').size()
        avg_occ = meal_df.groupby('hour')['occupancy'].mean()
        
        result = pd.DataFrame({
            'hour': meal_hours,
            'time': [f"{h:02d}:00" for h in meal_hours],
            'entries': [entries.get(h, 0) for h in meal_hours],
            'exits': [exits.get(h, 0) for h in meal_hours],
            'avg_occupancy': [round(avg_occ.get(h, 0), 1) for h in meal_hours]
        })
        
        return result
    
    def get_busiest_meal(self, days: int = 7) -> Tuple[str, MealStats]:
        """
        Find the busiest meal period by total entries.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Tuple of (meal_name, MealStats)
        """
        all_stats = self.get_all_meals_stats(days)
        
        if not all_stats:
            return ('None', MealStats('None', 'N/A', 'N/A', 0, 0, 0, 0, False))
        
        busiest = max(all_stats.items(), key=lambda x: x[1].total_entries)
        return busiest
    
    def get_meal_trends(self, weeks: int = 4) -> pd.DataFrame:
        """
        Get daily trends for each meal over multiple weeks.
        
        Args:
            weeks: Number of weeks to analyze
            
        Returns:
            DataFrame with date, meal, entries columns
        """
        start_date = datetime.now() - timedelta(weeks=weeks)
        df = self._get_dataframe(start_date=start_date)
        
        if df.empty:
            return pd.DataFrame()
        
        df['time_minutes'] = df['hour'] * 60 + df['minute']
        
        results = []
        
        for meal_name, meal in MEAL_TIMES.items():
            start_h, start_m = meal['start']
            end_h, end_m = meal['end']
            start_minutes = start_h * 60 + start_m
            end_minutes = end_h * 60 + end_m
            
            meal_df = df[(df['time_minutes'] >= start_minutes) & (df['time_minutes'] <= end_minutes)]
            
            if not meal_df.empty:
                daily_entries = meal_df[meal_df['direction'] == 'IN'].groupby('date').size()
                
                for date, entries in daily_entries.items():
                    results.append({
                        'date': date,
                        'meal': meal_name,
                        'entries': entries
                    })
        
        return pd.DataFrame(results)

