# 🐳 Docker Deployment Guide

## Quick Start

```bash
# Build and start the dashboard
docker-compose up -d dashboard

# View logs
docker-compose logs -f dashboard

# Access dashboard at http://localhost:8501
```

---

## Services

| Service | Port | Description |
|---------|------|-------------|
| `dashboard` | 8501 | Streamlit analytics dashboard |
| `counter` | - | Main counting application (headless) |
| `dev` | - | Development environment |

---

## Commands

### Start Dashboard Only
```bash
docker-compose up -d dashboard
```

### Start Counter with Video File
```bash
docker-compose --profile counter up -d
```

### Development Mode
```bash
docker-compose --profile dev run dev bash
```

### View Logs
```bash
docker-compose logs -f
```

### Stop All Services
```bash
docker-compose down
```

### Rebuild After Code Changes
```bash
docker-compose build --no-cache
docker-compose up -d
```

---

## Configuration

Environment variables can be set in `docker-compose.yml` or via `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `EAGLEEYE_LOG_LEVEL` | INFO | DEBUG, INFO, WARNING, ERROR |
| `EAGLEEYE_DATABASE_PATH` | /app/data/eagle_eye.db | Database location |
| `EAGLEEYE_CONFIDENCE` | 0.5 | Detection threshold |

---

## Volumes

| Volume | Purpose |
|--------|---------|
| `eagleeye_data` | Persistent database storage |
| `eagleeye_logs` | Log file storage |

---

## Using with Webcam (Linux)

Edit `docker-compose.yml` and uncomment:
```yaml
devices:
  - /dev/video0:/dev/video0
```

---

## Using with RTSP Stream

```bash
docker-compose run counter python main.py \
  --source rtsp://user:pass@192.168.1.100:554/stream \
  --no-display
```
