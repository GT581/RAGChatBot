import logging
from .settings import LOG_FORMAT, LOG_LEVEL

def setup_logging():
    """Configure application-wide logging"""
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT
    )
    
    # Reduce noise from third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING) 