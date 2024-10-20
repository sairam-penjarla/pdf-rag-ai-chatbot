import os
import sys
import logging
from time import time
from datetime import datetime

# Define the format for log messages
logging_str = "[%(asctime)s: %(levelname)s: %(message)s]"

logging.basicConfig(
    format=logging_str,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("SQL Agent")

logger.setLevel(logging.INFO)