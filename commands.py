import logging
from random import randint, choice
from typing import List, TYPE_CHECKING
from chatuser import ChatUser, send_all

if TYPE_CHECKING:
    from chatsystem import ChatSystem


commands = {}
harassment_msgs = [
    "I don’t want to talk to you no more, you empty-headed animal-food-trough wiper.",
    "I fart in your general direction.",
    "Your mother was a hamster, and your father smelt of elderberries.",
]


def command(fn):
    """Decorator to register commands for chat.
    Command function name should be of the form cmd_blah.
    Commands are invoked by typing /{name of command} in chat.
    The function's docstring will be used as the help message for the command.
    """
    name = "/" + fn.__name__[4:]
    commands[name] = fn
    return


@command
async def cmd_nick(user: ChatUser, args: List[str], chat_system: "ChatSystem"):
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
        del chat_system.client_from_name[old_name.lower()]
        message = f"{old_name} has changed name to {nick}."
        logging.debug(message)
        await send_all(message, chat_system)
    return


@command
async def cmd_exit(user: ChatUser, args: List[str], chat_system: "ChatSystem"):
    """Exits the chat.
    """
    message = f"{user.nick} has left the chat."
    logging.debug(message)
    await send_all(message, chat_system)
    return "exit"


def die(sides: int, n_rolls: int = 1):
    return [str(randint(1, sides)) for _ in range(n_rolls)]


@command
async def cmd_roll(user: ChatUser, args: List[str], chat_system: "ChatSystem"):
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
        await send_all(message, chat_system)
        logging.debug(message)
    return


@command
async def cmd_block(user: ChatUser, args: List[str], chat_system: "ChatSystem"):
    """Blocks messages from a user.
    Example: "/block Mean Guy"
    """
    blockee = chat_system.client_from_name[" ".join(args).lower()]
    user.blocks.append(blockee)
    message = f"{user.nick} has blocked {blockee.nick}."
    await send_all(message, chat_system)
    return


@command
async def cmd_unblock(user: ChatUser, args: List[str], chat_system: "ChatSystem"):
    """Unblocks a user you've blocked.
    Example: "/unblock Not So Mean Guy"
    """
    blockee = chat_system.client_from_name[" ".join(args).lower()]
    user.blocks.remove(blockee)
    message = f"{user.nick} has unblocked {blockee.nick}."
    await send_all(message, chat_system)
    return


@command
async def cmd_help(user: ChatUser, args: List[str], chat_system: "ChatSystem"):
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
async def cmd_dm(user: ChatUser, args: List[str], chat_system: "ChatSystem"):
    """Directly messages another user.
    If the user's name has spaces, seperate name from message with "//".
    Examples:
    "/dm Johnny hi"
    "/dm Silly Goose // you're so silly!"
    """
    s = " ".join(args)
    if "//" in s:
        target_nick, msg = s.split("//")
        target = chat_system.client_from_name[target_nick.lower().strip()]
        message = f"{user.nick} whispers: {msg.strip()}"
    else:
        target_nick, *msg_list = s.split()
        target = chat_system.client_from_name[target_nick.lower()]
        message = f"{user.nick} whispers: {' '.join(msg_list).strip()}"
    await target.send(message)
    return


@command
async def cmd_harass(user: ChatUser, args: List[str], chat_system: "ChatSystem"):
    """Shame on you! What is wrong with you? Honestly, you need help.
    """
    target = chat_system.client_from_name[" ".join(args).lower()]
    msg = choice(harassment_msgs)
    await target.send(" >> " + f"{user.nick} whispers: {msg}")
    await user.send(" >> " + f"You whisper to {target.nick}: {msg}")
    return


@command
async def cmd_kick(user: ChatUser, args: List[str], chat_system: "ChatSystem"):
    """Boots user from chat.
    Only moderators can use.
    Example: "/kick Bad Guy"
    """
    if not user.is_moderator:
        await user.send(" >> " + "You are not a moderator.")
        return
    target = chat_system.client_from_name[" ".join(args).lower()]
    message = f"{user.nick} has kicked {target.nick} from chat."
    await send_all(message, chat_system)
    target.is_kicked.set()
    return


@command
async def cmd_mod(user: ChatUser, args: List[str], chat_system: "ChatSystem"):
    """Grants mod privileges to another user.
    Only moderators can use.
    Example: "/mod Good Guy Greg"
    """
    if not user.is_moderator:
        await user.send(" >> " + "You are not a moderator.")
        return
    target = chat_system.client_from_name[" ".join(args).lower()]
    message = f"{user.nick} has granted moderator privileges to {target.nick}."
    await send_all(message, chat_system)
    target.is_moderator = True
    return


@command
async def cmd_userlist(user: ChatUser, args: List[str], chat_system: "ChatSystem"):
    """Lists all users currently in chat.
    """
    message = f"{sorted(list(chat_system.client_from_name))}"
    await user.send(" >> " + message)
    return


async def execute(user: ChatUser, cmd: str, args: List[str], chat_system: "ChatSystem"):
    """Called when a user sends a message of form "/cmd blah blah".
    The message is split on spaces and unpacked as cmd, *args.
    Looks up '/cmd' in the commands dict and tries to return the result of calling it.
    """
    if fn := commands.get(cmd):
        try:
            return await fn(user, args, chat_system)
        except:
            message = "Sorry, something went wrong."
            await user.send(" >> " + message)
    else:
        message = f"{cmd!r} is not a valid command."
        await user.send(" >> " + message)
    return
