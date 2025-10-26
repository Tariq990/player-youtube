"""
Logging Configuration - Centralized logging setup.

This module provides a centralized logging configuration for the entire project.
Uses rotating file handler to prevent log files from growing too large.
"""

# Standard library imports
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


def setup_logging(
    log_path: str = "logs/app.log",
    level: int = logging.INFO,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
    console_output: bool = True
) -> logging.Logger:
    """
    Configure logging with rotating file handler and optional console output.
    
    Args:
        log_path: Path to log file
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        console_output: Whether to output logs to console
        
    Returns:
        Configured logger instance
        
    Example:
        >>> logger = setup_logging("logs/app.log", level=logging.DEBUG)
        >>> logger.info("Application started")
    """
    # Ensure log directory exists
    log_file = Path(log_path)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("youtube_player")
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatters
    file_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)  # Console shows INFO and above
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    logger.info("=" * 60)
    logger.info("Logging system initialized")
    logger.info(f"Log file: {log_path}")
    logger.info(f"Log level: {logging.getLevelName(level)}")
    logger.info("=" * 60)
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get logger instance for a specific module.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.debug("Debug message")
    """
    if name:
        return logging.getLogger(f"youtube_player.{name}")
    return logging.getLogger("youtube_player")
