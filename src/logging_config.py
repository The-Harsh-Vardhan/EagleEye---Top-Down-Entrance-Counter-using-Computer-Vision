"""
Logging configuration for EagleEye People Counting System.

Provides structured logging with:
- Console output (colored)
- File logging with rotation
- Different log levels per environment
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from datetime import datetime

# Default log directory
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_FILE = LOG_DIR / "eagleeye.log"

# Log format
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    level: str = "INFO",
    log_to_file: bool = True,
    log_dir: Path = LOG_DIR,
    max_bytes: int = 5 * 1024 * 1024,  # 5MB
    backup_count: int = 3
) -> logging.Logger:
    """
    Configure and return the root logger for EagleEye.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to write logs to file
        log_dir: Directory for log files
        max_bytes: Max size per log file before rotation
        backup_count: Number of backup files to keep
    
    Returns:
        Configured root logger
    """
    # Create logs directory if it doesn't exist
    if log_to_file:
        log_dir.mkdir(parents=True, exist_ok=True)
    
    # Get or create the root logger
    logger = logging.getLogger("eagleeye")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_formatter = ColoredFormatter(LOG_FORMAT, DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_to_file:
        log_file = log_dir / "eagleeye.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds colors to console output.
    """
    
    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[41m",  # Red background
    }
    RESET = "\033[0m"
    
    def format(self, record):
        # Add color to levelname
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
        
        result = super().format(record)
        
        # Restore original levelname for file logging
        record.levelname = levelname
        
        return result


def get_logger(name: str = "eagleeye") -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (use module name for sub-loggers)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Create default logger on import
_logger = None


def get_default_logger() -> logging.Logger:
    """Get or create the default application logger."""
    global _logger
    if _logger is None:
        log_level = os.environ.get("EAGLEEYE_LOG_LEVEL", "INFO")
        _logger = setup_logging(level=log_level)
    return _logger
