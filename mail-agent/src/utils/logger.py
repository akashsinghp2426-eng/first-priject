"""Logging utility for Mail Agent."""

import logging
import sys
from pathlib import Path
from colorama import init, Fore, Style


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, Fore.WHITE)
        record.levelname = f"{log_color}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)


def setup_logger(name: str = 'MailAgent', config: dict = None) -> logging.Logger:
    """Setup and configure logger.
    
    Args:
        name: Logger name
        config: Logging configuration dict (optional)
        
    Returns:
        Configured logger instance
    """
    # Initialize colorama
    init()
    
    # Get config values
    if config is None:
        config = {}
    
    level_str = config.get('level', 'INFO')
    log_file = config.get('file', 'logs/mail_agent.log')
    max_size = config.get('max_size_mb', 10) * 1024 * 1024
    backup_count = config.get('backup_count', 5)
    
    # Convert level string to logging constant
    level = getattr(logging, level_str.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers = []  # Clear existing handlers
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    console_formatter = ColoredFormatter(console_format, datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    try:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(level)
        file_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        file_formatter = logging.Formatter(file_format, datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not create log file: {e}")
    
    return logger
