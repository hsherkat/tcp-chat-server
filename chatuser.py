from asyncio import StreamReader, StreamWriter, Event
from typing import List
from config import *


class ChatUser:
    def __init__(
        self, reader: StreamReader, writer: StreamWriter, chat_system: ChatSystem
    ):
        self.reader = reader
        self.writer = writer
        self.chat_system = chat_system
        self.addr = writer.get_extra_info("peername")
        self.blocks: List[ChatUser] = []
        self._nick = None
        self.is_moderator = False
        self.is_kicked = Event()
        return

    @property
    def nick(self):
        return self._nick if (self._nick is not None) else self.addr

    @nick.setter
    def nick(self, name):
        if not all(word.isalnum() for word in name.split()):
            raise ValueError
        if name in self.chat_system.client_from_name:
            raise KeyError
        self._nick = name
        self.chat_system.client_from_name[name] = self
        return

    async def send(self, message: str):
        msg = f"{message}\n\r".encode()
        self.writer.write(msg)
        await self.writer.drain()
        return

    async def send_from(self, message: str):
        msg = f"{self.nick}: {message}"
        for user in self.chat_system.clients:
            if self in user.blocks or user == self:
                continue
            await user.send(msg)
        return

    async def read(self):
        return await self.reader.read(300)


async def send_all(message: str, chat_system: ChatSystem):
    for user in chat_system.clients:
        await user.send(" >> " + message)
    return
