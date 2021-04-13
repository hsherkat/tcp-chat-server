import sys
import logging
from typing import List, Dict, TYPE_CHECKING

"""Just sets up the logger for all the different modules.
Also imports typing stuff.
"""

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.DEBUG,
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler("chat_logs.txt"), logging.StreamHandler(sys.stdout)],
)

