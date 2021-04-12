import asyncio
from typing import List
from config import *


class ChatUser:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer
        self.addr = writer.get_extra_info("peername")
        self.blocks: List[ChatUser] = []
        self._nick = None
        self.is_moderator = False
        self.is_kicked = asyncio.Event()
        return

    @property
    def nick(self):
        return self._nick if (self._nick is not None) else self.addr

    @nick.setter
    def nick(self, name):
        if not all(word.isalnum() for word in name.split()):
            raise ValueError
        if name in client_from_name:
            raise KeyError
        self._nick = name
        client_from_name[name] = self
        return

    async def send(self, message: str):
        msg = f"{message}\n\r".encode()
        self.writer.write(msg)
        await self.writer.drain()
        return

    async def send_from(self, message: str):
        msg = f"{self.nick}: {message}"
        for user in clients:
            if self in user.blocks or user == self:
                continue
            await user.send(msg)
        return

    async def read(self):
        return await self.reader.read(300)


async def send_all(message: str):
    for user in clients:
        await user.send(" >> " + message)
    return
