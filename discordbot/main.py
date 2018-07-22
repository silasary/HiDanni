import sys
import re

from typing import Dict

import discord
from discord.message import Message
from discord.errors import Forbidden

from shared import configuration

class Bot:
    def __init__(self) -> None:
        self.client = discord.Client()

    def init(self) -> None:
        self.client.run(configuration.get('token'))

BOT = Bot()

@BOT.client.event
async def on_message(message: Message) -> None:
    if message.author == BOT.client.user:
        return
    m = re.search(r"\b(?:I'?m|I am)\W+([\w\W]+)", message.content, re.IGNORECASE)
    if m:
        name = m.group(1)
        name = name.strip(' .!,)').title()
        if len(name) > 32:
            name = name.rsplit('.', 1)[0]
            name = name.strip(' .!,')
        nname = name
        if len(name) > 32:
            nname = name[:31]
            nname = nname.strip(' .!,')
        # Discord says that Server Admin is immune 😭
        try:
            await BOT.client.change_nickname(message.author, nname)
        except discord.Forbidden:
            pass
        await BOT.client.send_message(message.channel, f"Hi {name}, I'm Danni")

    if message.content == '!restartbot':
        await BOT.client.send_message(message.channel, 'Rebooting!')
        await BOT.client.logout()
        sys.exit()

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
