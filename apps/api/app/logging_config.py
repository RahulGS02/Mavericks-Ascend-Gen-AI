"""
Logging configuration for Maverick Ascend API
Provides separate log files for AI operations
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Create timestamp for log files
TIMESTAMP = datetime.now().strftime("%Y%m%d")

# Log file paths
AI_LOG_FILE = LOGS_DIR / f"ai_service_{TIMESTAMP}.log"
TALENT_SEARCH_LOG_FILE = LOGS_DIR / f"talent_search_{TIMESTAMP}.log"
APP_LOG_FILE = LOGS_DIR / f"app_{TIMESTAMP}.log"


def setup_ai_logging():
    """
    Setup dedicated logging for AI operations
    This captures ONLY AI-related logs in a separate file
    """
    
    # Create AI service logger
    ai_logger = logging.getLogger("ai_service")
    ai_logger.setLevel(logging.DEBUG)
    ai_logger.propagate = False  # Don't propagate to root logger
    
    # File handler for AI logs (rotating, 10MB max, keep 5 backups)
    ai_file_handler = RotatingFileHandler(
        AI_LOG_FILE,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    ai_file_handler.setLevel(logging.DEBUG)
    
    # Detailed format for AI logs
    ai_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    ai_file_handler.setFormatter(ai_formatter)
    
    # Add handler
    ai_logger.addHandler(ai_file_handler)
    
    # Also log to console in development
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(ai_formatter)
    ai_logger.addHandler(console_handler)
    
    return ai_logger


def setup_talent_search_logging():
    """
    Setup dedicated logging for talent search operations
    """
    
    # Create talent search logger
    ts_logger = logging.getLogger("talent_search")
    ts_logger.setLevel(logging.DEBUG)
    ts_logger.propagate = False
    
    # File handler
    ts_file_handler = RotatingFileHandler(
        TALENT_SEARCH_LOG_FILE,
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    ts_file_handler.setLevel(logging.DEBUG)
    
    # Format
    ts_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    ts_file_handler.setFormatter(ts_formatter)
    
    # Add handler
    ts_logger.addHandler(ts_file_handler)
    
    # Console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(ts_formatter)
    ts_logger.addHandler(console_handler)
    
    return ts_logger


def setup_app_logging():
    """
    Setup general application logging
    """
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # File handler
    app_file_handler = RotatingFileHandler(
        APP_LOG_FILE,
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    app_file_handler.setLevel(logging.INFO)
    
    # Format
    app_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    app_file_handler.setFormatter(app_formatter)
    
    # Add handler
    root_logger.addHandler(app_file_handler)
    
    return root_logger


def initialize_logging():
    """
    Initialize all logging handlers
    Call this once at application startup
    """
    # Setup all loggers
    ai_logger = setup_ai_logging()
    ts_logger = setup_talent_search_logging()
    app_logger = setup_app_logging()
    
    # Log initialization
    ai_logger.info("="*80)
    ai_logger.info("AI Service Logger Initialized")
    ai_logger.info(f"Log file: {AI_LOG_FILE}")
    ai_logger.info("="*80)
    
    ts_logger.info("="*80)
    ts_logger.info("Talent Search Logger Initialized")
    ts_logger.info(f"Log file: {TALENT_SEARCH_LOG_FILE}")
    ts_logger.info("="*80)
    
    return {
        'ai': ai_logger,
        'talent_search': ts_logger,
        'app': app_logger
    }


# Convenience function to get specific logger
def get_ai_logger():
    """Get the AI service logger"""
    return logging.getLogger("ai_service")


def get_talent_search_logger():
    """Get the talent search logger"""
    return logging.getLogger("talent_search")
