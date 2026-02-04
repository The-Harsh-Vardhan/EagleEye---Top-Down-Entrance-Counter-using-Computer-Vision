"""
Health check and monitoring module for EagleEye.

Provides system status monitoring, metrics collection, and health endpoints
for production deployments.
"""

import os
import sys
import time
import psutil
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, Optional, List
from pathlib import Path

from .config import DATABASE_PATH, VERSION


@dataclass
class SystemMetrics:
    """Container for system resource metrics."""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_percent: float
    python_version: str
    platform: str


@dataclass
class AppMetrics:
    """Container for application-specific metrics."""
    version: str
    uptime_seconds: float
    frames_processed: int = 0
    detections_total: int = 0
    crossings_in: int = 0
    crossings_out: int = 0
    last_detection_time: Optional[datetime] = None
    errors_count: int = 0


@dataclass
class HealthStatus:
    """Overall health status of the application."""
    status: str  # "healthy", "degraded", "unhealthy"
    timestamp: datetime
    system: SystemMetrics
    app: AppMetrics
    checks: Dict[str, bool] = field(default_factory=dict)
    message: str = ""


class HealthMonitor:
    """
    Monitors application health and collects metrics.
    
    Usage:
        monitor = HealthMonitor()
        monitor.record_frame()
        monitor.record_detection(count=3)
        monitor.record_crossing("IN")
        status = monitor.get_health()
    """
    
    def __init__(self):
        """Initialize the health monitor."""
        self._start_time = datetime.now()
        self._frames_processed = 0
        self._detections_total = 0
        self._crossings_in = 0
        self._crossings_out = 0
        self._last_detection_time: Optional[datetime] = None
        self._errors: List[str] = []
    
    def record_frame(self) -> None:
        """Record a processed frame."""
        self._frames_processed += 1
    
    def record_detection(self, count: int = 1) -> None:
        """Record person detections."""
        self._detections_total += count
        if count > 0:
            self._last_detection_time = datetime.now()
    
    def record_crossing(self, direction: str) -> None:
        """Record a line crossing event."""
        if direction.upper() == "IN":
            self._crossings_in += 1
        elif direction.upper() == "OUT":
            self._crossings_out += 1
    
    def record_error(self, error: str) -> None:
        """Record an error occurrence."""
        self._errors.append(f"{datetime.now().isoformat()}: {error}")
        # Keep only last 100 errors
        if len(self._errors) > 100:
            self._errors = self._errors[-100:]
    
    def get_uptime(self) -> timedelta:
        """Get application uptime."""
        return datetime.now() - self._start_time
    
    def get_system_metrics(self) -> SystemMetrics:
        """Collect current system resource metrics."""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage(Path.cwd())
            
            return SystemMetrics(
                cpu_percent=psutil.cpu_percent(interval=0.1),
                memory_percent=memory.percent,
                memory_used_mb=memory.used / (1024 * 1024),
                disk_percent=disk.percent,
                python_version=sys.version.split()[0],
                platform=sys.platform
            )
        except Exception:
            # Return defaults if psutil fails
            return SystemMetrics(
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used_mb=0.0,
                disk_percent=0.0,
                python_version=sys.version.split()[0],
                platform=sys.platform
            )
    
    def get_app_metrics(self) -> AppMetrics:
        """Get application-specific metrics."""
        return AppMetrics(
            version=VERSION,
            uptime_seconds=self.get_uptime().total_seconds(),
            frames_processed=self._frames_processed,
            detections_total=self._detections_total,
            crossings_in=self._crossings_in,
            crossings_out=self._crossings_out,
            last_detection_time=self._last_detection_time,
            errors_count=len(self._errors)
        )
    
    def run_health_checks(self) -> Dict[str, bool]:
        """Run all health checks and return results."""
        checks = {}
        
        # Check 1: Database accessible
        try:
            db_path = Path(DATABASE_PATH)
            checks["database"] = db_path.exists() or not db_path.is_absolute()
        except Exception:
            checks["database"] = False
        
        # Check 2: Memory usage below 90%
        try:
            memory = psutil.virtual_memory()
            checks["memory"] = memory.percent < 90
        except Exception:
            checks["memory"] = True  # Assume OK if can't check
        
        # Check 3: Disk space above 10%
        try:
            disk = psutil.disk_usage(Path.cwd())
            checks["disk_space"] = disk.percent < 90
        except Exception:
            checks["disk_space"] = True
        
        # Check 4: Recent activity (if running for > 1 min)
        uptime = self.get_uptime().total_seconds()
        if uptime > 60:
            checks["active"] = self._frames_processed > 0
        else:
            checks["active"] = True  # Too early to check
        
        return checks
    
    def get_health(self) -> HealthStatus:
        """Get comprehensive health status."""
        checks = self.run_health_checks()
        system = self.get_system_metrics()
        app = self.get_app_metrics()
        
        # Determine overall status
        failed_checks = [k for k, v in checks.items() if not v]
        
        if not failed_checks:
            status = "healthy"
            message = "All systems operational"
        elif len(failed_checks) == 1:
            status = "degraded"
            message = f"Issue with: {failed_checks[0]}"
        else:
            status = "unhealthy"
            message = f"Multiple issues: {', '.join(failed_checks)}"
        
        return HealthStatus(
            status=status,
            timestamp=datetime.now(),
            system=system,
            app=app,
            checks=checks,
            message=message
        )
    
    def get_health_dict(self) -> Dict:
        """Get health status as a dictionary (JSON-serializable)."""
        health = self.get_health()
        return {
            "status": health.status,
            "timestamp": health.timestamp.isoformat(),
            "message": health.message,
            "checks": health.checks,
            "system": {
                "cpu_percent": health.system.cpu_percent,
                "memory_percent": health.system.memory_percent,
                "memory_used_mb": round(health.system.memory_used_mb, 2),
                "disk_percent": health.system.disk_percent,
                "python_version": health.system.python_version,
                "platform": health.system.platform
            },
            "app": {
                "version": health.app.version,
                "uptime_seconds": round(health.app.uptime_seconds, 2),
                "frames_processed": health.app.frames_processed,
                "detections_total": health.app.detections_total,
                "crossings_in": health.app.crossings_in,
                "crossings_out": health.app.crossings_out,
                "errors_count": health.app.errors_count
            }
        }


# Global monitor instance
_monitor: Optional[HealthMonitor] = None


def get_monitor() -> HealthMonitor:
    """Get or create the global health monitor instance."""
    global _monitor
    if _monitor is None:
        _monitor = HealthMonitor()
    return _monitor
