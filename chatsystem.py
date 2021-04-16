import asyncio
import logging
from typing import List, Dict
from asyncio.tasks import FIRST_COMPLETED

from chatuser import ChatUser, send_all
from commands import execute


class ChatSystem:
    def __init__(self, HOST="127.0.0.1", PORT=9999) -> None:
        self.HOST = HOST
        self.PORT = PORT
        self.clients: List["ChatUser"] = []
        self.client_from_name: Dict[str, "ChatUser"] = {}
        return

    async def create_user(self, reader, writer) -> ChatUser:
        user = ChatUser(reader, writer, self)
        if not self.clients:  # first user to join gets mod privileges
            user.is_moderator = True
        self.clients.append(user)
        self.client_from_name[user.nick] = user
        message = f"{user.nick} has connected."
        logging.debug(message)
        await send_all(message, self)
        return user

    def create_handler(self):
        """Makes callback for client connection for start_server (primary function that runs the chat server).
        The callback can only have reader, writer as args, so need to have chat system in enclosure.
        """

        async def handle(reader, writer):

            # on connection
            user = await self.create_user(reader, writer)
            kicked = asyncio.create_task(user.is_kicked.wait())

            # chat loop
            while True:
                read_data = asyncio.create_task(user.read())
                done, _ = await asyncio.wait(
                    [kicked, read_data], return_when=FIRST_COMPLETED
                )
                if kicked in done:
                    break
                data = read_data.result()
                message = data.decode("utf8", "ignore").strip()
                if (
                    message == "" or message == "\x18'\x01\x03\x03"
                ):  # blanks and weird bytestrings
                    continue
                log_prefix = (
                    f"{user.addr} sent: "
                    if user.addr == user.nick
                    else f"{user.nick!r} {user.addr} sent: "
                )
                log_msg = log_prefix + f"{message!r}"
                logging.debug(log_msg)

                if message.startswith("/"):
                    cmd, *args = message.split()
                    if await execute(user, cmd, args, self) == "exit":
                        break
                else:
                    await user.send_from(message)

            # on exit
            user.writer.close()
            await user.writer.wait_closed()
            del self.client_from_name[user.nick]
            self.clients.remove(user)

            return

        return handle

    async def run_server(self):
        server = await asyncio.start_server(self.create_handler(), self.HOST, self.PORT)
        addr = server.sockets[0].getsockname()
        logging.debug(f"Serving on {addr}.")
        async with server:
            await server.serve_forever()
        return

