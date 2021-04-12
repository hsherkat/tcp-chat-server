from random import randint, choice
from config import *
from chatuser import ChatUser, send_all


def command(fn):
    """Decorator to register commands for chat.
    Command function name must be of the form cmd_blah.
    Commands are invoked by typing /{name of command} in chat.
    The function's docstring will be used as the help message for the command.
    """
    name = "/" + fn.__name__[4:]
    commands[name] = fn
    return


@command
async def cmd_nick(user: ChatUser, args: List[str]):
    """Changes your username.
    Example: "/nick Cool Guy"
    """
    old_name = user.nick
    nick = " ".join(args).strip()
    try:
        user.nick = nick
    except ValueError:
        await user.send(" >> " + "Usernames must be alphanumeric.")
    except KeyError:
        await user.send(" >> " + f"Sorry, someone is already named {nick!r}.")
    else:
        del client_from_name[old_name]
        message = f"{old_name} has changed name to {nick}."
        logging.debug(message)
        await send_all(message)
    return


@command
async def cmd_exit(user: ChatUser, args: List[str]):
    """Exits the chat.
    """
    message = f"{user.nick} has left the chat."
    logging.debug(message)
    await send_all(message)
    return "exit"


def die(sides: int, n_rolls: int = 1):
    return [str(randint(1, sides)) for _ in range(n_rolls)]


@command
async def cmd_roll(user: ChatUser, args: List[str]):
    """Rolls some dice!
    Example: "/roll 1d20 2d4" 
    """
    try:
        rolls = []
        for dice in args:
            n_rolls, sides = map(int, dice.split("d"))
            rolls.extend(die(sides, n_rolls))
    except:
        raise ValueError
    else:
        dice_str = " ".join(args)
        results = " ".join(rolls)
        message = f"{user.nick} just rolled {dice_str} and got: {results}"
        await send_all(message)
        logging.debug(message)
    return


@command
async def cmd_block(user: ChatUser, args: List[str]):
    """Blocks messages from a user.
    Example: "/block Mean Guy"
    """
    blockee = client_from_name[" ".join(args)]
    user.blocks.append(blockee)
    message = f"{user.nick} has blocked {blockee.nick}."
    await send_all(message)
    return


@command
async def cmd_unblock(user: ChatUser, args: List[str]):
    """Unblocks a user you've blocked.
    Example: "/unblock Not So Mean Guy"
    """
    blockee = client_from_name[" ".join(args)]
    user.blocks.remove(blockee)
    message = f"{user.nick} has unblocked {blockee.nick}."
    await send_all(message)
    return


@command
async def cmd_help(user: ChatUser, args: List[str]):
    """Haha, so meta!
    """
    if not args:
        message = f"The commands are:\n\r{sorted(list(commands))!r}"
        await user.send(" >> " + message)
        message = f'Type "/help {{command name}}" for help on a command.'
        await user.send(" >> " + message)
    else:
        cmd = commands["/" + " ".join(args)]
        lines = cmd.__doc__.strip().split("\n")
        message = "\n\r".join([" >> " + line.strip() for line in lines])
        await user.send(message)
    return


@command
async def cmd_dm(user: ChatUser, args: List[str]):
    """Directly messages another user.
    If the user's name has spaces, seperate name from message with "//".
    Examples:
    "/dm Johnny hi"
    "/dm Silly Goose // you're so silly!"
    """
    s = " ".join(args)
    if "//" in s:
        target_nick, msg = s.split("//")
        target = client_from_name[target_nick.strip()]
        message = f"{user.nick} whispers: {msg.strip()}"
    else:
        target_nick, *msg_list = s.split()
        target = client_from_name[target_nick]
        message = f"{user.nick} whispers: {' '.join(msg_list).strip()}"
    await target.send(message)
    return


@command
async def cmd_harass(user: ChatUser, args: List[str]):
    """Shame on you! What is wrong with you? Honestly, you need help.
    """
    target = client_from_name[" ".join(args)]
    msg = choice(harassment_msgs)
    await target.send(" >> " + f"{user.nick} whispers: {msg}")
    await user.send(" >> " + f"You whisper to {target.nick}: {msg}")
    return


@command
async def cmd_kick(user: ChatUser, args: List[str]):
    """Boots user from chat.
    Only moderators can use.
    Example: "/kick Bad Guy"
    """
    if not user.is_moderator:
        await user.send(" >> " + "You are not a moderator.")
        return
    target = client_from_name[" ".join(args)]
    message = f"{user.nick} has kicked {target.nick} from chat."
    await send_all(message)
    target.is_kicked.set()
    return


@command
async def cmd_mod(user: ChatUser, args: List[str]):
    """Grants mod privileges to another user.
    Only moderators can use.
    Example: "/mod Good Guy Greg"
    """
    if not user.is_moderator:
        await user.send(" >> " + "You are not a moderator.")
        return
    target = client_from_name[" ".join(args)]
    message = f"{user.nick} has granted moderator privileges to {target.nick}."
    await send_all(message)
    target.is_moderator = True
    return


@command
async def cmd_userlist(user: ChatUser, args: List[str]):
    """Lists all users currently in chat.
    """
    message = f"{sorted(list(client_from_name))}"
    await user.send(" >> " + message)
    return


async def execute(user: ChatUser, cmd: str, args: List[str]):
    if fn := commands.get(cmd):
        try:
            return await fn(user, args)
        except:
            message = "Sorry, something went wrong."
            await user.send(" >> " + message)
    else:
        message = f"{cmd!r} is not a valid command."
        await user.send(" >> " + message)
    return
