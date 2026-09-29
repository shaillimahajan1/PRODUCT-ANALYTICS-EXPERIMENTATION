"""
Structured logging utility for Product Analytics Platform.
"""

import logging
import sys


def setup_logger(name: str = "product_analytics", level: int = logging.INFO) -> logging.Logger:
    """
    Configure and return a structured logger.
    
    Args:
        name: Name of the logger.
        level: Logging level (default: logging.INFO).
        
    Returns:
        Configured logging.Logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
