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


class ChatSystem:
    def __init__(self, HOST="127.0.0.1", PORT=9999) -> None:
        self.HOST = HOST
        self.PORT = PORT
        self.clients: List["ChatUser"] = []
        self.client_from_name: Dict[str, "ChatUser"] = {}
        return

