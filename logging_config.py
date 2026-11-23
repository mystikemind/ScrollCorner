"""
Centralized logging configuration for ScrollCorner pipeline.
Provides consistent logging across all modules.
"""
import logging
import sys
from datetime import datetime

# Create logs directory if it doesn't exist
import os
os.makedirs('logs', exist_ok=True)

def setup_logger(name: str, level=logging.INFO) -> logging.Logger:
    """
    Configure a logger with both file and console handlers.
    
    Args:
        name: Logger name (typically __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Format: [TIMESTAMP] [LEVEL] [MODULE] Message
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)-8s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    logger.addHandler(console_handler)
    
    # File handler (daily rotation)
    log_filename = f'logs/scrollcorner_{datetime.now().strftime("%Y-%m-%d")}.log'
    try:
        file_handler = logging.FileHandler(log_filename)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)  # File gets all levels
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f'Could not create log file {log_filename}: {e}')
    
    return logger
