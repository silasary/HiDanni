import datetime
import re
import sys
import random
from typing import Dict

import discord
from discord.errors import Forbidden
from discord.message import Message
from discord.user import User

from shared import configuration
from shared.limited_dict import LimitedSizeDict

class Bot:
    def __init__(self) -> None:
        self.client = discord.Client()
        self.cache: Dict[User, str] = LimitedSizeDict(size_limit=500)
        t = datetime.timedelta(hours=2)
        self.next_meow = datetime.datetime.now() + t

    def init(self) -> None:
        self.client.run(configuration.get('token'))

BOT = Bot()
REGEX_IM = r"\b(?:I'?m|I ?am)\W+([\w\W]+)"
STRIP_CHARS = ' .!,)?*'
REGEX_SUPERLATIVE = r'((very|really|super) ?)*'

@BOT.client.event
async def on_message(message: Message) -> None:
    if message.author == BOT.client.user:
        return
    m = re.search(REGEX_IM, message.clean_content, re.IGNORECASE)
    if not m:
        m = re.search(REGEX_IM, BOT.cache.get(message.author, '') + ' ' + message.clean_content, re.IGNORECASE)
        BOT.cache[message.author] = message.clean_content
    if m:
        name = m.group(1)
        name = name.strip(STRIP_CHARS)
        name = make_positive(name)
        name = name[0].upper() + name[1:]
        if len(name) > 32:
            name = name.rsplit('.', 1)[0]
            name = name.strip(STRIP_CHARS)
        nname = name
        if len(name) > 32:
            nname = name[:31]
            nname = nname.strip(STRIP_CHARS)
        # Discord says that Server Admin is immune 😭
        try:
            await BOT.client.change_nickname(message.author, nname)
        except discord.Forbidden:
            pass
        await BOT.client.send_message(message.channel, f"Hi {name}, I'm Danni")
        return

    if message.content == '!restartbot':
        await BOT.client.send_message(message.channel, 'Rebooting!')
        await BOT.client.logout()
        sys.exit()

    diff = datetime.datetime.now().timestamp() - BOT.next_meow.timestamp()
    if diff > 0:
        await BOT.client.send_message(message.channel, 'meow')
        t = datetime.timedelta(days=random.randrange(2,7), hours=random.randrange(6,23))
        BOT.next_meow = datetime.datetime.now() + t
        return

def make_positive(nname: str) -> str:
    nname = re.sub(r'^' + REGEX_SUPERLATIVE + r'not cute', 'really cute', nname, flags=re.I)
    nname = re.sub(r'^' + REGEX_SUPERLATIVE + r'(f?ugly|hideous|garbage)', 'beautiful', nname, flags=re.I)
    nname = re.sub(r'^' + REGEX_SUPERLATIVE + r'gross', 'beautiful', nname, flags=re.I)
    nname = re.sub(r'^' + REGEX_SUPERLATIVE + r'awful', 'lovely', nname, flags=re.I)
    nname = re.sub(r'^' + REGEX_SUPERLATIVE + r'dumb', 'brilliant', nname, flags=re.I)
    nname = re.sub(r'^' + REGEX_SUPERLATIVE + r'useless', 'valuable', nname, flags=re.I)

    return nname

@BOT.client.event
async def on_ready() -> None:
    print('Logged in as {username} ({id})'.format(username=BOT.client.user.name, id=BOT.client.user.id))
    print('Connected to {0}'.format(', '.join([server.name for server in BOT.client.servers])))
    print('--------')


@BOT.client.event
async def on_server_join(server: discord.Server) -> None:
    await BOT.client.send_message(server.default_channel, "Hi everyone! I'm a terrible idea given form")

def init() -> None:
    BOT.init()

if __name__ == "__main__":
    init()
