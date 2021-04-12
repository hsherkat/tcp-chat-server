import asyncio
from asyncio.tasks import FIRST_COMPLETED

from config import *
from chatuser import ChatUser, send_all
from commands import execute


async def initial_setup(reader, writer, chat_system: ChatSystem) -> ChatUser:
    user = ChatUser(reader, writer, chat_system)
    if not chat_system.clients:  # first user to join gets mod privileges
        user.is_moderator = True
    chat_system.clients.append(user)
    chat_system.client_from_name[user.nick] = user
    message = f"{user.nick} has connected."
    logging.debug(message)
    await send_all(message, chat_system)
    return user


async def handle(reader, writer):
    global chat_system

    # on connection
    user = await initial_setup(reader, writer, chat_system)
    kicked = asyncio.create_task(user.is_kicked.wait())

    # chat loop
    while True:
        read_data = asyncio.create_task(user.read())
        done, _ = await asyncio.wait([kicked, read_data], return_when=FIRST_COMPLETED)
        if kicked in done:
            break
        data = read_data.result()
        message = data.decode("utf8", "ignore").strip()
        prefix = (
            f"{user.addr} sent: "
            if user.addr == user.nick
            else f"{user.nick!r} {user.addr} sent: "
        )
        log_msg = prefix + f"{message!r}"
        logging.debug(log_msg)

        if message.startswith("/"):
            cmd, *args = message.split()
            if await execute(user, cmd, args, chat_system) == "exit":
                break
        else:
            await user.send_from(message)

    # on exit
    user.writer.close()
    await user.writer.wait_closed()
    del chat_system.client_from_name[user.nick]
    chat_system.clients.remove(user)

    return


async def main():
    server = await asyncio.start_server(handle, chat_system.HOST, chat_system.PORT)
    addr = server.sockets[0].getsockname()
    logging.debug(f"Serving on {addr}.")
    async with server:
        await server.serve_forever()


try:
    asyncio.run(main())
except KeyboardInterrupt:
    logging.debug("Server shut down.")
