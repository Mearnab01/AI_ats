import logging
import sys
from pathlib import Path

# Create a logs directory if it doesn't exist
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"

# Define the format: Time - File/Module Name - Level - Message
LOG_FORMAT = "%(asctime)s - [%(name)s] - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logger(module_name: str):
    """
    Configures a logger that outputs to both a file (app.log) and the console.
    """
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.INFO)

    # Prevent duplicate logs if the logger is already configured
    if not logger.handlers:
        # 1. File Handler (saves to backend/logs/app.log)
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
        logger.addHandler(file_handler)

        # 2. Console Handler (so you can see it in your terminal while developing)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
        logger.addHandler(console_handler)

    return logger