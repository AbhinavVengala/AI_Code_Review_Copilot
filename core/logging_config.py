"""
Logging configuration for AI Code Review Copilot.

Provides structured logging with JSON output for production and
colored console output for development.
"""
import os
import sys
import logging
import structlog
from typing import Any


def get_log_level() -> str:
    """Get log level from environment or default to INFO."""
    return os.getenv("LOG_LEVEL", "INFO").upper()


def is_production() -> bool:
    """Check if running in production environment."""
    return os.getenv("ENVIRONMENT", "development").lower() == "production"


def configure_logging() -> None:
    """
    Configure structured logging for the application.
    
    - Production: JSON output for log aggregation
    - Development: Colored console output for readability
    """
    log_level = get_log_level()
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level),
    )
    
    # Shared processors for both environments
    shared_processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    if is_production():
        # Production: JSON output
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer()
        ]
    else:
        # Development: Colored console output
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = None) -> Any:
    """
   Get a configured logger instance.
    
    Args:
        name: Logger name (usually __name__ of the module)
    
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


# Configure logging on module import
configure_logging()
