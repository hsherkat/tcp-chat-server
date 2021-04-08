import sys
import logging
from typing import List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from chatuser import ChatUser


logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.DEBUG,
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler("chat_logs.txt"), logging.StreamHandler(sys.stdout)],
)


HOST = "127.0.0.1"
PORT = 9999


commands = {}
clients: List["ChatUser"] = []
client_from_name: Dict[str, "ChatUser"] = {}


harassment_msgs = [
    "I don’t want to talk to you no more, you empty-headed animal-food-trough wiper.",
    "I fart in your general direction.",
    "Your mother was a hamster, and your father smelt of elderberries.",
]