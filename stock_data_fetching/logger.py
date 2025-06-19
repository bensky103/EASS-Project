import logging
from pythonjsonlogger import jsonlogger
from stock_data_fetching.config import settings
import sys

def setup_logger():
    logger = logging.getLogger(settings.SERVICE_NAME)
    logger.setLevel(settings.LOG_LEVEL)

    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    
    # Create formatters and add it to handlers
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = jsonlogger.JsonFormatter(log_format)
    console_handler.setFormatter(formatter)
    
    # Add handlers to the logger
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger() 