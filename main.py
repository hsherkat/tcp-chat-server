import asyncio

from config import *
from chatsystem import ChatSystem


chat_system = ChatSystem()

try:
    asyncio.run(chat_system.run_server())
except KeyboardInterrupt:
    logging.debug("Server shut down.")
