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
    
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Analytics", "🕐 Historical", "⚙️ System"])
    
    # TAB 1: Overview
    with tab1:
        # Current statistics
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
    
    # TAB 3: Historical Data
    with tab3:
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
    with tab4:
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
