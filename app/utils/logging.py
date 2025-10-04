"""
Logging configuration for ArchaeoVault.

This module provides structured logging configuration following
12-Factor App principles and best practices.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

from ..config import LoggingSettings


def setup_logging(settings: LoggingSettings) -> None:
    """
    Setup application logging configuration.
    
    Args:
        settings: Logging configuration settings
    """
    # Create logs directory if it doesn't exist
    log_file_path = Path(settings.file_path)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    if settings.format == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.level.upper()))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.handlers.RotatingFileHandler(
        filename=settings.file_path,
        maxBytes=settings.max_size_mb * 1024 * 1024,
        backupCount=settings.backup_count
    )
    file_handler.setLevel(getattr(logging, settings.level.upper()))
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Configure specific loggers
    _configure_third_party_loggers()
    
    # Log configuration
    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully")
    logger.info("Log level: %s", settings.level)
    logger.info("Log format: %s", settings.format)
    logger.info("Log file: %s", settings.file_path)


def _configure_third_party_loggers() -> None:
    """Configure third-party library loggers."""
    # Reduce noise from third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("asyncpg").setLevel(logging.WARNING)
    logging.getLogger("redis").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.INFO)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        import json
        from datetime import datetime
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in log_entry and not key.startswith("_"):
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str)


class StructuredLogger:
    """Structured logger for application components."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message with structured data."""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message with structured data."""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message with structured data."""
        self.logger.error(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message with structured data."""
        self.logger.debug(message, extra=kwargs)
    
    def exception(self, message: str, **kwargs) -> None:
        """Log exception with structured data."""
        self.logger.exception(message, extra=kwargs)
