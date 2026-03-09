"""Logging configuration and utilities."""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "theme_anchor_agent",
    log_file: Optional[str] = None,
    level: str = "INFO",
    log_format: Optional[str] = None,
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5,
    console_output: bool = True
) -> logging.Logger:
    """Setup and configure logger.
    
    Args:
        name: Logger name
        log_file: Path to log file. If None, logs only to console
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log message format
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        console_output: Whether to output to console
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Set logging level
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Default format
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    formatter = logging.Formatter(log_format)
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "theme_anchor_agent") -> logging.Logger:
    """Get logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def setup_logger_from_config(config: dict) -> logging.Logger:
    """Setup logger from configuration dictionary.
    
    Args:
        config: Configuration dictionary with logging settings
        
    Returns:
        Configured logger instance
    """
    logging_config = config.get('logging', {})
    
    return setup_logger(
        name="theme_anchor_agent",
        log_file=logging_config.get('file'),
        level=logging_config.get('level', 'INFO'),
        log_format=logging_config.get('format'),
        max_bytes=logging_config.get('max_bytes', 10485760),
        backup_count=logging_config.get('backup_count', 5),
        console_output=logging_config.get('console_output', True)
    )
