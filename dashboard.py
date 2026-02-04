"""
EagleEye Streamlit Dashboard
Real-time monitoring and analytics for people counting system
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import time
import random
import sys
sys.path.insert(0, '.')

# Import time series analyzer
try:
    from src.time_series import TimeSeriesAnalyzer
    TIME_SERIES_AVAILABLE = True
except ImportError:
    TIME_SERIES_AVAILABLE = False


def generate_demo_data():
    """Generate impressive demo statistics for showcase"""
    now = datetime.now()
    
    # Generate realistic cafeteria traffic patterns
    demo_stats = {
        "current_occupancy": random.randint(45, 85),
        "max_capacity": 150,
        "total_in": random.randint(2500, 3500),
        "total_out": random.randint(2400, 3400),
        "today_in": random.randint(180, 280),
        "today_out": random.randint(160, 260),
        "avg_dwell_time": random.randint(18, 28),  # minutes
        "peak_hour": "12:30 PM",
        "busiest_day": "Tuesday",
        "weekly_visitors": random.randint(12000, 18000),
        "monthly_visitors": random.randint(48000, 65000),
        "accuracy": 98.7,
        "uptime": 99.2,
    }
    
    # Generate hourly data for today
    hours = list(range(7, 21))  # 7 AM to 8 PM
    hourly_data = []
    for hour in hours:
        # Simulate meal rush patterns
        if hour in [8, 9]:  # Breakfast
            entries = random.randint(40, 80)
        elif hour in [12, 13]:  # Lunch rush
            entries = random.randint(120, 200)
        elif hour in [18, 19]:  # Dinner
            entries = random.randint(100, 160)
        else:
            entries = random.randint(15, 50)
        
        exits = int(entries * random.uniform(0.8, 1.1))
        hourly_data.append({
            'hour': f"{hour:02d}:00",
            'entries': entries,
            'exits': exits
        })
    
    # Generate weekly data
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekly_data = []
    for i, day in enumerate(days):
        date = now - timedelta(days=6-i)
        if day in ['Saturday', 'Sunday']:
            total = random.randint(800, 1200)
        else:
            total = random.randint(2000, 3000)
        weekly_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'day': day,
            'visitors': total
        })
    
    # Generate recent events
    recent_events = []
    for i in range(15):
        event_time = now - timedelta(minutes=i*2)
        direction = random.choice(['IN', 'IN', 'IN', 'OUT', 'OUT'])  # Slight bias to IN
        occupancy = demo_stats["current_occupancy"] + random.randint(-5, 5)
        recent_events.append({
            'timestamp': event_time,
            'direction': direction,
            'occupancy': max(0, occupancy)
        })
    
    # Generate heatmap data
    heatmap_data = []
    for day_offset in range(7):
        date = now - timedelta(days=day_offset)
        for hour in range(7, 21):
            if hour in [12, 13]:
                occupancy = random.randint(60, 95)
            elif hour in [8, 9, 18, 19]:
                occupancy = random.randint(40, 70)
            else:
                occupancy = random.randint(10, 40)
            heatmap_data.append({
                'date': date.date(),
                'hour': hour,
                'occupancy': occupancy
            })
    
    return demo_stats, hourly_data, weekly_data, recent_events, heatmap_data

# Page configuration
st.set_page_config(
    page_title="EagleEye Dashboard",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Database connection
@st.cache_resource
def get_database_connection():
    """Create database connection"""
    db_path = Path("eagle_eye.db")
    if not db_path.exists():
        st.warning("Database not found. Run the system first to generate data.")
        return None
    return sqlite3.connect(str(db_path), check_same_thread=False)

def load_data(hours=24):
    """Load crossing events from database"""
    conn = get_database_connection()
    if conn is None:
        return pd.DataFrame()
    
    query = f"""
    SELECT 
        timestamp,
        direction,
        occupancy
    FROM crossing_events
    WHERE datetime(timestamp) >= datetime('now', '-{hours} hours')
    ORDER BY timestamp DESC
    """
    
    df = pd.read_sql_query(query, conn)
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def get_current_stats():
    """Get current statistics"""
    conn = get_database_connection()
    if conn is None:
        return {"in": 0, "out": 0, "occupancy": 0}
    
    cursor = conn.cursor()
    
    # Get total counts
    cursor.execute("SELECT COUNT(*) FROM crossing_events WHERE direction = 'IN'")
    total_in = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT COUNT(*) FROM crossing_events WHERE direction = 'OUT'")
    total_out = cursor.fetchone()[0] or 0
    
    # Get current occupancy (latest record)
    cursor.execute("SELECT occupancy FROM crossing_events ORDER BY timestamp DESC LIMIT 1")
    result = cursor.fetchone()
    occupancy = result[0] if result else 0
    
    return {
        "in": total_in,
        "out": total_out,
        "occupancy": occupancy
    }

def get_today_stats():
    """Get today's statistics"""
    conn = get_database_connection()
    if conn is None:
        return {"in": 0, "out": 0}
    
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) FROM crossing_events 
        WHERE direction = 'IN' AND date(timestamp) = date('now')
    """)
    today_in = cursor.fetchone()[0] or 0
    
    cursor.execute("""
        SELECT COUNT(*) FROM crossing_events 
        WHERE direction = 'OUT' AND date(timestamp) = date('now')
    """)
    today_out = cursor.fetchone()[0] or 0
    
    return {"in": today_in, "out": today_out}

def get_hourly_data(days=7):
    """Get hourly traffic data"""
    conn = get_database_connection()
    if conn is None:
        return pd.DataFrame()
    
    query = f"""
    SELECT 
        strftime('%Y-%m-%d', timestamp) as date,
        strftime('%H:00', timestamp) as hour,
        direction,
        COUNT(*) as count
    FROM crossing_events
    WHERE datetime(timestamp) >= datetime('now', '-{days} days')
    GROUP BY date, hour, direction
    ORDER BY date, hour
    """
    
    df = pd.read_sql_query(query, conn)
    return df

def get_peak_hours():
    """Get peak hours analysis"""
    conn = get_database_connection()
    if conn is None:
        return pd.DataFrame()
    
    query = """
    SELECT 
        strftime('%H:00', timestamp) as hour,
        SUM(CASE WHEN direction = 'IN' THEN 1 ELSE 0 END) as entries,
        SUM(CASE WHEN direction = 'OUT' THEN 1 ELSE 0 END) as exits
    FROM crossing_events
    WHERE date(timestamp) = date('now')
    GROUP BY hour
    ORDER BY entries DESC
    """
    
    df = pd.read_sql_query(query, conn)
    return df

# Main app
def main():
    # Header
    st.markdown('<h1 class="main-header">🦅 EagleEye Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("**Real-time People Counting & Analytics**")
    st.markdown("---")
    
    # Sidebar
    st.sidebar.header("⚙️ Settings")
    
    # DEMO MODE - Prominent toggle
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎯 Demo Mode")
    demo_mode = st.sidebar.toggle("Enable Demo Mode", value=False, help="Show impressive sample statistics")
    
    if demo_mode:
        st.sidebar.success("✨ Demo Mode Active!")
        demo_stats, hourly_data, weekly_data, recent_events, heatmap_data = generate_demo_data()
        
        # Show key demo stats in sidebar
        st.sidebar.markdown("---")
        st.sidebar.markdown("#### 📊 Quick Stats")
        st.sidebar.metric("🎯 Accuracy", f"{demo_stats['accuracy']}%")
        st.sidebar.metric("⏱️ Uptime", f"{demo_stats['uptime']}%")
        st.sidebar.metric("👥 Monthly Visitors", f"{demo_stats['monthly_visitors']:,}")
    
    st.sidebar.markdown("---")
    
    # Time range selector
    time_range = st.sidebar.selectbox(
        "Time Range",
        ["Last Hour", "Last 6 Hours", "Last 24 Hours", "Last 7 Days", "Last 30 Days"],
        index=2
    )
    
    hours_map = {
        "Last Hour": 1,
        "Last 6 Hours": 6,
        "Last 24 Hours": 24,
        "Last 7 Days": 168,
        "Last 30 Days": 720
    }
    hours = hours_map[time_range]
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("Auto Refresh (30s)", value=False)
    
    if auto_refresh:
        st.sidebar.info("Dashboard will refresh every 30 seconds")
        time.sleep(30)
        st.rerun()
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Now"):
        st.rerun()
    
    # Main content tabs
    if demo_mode:
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Overview", "📈 Analytics", "📉 Time Series", "🏆 Insights", "🕐 Historical", "⚙️ System"])
    else:
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "📈 Analytics", "📉 Time Series", "🕐 Historical", "⚙️ System"])
    
    # TAB 1: Overview
    with tab1:
        if demo_mode:
            # DEMO MODE - Impressive Statistics
            st.markdown("### 🎯 Live Monitoring Dashboard")
            
            # Big impressive numbers
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric(
                    label="🟢 Current Occupancy",
                    value=demo_stats["current_occupancy"],
                    delta=f"{demo_stats['current_occupancy']*100//demo_stats['max_capacity']}% capacity"
                )
            
            with col2:
                st.metric(
                    label="⬆️ Total IN",
                    value=f"{demo_stats['total_in']:,}",
                    delta=f"+{demo_stats['today_in']} today"
                )
            
            with col3:
                st.metric(
                    label="⬇️ Total OUT",
                    value=f"{demo_stats['total_out']:,}",
                    delta=f"+{demo_stats['today_out']} today"
                )
            
            with col4:
                st.metric(
                    label="⏱️ Avg Dwell Time",
                    value=f"{demo_stats['avg_dwell_time']} min",
                    delta="optimal"
                )
            
            with col5:
                st.metric(
                    label="🔥 Peak Hour",
                    value=demo_stats["peak_hour"],
                    delta="lunch rush"
                )
            
            st.markdown("---")
            
            # Traffic chart
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("📈 Today's Traffic Flow")
                hourly_df = pd.DataFrame(hourly_data)
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=hourly_df['hour'],
                    y=hourly_df['entries'],
                    name='Entries',
                    marker_color='#00C853'
                ))
                fig.add_trace(go.Bar(
                    x=hourly_df['hour'],
                    y=hourly_df['exits'],
                    name='Exits',
                    marker_color='#FF5252'
                ))
                
                fig.update_layout(
                    barmode='group',
                    height=350,
                    xaxis_title="Hour",
                    yaxis_title="Count",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02),
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("📋 Recent Events")
                events_df = pd.DataFrame(recent_events)
                events_df['Time'] = events_df['timestamp'].dt.strftime('%H:%M:%S')
                events_df['Direction'] = events_df['direction'].apply(
                    lambda x: "⬆️ IN" if x == "IN" else "⬇️ OUT"
                )
                display_df = events_df[['Time', 'Direction', 'occupancy']].head(10)
                display_df.columns = ['Time', 'Direction', 'Occupancy']
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Weekly trend
            st.subheader("📊 Weekly Visitors")
            weekly_df = pd.DataFrame(weekly_data)
            
            fig = px.bar(
                weekly_df,
                x='day',
                y='visitors',
                color='visitors',
                color_continuous_scale='Viridis',
                title=""
            )
            fig.update_layout(
                height=300,
                xaxis_title="",
                yaxis_title="Visitors",
                showlegend=False,
                coloraxis_showscale=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            # Normal mode - use database
            stats = get_current_stats()
            today_stats = get_today_stats()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="🟢 Current Occupancy",
                    value=stats["occupancy"],
                    delta=None
                )
            
            with col2:
                st.metric(
                    label="⬆️ Total IN",
                    value=stats["in"],
                    delta=f"+{today_stats['in']} today"
                )
            
            with col3:
                st.metric(
                    label="⬇️ Total OUT",
                    value=stats["out"],
                    delta=f"+{today_stats['out']} today"
                )
            
            with col4:
                net_today = today_stats['in'] - today_stats['out']
                st.metric(
                    label="📊 Today's Net",
                    value=net_today,
                    delta=None
                )
        
        st.markdown("---")
        
        # Recent activity
        st.subheader("📋 Recent Activity")
        df_recent = load_data(hours=1)
        
        if not df_recent.empty:
            # Display recent events
            df_display = df_recent.head(10).copy()
            df_display['Time'] = df_display['timestamp'].dt.strftime('%H:%M:%S')
            df_display['Direction'] = df_display['direction'].apply(
                lambda x: "⬆️ IN" if x == "IN" else "⬇️ OUT"
            )
            df_display = df_display[['Time', 'Direction', 'occupancy']]
            df_display.columns = ['Time', 'Direction', 'Occupancy']
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.info("No recent activity. Start the counting system to see data.")
        
        # Real-time chart
        st.subheader("📈 Traffic Over Time")
        df_chart = load_data(hours=hours)
        
        if not df_chart.empty:
            # Resample by 10-minute intervals
            df_chart.set_index('timestamp', inplace=True)
            df_in = df_chart[df_chart['direction'] == 'IN'].resample('10T').size()
            df_out = df_chart[df_chart['direction'] == 'OUT'].resample('10T').size()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_in.index,
                y=df_in.values,
                name='IN',
                mode='lines+markers',
                line=dict(color='green', width=2),
                fill='tozeroy'
            ))
            fig.add_trace(go.Scatter(
                x=df_out.index,
                y=df_out.values,
                name='OUT',
                mode='lines+markers',
                line=dict(color='red', width=2),
                fill='tozeroy'
            ))
            
            fig.update_layout(
                title=f"Traffic Flow ({time_range})",
                xaxis_title="Time",
                yaxis_title="Count per 10 min",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for the selected time range.")
    
    # TAB 2: Analytics
    with tab2:
        st.subheader("📊 Detailed Analytics")
        
        # Peak hours analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🔥 Peak Hours Today")
            peak_df = get_peak_hours()
            
            if not peak_df.empty:
                fig = px.bar(
                    peak_df,
                    x='hour',
                    y=['entries', 'exits'],
                    title="Hourly Traffic Distribution",
                    labels={'value': 'Count', 'hour': 'Hour'},
                    barmode='group',
                    color_discrete_map={'entries': 'green', 'exits': 'red'}
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Show top 3 peak hours
                top_hours = peak_df.nlargest(3, 'entries')
                st.write("**Top 3 Busiest Hours:**")
                for idx, row in top_hours.iterrows():
                    st.write(f"• {row['hour']} - {row['entries']} entries")
            else:
                st.info("No data for today yet.")
        
        with col2:
            st.markdown("### 📈 Weekly Trend")
            weekly_df = get_hourly_data(days=7)
            
            if not weekly_df.empty:
                # Aggregate by date
                daily = weekly_df.groupby(['date', 'direction'])['count'].sum().reset_index()
                daily_pivot = daily.pivot(index='date', columns='direction', values='count').fillna(0)
                
                fig = go.Figure()
                if 'IN' in daily_pivot.columns:
                    fig.add_trace(go.Bar(
                        x=daily_pivot.index,
                        y=daily_pivot['IN'],
                        name='IN',
                        marker_color='green'
                    ))
                if 'OUT' in daily_pivot.columns:
                    fig.add_trace(go.Bar(
                        x=daily_pivot.index,
                        y=daily_pivot['OUT'],
                        name='OUT',
                        marker_color='red'
                    ))
                
                fig.update_layout(
                    title="Daily Traffic (Last 7 Days)",
                    xaxis_title="Date",
                    yaxis_title="Count",
                    barmode='group'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Not enough data for weekly trend.")
        
        # Occupancy heatmap
        st.markdown("### 🗺️ Occupancy Heatmap")
        df_occupancy = load_data(hours=168)  # Last 7 days
        
        if not df_occupancy.empty:
            # Create hourly occupancy matrix
            df_occupancy['date'] = df_occupancy['timestamp'].dt.date
            df_occupancy['hour'] = df_occupancy['timestamp'].dt.hour
            
            heatmap_data = df_occupancy.groupby(['date', 'hour'])['occupancy'].mean().reset_index()
            heatmap_pivot = heatmap_data.pivot(index='hour', columns='date', values='occupancy')
            
            fig = px.imshow(
                heatmap_pivot,
                labels=dict(x="Date", y="Hour", color="Avg Occupancy"),
                x=heatmap_pivot.columns.astype(str),
                y=heatmap_pivot.index,
                color_continuous_scale='RdYlGn_r',
                title="Average Occupancy by Hour and Date"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough data for heatmap.")
    
    # TAB 3: Time Series Analysis (both modes)
    with tab3:
        st.subheader("📉 Time Series Analysis")
        
        if not TIME_SERIES_AVAILABLE:
            st.warning("⚠️ Time Series module not available. Please check the installation.")
        else:
            analyzer = TimeSeriesAnalyzer()
            
            # Analysis period selector
            analysis_period = st.selectbox(
                "Analysis Period",
                ["Last 7 Days", "Last 14 Days", "Last 30 Days", "Last 90 Days"],
                index=0
            )
            period_days = {"Last 7 Days": 7, "Last 14 Days": 14, "Last 30 Days": 30, "Last 90 Days": 90}
            days = period_days[analysis_period]
            
            # Statistics Summary
            st.markdown("### 📊 Statistical Summary")
            stats = analyzer.get_statistics(days=days)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total IN", stats.total_in)
            with col2:
                st.metric("Total OUT", stats.total_out)
            with col3:
                st.metric("Net Flow", stats.net_flow, delta=None)
            with col4:
                st.metric("Peak Hour", stats.peak_hour)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Avg Occupancy", f"{stats.avg_occupancy:.1f}")
            with col2:
                st.metric("Max Occupancy", stats.max_occupancy)
            with col3:
                st.metric("Min Occupancy", stats.min_occupancy)
            with col4:
                st.metric("Peak Count", stats.peak_count)
            
            st.markdown("---")
            
            # Hourly Trend Chart
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📈 Hourly Traffic Pattern")
                hourly = analyzer.get_hourly_trend(days=days)
                
                if not hourly.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=hourly['hour'],
                        y=hourly['entries'],
                        name='Entries',
                        marker_color='#00C853'
                    ))
                    fig.add_trace(go.Bar(
                        x=hourly['hour'],
                        y=hourly['exits'],
                        name='Exits',
                        marker_color='#FF5252'
                    ))
                    fig.update_layout(
                        barmode='group',
                        height=350,
                        xaxis_title="Hour of Day",
                        yaxis_title="Count",
                        xaxis=dict(tickmode='linear', tick0=0, dtick=2)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No hourly data available.")
            
            with col2:
                st.markdown("### 📊 Weekly Pattern")
                weekly = analyzer.get_weekly_pattern(weeks=4)
                
                if not weekly.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=weekly['day_of_week'],
                        y=weekly['avg_entries'],
                        name='Avg Entries',
                        marker_color='#2196F3'
                    ))
                    fig.add_trace(go.Bar(
                        x=weekly['day_of_week'],
                        y=weekly['avg_exits'],
                        name='Avg Exits',
                        marker_color='#FF9800'
                    ))
                    fig.update_layout(
                        barmode='group',
                        height=350,
                        xaxis_title="Day of Week",
                        yaxis_title="Average Count"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No weekly data available.")
            
            st.markdown("---")
            
            # Heatmap and Moving Average
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🗺️ Hour × Day Heatmap")
                heatmap = analyzer.get_hourly_heatmap_data(weeks=4)
                
                if not heatmap.empty:
                    fig = px.imshow(
                        heatmap,
                        labels=dict(x="Day of Week", y="Hour", color="Entries"),
                        color_continuous_scale='Viridis',
                        aspect="auto"
                    )
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Not enough data for heatmap.")
            
            with col2:
                st.markdown("### 📉 Daily Trend with Moving Average")
                ma_data = analyzer.get_moving_average(window_days=7)
                
                if not ma_data.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=ma_data['date'].astype(str),
                        y=ma_data['entries'],
                        name='Daily Entries',
                        mode='lines+markers',
                        line=dict(color='#9E9E9E', width=1),
                        marker=dict(size=4)
                    ))
                    fig.add_trace(go.Scatter(
                        x=ma_data['date'].astype(str),
                        y=ma_data['ma_entries'],
                        name='7-Day Moving Avg',
                        mode='lines',
                        line=dict(color='#2196F3', width=3)
                    ))
                    fig.update_layout(
                        height=350,
                        xaxis_title="Date",
                        yaxis_title="Entries"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Not enough data for moving average.")
            
            st.markdown("---")
            
            # Forecasting Section
            st.markdown("### 🔮 Traffic Forecast")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Next Hour Prediction")
                forecast = analyzer.forecast_next_hour()
                
                next_hour = (datetime.now().hour + 1) % 24
                st.write(f"**Predicted for {next_hour:02d}:00**")
                
                fcol1, fcol2, fcol3 = st.columns(3)
                with fcol1:
                    st.metric("Expected Entries", f"{forecast['predicted_entries']:.0f}")
                with fcol2:
                    st.metric("Expected Exits", f"{forecast['predicted_exits']:.0f}")
                with fcol3:
                    st.metric("Confidence", f"{forecast['confidence']*100:.0f}%")
            
            with col2:
                st.markdown("#### Peak Hours Detected")
                peak_hours = analyzer.detect_peak_hours(percentile=75)
                
                if peak_hours:
                    peak_str = ", ".join([f"{h:02d}:00" for h in peak_hours])
                    st.info(f"🔥 **Peak Hours:** {peak_str}")
                else:
                    st.info("Not enough data to detect peak hours.")
                
                # Anomalies
                anomalies = analyzer.detect_anomalies(std_threshold=2.0)
                if not anomalies.empty:
                    st.warning(f"⚠️ **{len(anomalies)} anomalous days detected**")
                    st.dataframe(anomalies, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            st.markdown("---")
            
            # ==================== MEAL TIME ANALYSIS ====================
            st.markdown("### 🍽️ Meal Time Analysis")
            st.markdown("**Meal Schedule:** Breakfast (7:30-9:30), Lunch (12:00-14:00), Snacks (17:30-18:30), Dinner (19:30-21:30)")
            
            # Import MEAL_TIMES for display
            try:
                from src.time_series import MEAL_TIMES, MealStats
                
                # Meal comparison table
                meal_comparison = analyzer.get_meal_comparison(days=days)
                if not meal_comparison.empty:
                    st.dataframe(meal_comparison, use_container_width=True, hide_index=True)
                else:
                    st.info("No meal data available yet.")
                
                # Busiest meal highlight
                busiest_meal, busiest_stats = analyzer.get_busiest_meal(days=days)
                if busiest_stats.total_entries > 0:
                    emoji = MEAL_TIMES[busiest_meal]['emoji']
                    st.success(f"🏆 **Busiest Meal:** {emoji} {busiest_meal} with {busiest_stats.total_entries} entries (Avg Occupancy: {busiest_stats.avg_occupancy})")
                
                # Meal breakdown charts
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 📊 Entries by Meal")
                    all_meals = analyzer.get_all_meals_stats(days=days)
                    
                    if all_meals:
                        meal_names = [f"{MEAL_TIMES[m]['emoji']} {m}" for m in all_meals.keys()]
                        entries = [s.total_entries for s in all_meals.values()]
                        
                        if sum(entries) > 0:
                            fig = go.Figure(data=[go.Pie(
                                labels=meal_names,
                                values=entries,
                                hole=0.4,
                                marker_colors=['#FF9800', '#4CAF50', '#9C27B0', '#2196F3']
                            )])
                            fig.update_layout(
                                height=300,
                                showlegend=True,
                                legend=dict(orientation="h", yanchor="bottom", y=-0.2)
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No meal entries recorded yet.")
                
                with col2:
                    st.markdown("#### ⏱️ Select Meal for Breakdown")
                    selected_meal = st.selectbox(
                        "Meal",
                        list(MEAL_TIMES.keys()),
                        key="meal_select",
                        format_func=lambda x: f"{MEAL_TIMES[x]['emoji']} {x}"
                    )
                    
                    meal_breakdown = analyzer.get_meal_hourly_breakdown(selected_meal, days=days)
                    if not meal_breakdown.empty:
                        fig = go.Figure()
                        fig.add_trace(go.Bar(
                            x=meal_breakdown['time'],
                            y=meal_breakdown['entries'],
                            name='Entries',
                            marker_color='#4CAF50'
                        ))
                        fig.add_trace(go.Bar(
                            x=meal_breakdown['time'],
                            y=meal_breakdown['exits'],
                            name='Exits',
                            marker_color='#F44336'
                        ))
                        fig.update_layout(
                            height=250,
                            barmode='group',
                            xaxis_title="Hour",
                            yaxis_title="Count",
                            margin=dict(l=20, r=20, t=20, b=20)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info(f"No data for {selected_meal} yet.")
                
            except ImportError:
                st.warning("Meal time analysis not available.")
            
            st.markdown("---")
            
            # Export Section
            st.markdown("### 📥 Export Data")
            col1, col2 = st.columns(2)
            
            with col1:
                export_start = st.date_input("Export Start Date", datetime.now() - timedelta(days=30), key="ts_export_start")
            with col2:
                export_end = st.date_input("Export End Date", datetime.now(), key="ts_export_end")
            
            if st.button("📥 Generate CSV Export"):
                import io
                from datetime import datetime as dt
                
                start_dt = datetime.combine(export_start, datetime.min.time())
                end_dt = datetime.combine(export_end, datetime.max.time())
                
                df = analyzer._get_dataframe(start_date=start_dt, end_date=end_dt)
                if not df.empty:
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="⬇️ Download CSV",
                        data=csv,
                        file_name=f"eagleeye_timeseries_{export_start}_to_{export_end}.csv",
                        mime="text/csv"
                    )
                    st.success(f"✅ Ready to download {len(df)} records!")
                else:
                    st.warning("No data available for the selected date range.")
    
    # TAB 4: Insights (Demo Mode only)
    if demo_mode:
        with tab4:
            st.subheader("🏆 AI-Powered Insights")
            
            # Key insights cards
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### 📊 Capacity Analysis")
                capacity_pct = demo_stats['current_occupancy'] * 100 // demo_stats['max_capacity']
                
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=capacity_pct,
                    title={'text': "Capacity Utilization"},
                    delta={'reference': 50, 'suffix': "%"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#1f77b4"},
                        'steps': [
                            {'range': [0, 40], 'color': "#d4edda"},
                            {'range': [40, 70], 'color': "#fff3cd"},
                            {'range': [70, 100], 'color': "#f8d7da"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 85
                        }
                    }
                ))
                fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### 🔮 AI Predictions")
                st.markdown("""
                **Next Hour Forecast:**
                - Expected entries: **~85 people**
                - Expected exits: **~72 people**
                - Predicted occupancy: **~68 people**
                
                **Recommendations:**
                - ✅ Optimal staffing for current load
                - ⚠️ Lunch rush approaching in 2 hours
                - 📊 Suggest preparing extra seating
                """)
            
            with col3:
                st.markdown("### ⚡ Efficiency Metrics")
                metrics = [
                    ("Detection Accuracy", "98.7%", "✅"),
                    ("Processing Speed", "15 FPS", "✅"),
                    ("Avg Latency", "67ms", "✅"),
                    ("False Positives", "1.3%", "✅"),
                    ("System Uptime", "99.2%", "✅"),
                    ("Data Sync", "Real-time", "✅")
                ]
                for name, value, status in metrics:
                    st.markdown(f"{status} **{name}:** {value}")
            
            st.markdown("---")
            
            # Heatmap visualization
            st.subheader("🗺️ Weekly Occupancy Heatmap")
            
            heatmap_df = pd.DataFrame(heatmap_data)
            heatmap_pivot = heatmap_df.pivot(index='hour', columns='date', values='occupancy')
            
            fig = px.imshow(
                heatmap_pivot,
                labels=dict(x="Date", y="Hour", color="Occupancy"),
                x=[str(d) for d in heatmap_pivot.columns],
                y=heatmap_pivot.index,
                color_continuous_scale='RdYlGn_r',
                aspect="auto"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Fun facts
            st.markdown("---")
            st.subheader("🎉 Fun Facts")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🍕 Meals Served Today", f"{demo_stats['today_in']}")
            with col2:
                st.metric("☕ Coffee Breaks", f"{random.randint(50, 100)}")
            with col3:
                st.metric("🏃 Busiest Minute", "12:34 PM (23 entries!)")
            with col4:
                st.metric("🎯 Perfect Days", "42 (no overcrowding)")
        
        # Historical is tab5 in demo mode (after Time Series and Insights)
        historical_tab = tab5
        system_tab = tab6
    else:
        historical_tab = tab4
        system_tab = tab5
    
    # Historical Data Tab
    with historical_tab:
        st.subheader("📅 Historical Data")
        
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", datetime.now() - timedelta(days=7))
        with col2:
            end_date = st.date_input("End Date", datetime.now())
        
        # Load historical data
        conn = get_database_connection()
        if conn:
            query = f"""
            SELECT 
                timestamp,
                direction,
                occupancy
            FROM crossing_events
            WHERE date(timestamp) BETWEEN '{start_date}' AND '{end_date}'
            ORDER BY timestamp DESC
            """
            
            df_historical = pd.read_sql_query(query, conn)
            
            if not df_historical.empty:
                # Summary statistics
                col1, col2, col3 = st.columns(3)
                
                total_in = len(df_historical[df_historical['direction'] == 'IN'])
                total_out = len(df_historical[df_historical['direction'] == 'OUT'])
                avg_occupancy = df_historical['occupancy'].mean()
                
                with col1:
                    st.metric("Total IN", total_in)
                with col2:
                    st.metric("Total OUT", total_out)
                with col3:
                    st.metric("Avg Occupancy", f"{avg_occupancy:.1f}")
                
                # Download button
                csv = df_historical.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"eagleeye_data_{start_date}_to_{end_date}.csv",
                    mime="text/csv"
                )
                
                # Show data table
                st.dataframe(df_historical, use_container_width=True, height=400)
            else:
                st.info("No data available for selected date range.")
    
    # TAB 4: System Info
    with system_tab:
        st.subheader("⚙️ System Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Database Stats")
            conn = get_database_connection()
            if conn:
                cursor = conn.cursor()
                
                # Total records
                cursor.execute("SELECT COUNT(*) FROM crossing_events")
                total_records = cursor.fetchone()[0]
                
                # First record
                cursor.execute("SELECT MIN(timestamp) FROM crossing_events")
                first_record = cursor.fetchone()[0]
                
                # Last record
                cursor.execute("SELECT MAX(timestamp) FROM crossing_events")
                last_record = cursor.fetchone()[0]
                
                st.write(f"**Total Records:** {total_records}")
                st.write(f"**First Record:** {first_record or 'N/A'}")
                st.write(f"**Last Record:** {last_record or 'N/A'}")
                
                # Database size
                db_path = Path("eagle_eye.db")
                if db_path.exists():
                    size_mb = db_path.stat().st_size / (1024 * 1024)
                    st.write(f"**Database Size:** {size_mb:.2f} MB")
        
        with col2:
            st.markdown("### 🔧 Configuration")
            st.code("""
