"""Logging utilities."""
from __future__ import annotations

import logging
import sys
from pathlib import Path

from infrastructure.config import get_config


def setup_logging() -> None:
    """Setup logging configuration."""
    config = get_config()
    
    log_level = getattr(logging, config.log.level.upper(), logging.INFO)
    
    log_format = config.log.format
    
    handlers = []
    
    if config.log.console_enabled:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(console_handler)
    
    if config.log.file_enabled:
        log_file = Path(config.log.file_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        from logging.handlers import RotatingFileHandler
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=config.log.file_max_bytes,
            backupCount=config.log.file_backup_count,
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(file_handler)
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers,
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Logging initialized")
