# =============================================================================
# EagleEye - People Counting System
# Multi-stage Docker Build
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Base image with Python and system dependencies
# -----------------------------------------------------------------------------
FROM python:3.11-slim as base

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for OpenCV and video processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------------------
# Stage 2: Builder - Install Python dependencies
# -----------------------------------------------------------------------------
FROM base as builder

WORKDIR /app

# Copy requirements files
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# -----------------------------------------------------------------------------
# Stage 3: Production image
# -----------------------------------------------------------------------------
FROM base as production

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash eagleeye && \
    mkdir -p /app/logs /app/data && \
    chown -R eagleeye:eagleeye /app

# Copy application code
COPY --chown=eagleeye:eagleeye . .

# Download YOLO model (optional - can also mount at runtime)
# RUN python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

# Switch to non-root user
USER eagleeye

# Environment variables
ENV EAGLEEYE_DATABASE_PATH=/app/data/eagle_eye.db \
    EAGLEEYE_LOG_LEVEL=INFO \
    EAGLEEYE_LOG_TO_FILE=true

# Expose ports
# 8501 - Streamlit Dashboard
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from src.health import get_monitor; print(get_monitor().get_health().status)" || exit 1

# Default command - run dashboard
CMD ["streamlit", "run", "dashboard.py", "--server.address", "0.0.0.0", "--server.port", "8501"]

# -----------------------------------------------------------------------------
# Stage 4: Development image (includes dev dependencies)
# -----------------------------------------------------------------------------
FROM production as development

USER root

# Install development dependencies
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

USER eagleeye

# Override command for development
CMD ["bash"]
