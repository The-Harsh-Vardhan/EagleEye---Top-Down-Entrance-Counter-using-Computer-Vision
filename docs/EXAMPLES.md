# EagleEye Usage Examples

Real-world examples and use cases for the EagleEye People Counting System.

## Table of Contents

- [Basic Examples](#basic-examples)
- [Advanced Usage](#advanced-usage)
- [Use Case Scenarios](#use-case-scenarios)
- [Integration Examples](#integration-examples)
- [Analysis & Reporting](#analysis--reporting)

---

## Basic Examples

### Example 1: Webcam Monitoring

Monitor your office entrance with a USB webcam:

```bash
python main.py --source 0
```

**When to use**: Quick testing, desktop setup, single room monitoring.

---

### Example 2: Pre-recorded Video Analysis

Analyze a recorded video to count people and export results:

```bash
python main.py \
  --source recordings/entrance_video.mp4 \
  --output analyzed_output.mp4 \
  --line-position 0.6
```

**When to use**: Analyzing historical footage, testing different line positions, creating demonstration videos.

---

### Example 3: IP Camera (ESP32-CAM)

Monitor entrance with ESP32-CAM over WiFi:

```bash
python main.py \
  --source http://192.168.1.100:81/stream \
  --confidence 0.6 \
  --min-size 35
```

**When to use**: Budget-friendly deployment, WiFi-based monitoring, maker projects.

**ESP32-CAM Setup:**
1. Flash with CameraWebServer sketch
2. Configure WiFi credentials
3. Note IP address from Serial Monitor
4. Use stream URL: `http://<IP>:81/stream`

---

### Example 4: Headless Server Deployment

Run on a server without display for continuous monitoring:

```bash
python main.py \
  --source http://192.168.1.100/stream \
  --no-display \
  --confidence 0.65 &
```

**When to use**: 24/7 monitoring, Raspberry Pi deployment, cloud servers.

**View logs:**
```bash
# Check last 100 events
sqlite3 eagle_eye.db "SELECT * FROM crossing_events ORDER BY timestamp DESC LIMIT 100;"
```

---

## Advanced Usage

### Example 5: High-Traffic Entrance

Optimize for high-traffic college mess hall entrance:

```bash
python main.py \
  --source rtsp://admin:password@192.168.1.50:554/stream1 \
  --line-position 0.55 \
  --confidence 0.7 \
  --min-size 45
```

**Configuration** ([src/config.py](src/config.py)):
```python
# Use faster model for real-time
YOLO_MODEL = 'yolov8n.pt'

# Reduce false positives
CONFIDENCE_THRESHOLD = 0.7
MIN_DETECTION_SIZE = (45, 45)

# Handle crowded scenes
TRACK_BUFFER = 45  # Longer buffer for occlusions
MIN_CROSSING_DISTANCE = 15  # Prevent jitter in crowds
```

---

### Example 6: Multiple Entrances (Separate Instances)

Monitor two entrances with separate databases:

**Terminal 1 (Main Entrance):**
```bash
# Create separate directory
mkdir main_entrance && cd main_entrance
cp ../main.py ../src -r .
python main.py --source http://192.168.1.100:81/stream
# Creates eagle_eye.db in main_entrance/
```

**Terminal 2 (Side Entrance):**
```bash
mkdir side_entrance && cd side_entrance
cp ../main.py ../src -r .
python main.py --source http://192.168.1.101:81/stream
# Creates eagle_eye.db in side_entrance/
```

**Combine data:**
```bash
# Query both databases
sqlite3 main_entrance/eagle_eye.db "SELECT 'Main' as entrance, * FROM crossing_events WHERE date(timestamp) = date('now');" > today.csv
sqlite3 side_entrance/eagle_eye.db "SELECT 'Side' as entrance, * FROM crossing_events WHERE date(timestamp) = date('now');" >> today.csv
```

---

### Example 7: GPU Acceleration

Use NVIDIA GPU for maximum performance:

```bash
# Verify CUDA is available
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"

# Use larger, more accurate model with GPU
python main.py \
  --source 0 \
  --confidence 0.5
```

**Configuration** for GPU:
```python
# In src/config.py
YOLO_MODEL = 'yolov8s.pt'  # More accurate with GPU
CONFIDENCE_THRESHOLD = 0.5
```

**Expected Performance:**
- CPU: 15-25 FPS with yolov8n
- GPU (GTX 1650): 60-80 FPS with yolov8n
- GPU (RTX 3060): 80-120 FPS with yolov8s

---

## Use Case Scenarios

### Scenario 1: College Mess Hall Occupancy

**Goal**: Track student dining patterns to correlate with food quality and menu.

**Setup:**
- Camera: Ceiling-mounted 1080p IP camera
- Position: Directly above entrance
- Line position: 0.5 (center of doorway)

**Implementation:**
```bash
python main.py \
  --source rtsp://admin:pass@192.168.1.50:554/stream \
  --line-position 0.5 \
  --confidence 0.6 \
  --no-display
```

**Daily Analysis:**
```sql
-- Peak hours
SELECT 
  strftime('%H:00', timestamp) as hour,
  COUNT(*) as entries
FROM crossing_events
WHERE direction = 'IN' 
  AND date(timestamp) = date('now')
GROUP BY hour
ORDER BY entries DESC;

-- Compare weekdays
SELECT 
  CASE CAST(strftime('%w', timestamp) AS INTEGER)
    WHEN 0 THEN 'Sunday'
    WHEN 1 THEN 'Monday'
    WHEN 2 THEN 'Tuesday'
    WHEN 3 THEN 'Wednesday'
    WHEN 4 THEN 'Thursday'
    WHEN 5 THEN 'Friday'
    WHEN 6 THEN 'Saturday'
  END as day_name,
  COUNT(*) as total_entries
FROM crossing_events
WHERE direction = 'IN'
  AND date(timestamp) >= date('now', '-7 days')
GROUP BY strftime('%w', timestamp)
ORDER BY total_entries DESC;
```

**Insights:**
- Identify low-turnout days (potential food quality issues)
- Discover peak times for staff scheduling
- Correlate menu items with attendance

---

### Scenario 2: Retail Store Traffic Analysis

**Goal**: Count customer visits and measure conversion rates.

**Setup:**
- Camera: Doorway-mounted wide-angle camera
- Line position: 0.6 (just inside door)

**Implementation:**
```bash
# Business hours only (scheduled via cron/Task Scheduler)
python main.py \
  --source 0 \
  --line-position 0.6 \
  --confidence 0.65
```

**Weekly Report:**
```sql
-- Daily traffic summary
SELECT 
  date(timestamp) as date,
  SUM(CASE WHEN direction = 'IN' THEN 1 ELSE 0 END) as entries,
  SUM(CASE WHEN direction = 'OUT' THEN 1 ELSE 0 END) as exits,
  AVG(occupancy) as avg_occupancy,
  MAX(occupancy) as peak_occupancy
FROM crossing_events
WHERE date(timestamp) >= date('now', '-7 days')
GROUP BY date(timestamp)
ORDER BY date DESC;
```

**Business Metrics:**
- Calculate conversion rate: (Sales / Entries) × 100%
- Identify busiest days for staffing
- Measure marketing campaign impact

---

### Scenario 3: Library Capacity Management

**Goal**: Track library occupancy to prevent overcrowding (COVID-safe).

**Setup:**
- Camera: Entrance monitoring
- Alert when capacity reaches 80%

**Implementation:**

**Python wrapper with alerts:**
```python
# monitor_with_alerts.py
import subprocess
import sqlite3
import time
import smtplib
from email.message import EmailMessage

MAX_CAPACITY = 50
ALERT_THRESHOLD = 0.8  # 80%

def send_alert(occupancy):
    msg = EmailMessage()
    msg.set_content(f"Library occupancy: {occupancy}/{MAX_CAPACITY} ({occupancy/MAX_CAPACITY*100:.0f}%)")
    msg['Subject'] = 'Library Capacity Alert'
    msg['From'] = 'library@example.com'
    msg['To'] = 'admin@example.com'
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('your_email', 'your_password')
        server.send_message(msg)

def monitor():
    # Run EagleEye in background
    process = subprocess.Popen([
        'python', 'main.py',
        '--source', '0',
        '--no-display'
    ])
    
    # Monitor database
    while True:
        time.sleep(30)  # Check every 30 seconds
        
        conn = sqlite3.connect('eagle_eye.db')
        cursor = conn.cursor()
        cursor.execute("SELECT occupancy FROM crossing_events ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        
        if result:
            occupancy = result[0]
            if occupancy >= MAX_CAPACITY * ALERT_THRESHOLD:
                send_alert(occupancy)

if __name__ == '__main__':
    monitor()
```

---

### Scenario 4: Event Venue Attendance

**Goal**: Real-time attendance counting for conferences/events.

**Setup:**
- Multiple cameras at all entrances
- Aggregate counts from all entrances

**Multi-entrance aggregation:**
```python
# aggregate_counts.py
import sqlite3
from datetime import datetime

DATABASES = [
    'entrance1/eagle_eye.db',
    'entrance2/eagle_eye.db',
    'entrance3/eagle_eye.db'
]

def get_total_occupancy():
    total_in = 0
    total_out = 0
    
    for db_path in DATABASES:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get latest counts
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN direction = 'IN' THEN 1 ELSE 0 END) as ins,
                SUM(CASE WHEN direction = 'OUT' THEN 1 ELSE 0 END) as outs
            FROM crossing_events
            WHERE date(timestamp) = date('now')
        """)
        
        ins, outs = cursor.fetchone()
        total_in += ins or 0
        total_out += outs or 0
        conn.close()
    
    return total_in - total_out

# Real-time display
import time
while True:
    occupancy = get_total_occupancy()
    print(f"Current Attendance: {occupancy}", end='\r')
    time.sleep(5)
```

---

## Integration Examples

### Example 8: REST API Integration

Create a simple Flask API to expose count data:

```python
# api_server.py
from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/api/stats')
def get_stats():
    conn = sqlite3.connect('eagle_eye.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Current occupancy
    cursor.execute("SELECT occupancy FROM crossing_events ORDER BY id DESC LIMIT 1")
    current = cursor.fetchone()
    
    # Today's traffic
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN direction = 'IN' THEN 1 ELSE 0 END) as total_in,
            SUM(CASE WHEN direction = 'OUT' THEN 1 ELSE 0 END) as total_out
        FROM crossing_events
        WHERE date(timestamp) = date('now')
    """)
    today = cursor.fetchone()
    
    conn.close()
    
    return jsonify({
        'current_occupancy': current['occupancy'] if current else 0,
        'today_entries': today['total_in'] or 0,
        'today_exits': today['total_out'] or 0,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/events/<int:hours>')
def get_recent_events(hours):
    conn = sqlite3.connect('eagle_eye.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM crossing_events
        WHERE datetime(timestamp) >= datetime('now', '-' || ? || ' hours')
        ORDER BY timestamp DESC
    """, (hours,))
    
    events = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(events)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

**Usage:**
```bash
# Start API server
python api_server.py

# Query from anywhere
curl http://localhost:5000/api/stats
curl http://localhost:5000/api/events/24
```

---

### Example 9: MQTT Integration (IoT)

Publish events to MQTT broker for smart building integration:

```python
# mqtt_publisher.py
import sqlite3
import time
import json
import paho.mqtt.client as mqtt

# MQTT Configuration
BROKER = 'mqtt.example.com'
PORT = 1883
TOPIC_PREFIX = 'building/entrance'

client = mqtt.Client()
client.connect(BROKER, PORT)

last_id = 0

while True:
    conn = sqlite3.connect('eagle_eye.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get new events
    cursor.execute("""
        SELECT * FROM crossing_events
        WHERE id > ?
        ORDER BY id ASC
    """, (last_id,))
    
    events = cursor.fetchall()
    
    for event in events:
        payload = {
            'direction': event['direction'],
            'occupancy': event['occupancy'],
            'timestamp': event['timestamp']
        }
        
        client.publish(f"{TOPIC_PREFIX}/events", json.dumps(payload))
        client.publish(f"{TOPIC_PREFIX}/occupancy", event['occupancy'])
        
        last_id = event['id']
    
    conn.close()
    time.sleep(1)
```

---

## Analysis & Reporting

### Example 10: Weekly Report Generation

Generate automated weekly PDF reports:

```python
# weekly_report.py
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def generate_weekly_report():
    conn = sqlite3.connect('eagle_eye.db')
    cursor = conn.cursor()
    
    # Get week data
    cursor.execute("""
        SELECT 
            strftime('%Y-%m-%d', timestamp) as date,
            strftime('%H', timestamp) as hour,
            direction,
            COUNT(*) as count
        FROM crossing_events
        WHERE date(timestamp) >= date('now', '-7 days')
        GROUP BY date, hour, direction
    """)
    
    data = cursor.fetchall()
    conn.close()
    
    # Create PDF
    with PdfPages('weekly_report.pdf') as pdf:
        # Page 1: Daily traffic
        fig, ax = plt.subplots(figsize=(10, 6))
        # ... plotting code ...
        pdf.savefig(fig)
        
        # Page 2: Hourly patterns
        fig, ax = plt.subplots(figsize=(10, 6))
        # ... plotting code ...
        pdf.savefig(fig)
        
    print("Report saved: weekly_report.pdf")

generate_weekly_report()
```

---

## Tips & Best Practices

### 1. Optimal Line Positioning

```bash
# Test different positions
python main.py --source video.mp4 --line-position 0.4  # 40% from top
python main.py --source video.mp4 --line-position 0.5  # Center
python main.py --source video.mp4 --line-position 0.6  # 60% from top
```

**Rule of thumb:**
- Wide entrance: 0.5 (center)
- Narrow entrance: 0.6 (slightly inside)
- Test with sample footage to minimize double-counting

### 2. Confidence Tuning

```bash
# Too many false positives? Increase confidence
python main.py --source 0 --confidence 0.7

# Missing detections? Decrease confidence
python main.py --source 0 --confidence 0.4
```

### 3. Performance Optimization

```python
# config.py adjustments for different scenarios

# High FPS (low accuracy OK)
YOLO_MODEL = 'yolov8n.pt'
CONFIDENCE_THRESHOLD = 0.6
PROCESSING_WIDTH = 640

# High accuracy (low FPS OK)
YOLO_MODEL = 'yolov8m.pt'
CONFIDENCE_THRESHOLD = 0.5
PROCESSING_WIDTH = None  # Full resolution
```

---

For more examples and use cases, visit the [GitHub repository](https://github.com/The-Harsh-Vardhan/EagleEye) or [open a discussion](https://github.com/The-Harsh-Vardhan/EagleEye/discussions).
