import asyncio
import logging
import sys

from chatsystem import ChatSystem


logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.DEBUG,
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler("chat_logs.txt"), logging.StreamHandler(sys.stdout)],
)


chat_system = ChatSystem()

try:
    asyncio.run(chat_system.run_server())
except KeyboardInterrupt:
    logging.debug("Server shut down.")