# Current Configuration
YOLO_MODEL = 'yolov8n.pt'
CONFIDENCE_THRESHOLD = 0.3
MIN_DETECTION_SIZE = (10, 10)
PROCESSING_WIDTH = 640
FRAME_SKIP = 3
DEFAULT_LINE_POSITION = 0.5
            """)
        
        st.markdown("---")
        
        # System actions
        st.markdown("### 🛠️ System Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🗑️ Clear Today's Data"):
                conn = get_database_connection()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM crossing_events WHERE date(timestamp) = date('now')")
                    conn.commit()
                    st.success("Today's data cleared!")
                    time.sleep(1)
                    st.rerun()
        
        with col2:
            if st.button("⚠️ Clear All Data"):
                if st.session_state.get('confirm_clear', False):
                    conn = get_database_connection()
                    if conn:
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM crossing_events")
                        conn.commit()
                        st.success("All data cleared!")
                        st.session_state['confirm_clear'] = False
                        time.sleep(1)
                        st.rerun()
                else:
                    st.warning("Click again to confirm")
                    st.session_state['confirm_clear'] = True
        
        with col3:
            if st.button("📊 Reset Counts"):
                st.info("This will be implemented in the main system")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray;'>
            🦅 EagleEye Dashboard | Made with ❤️ using Streamlit | 
            <a href='https://github.com/The-Harsh-Vardhan/EagleEye-Top_Down_Entrance_Counter_Using_Computer_Vision'>GitHub</a>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
