import datetime
import os
import random
import re
import sys
from typing import Dict

import discord
from discord import Emoji, Message, Reaction, User
from discord.errors import Forbidden
import requests

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

    def get_yeet(self) -> Emoji:
        yeets = []
        for emoji in self.client.emojis:
            if emoji.name.startswith('yeet'):
                yeets.append(emoji)
        if not yeets:
            return None
        random.shuffle(yeets)
        return yeets[0]

BOT = Bot()
REGEXP_I = r'[Iℹ🇮]'
REGEXP_APOS = r"['’\" ]?"
REGEXP_M = r'[m♏🇲]'
REGEXP_AM = r'(am|is)'

REGEX_IM = r"\b(" + REGEXP_I + REGEXP_APOS + REGEXP_M + r"|" + REGEXP_I + r"\W" + REGEXP_AM +  r")\W+(?P<name>[\w\W]+)"
REGEX_AM = r''
STRIP_CHARS = ' .!,)?*~|'
REGEX_SUPERLATIVE = r'((very|really|super) ?)*'

@BOT.client.event
async def on_message(message: Message) -> None:
    await slurp_emoji(message)
    if message.author == BOT.client.user:
        return
    m = re.search(REGEX_IM, message.clean_content, re.IGNORECASE)
    if not m:
        m = re.search(REGEX_IM, BOT.cache.get(message.author, '') + ' ' + message.clean_content, re.IGNORECASE)
        BOT.cache[message.author] = message.clean_content
    if m:
        i_is = m.group(1).endswith(' is')
        name = m.group('name')
        name = name.strip(STRIP_CHARS)
        name = make_positive(name)
        name = name[0].upper() + name[1:]
        if len(name) > 32:
            splits = name.rsplit('.')
            while len(splits) > 1 and len('.'.join(splits[:-1])) > 32:
                splits = splits[:-1]
            name = '.'.join(splits)
            name = name.strip(STRIP_CHARS)
        nname = name
        if len(name) > 32:
            nname = name[:31]
            nname = nname.strip(STRIP_CHARS)
        # Discord says that Server Admin is immune 😭
        try:
            await message.author.edit(nick=nname)
        except discord.Forbidden:
            pass
        if i_is:
            await message.channel.send(f"Yes, you are {name}")
            return

        await message.channel.send(f"Hi {name}, I'm Danni")
        return

    if message.content.lower() == 'owo' and message.author.id == 225711751071662082:
        await message.channel.send(file=discord.File('tove.jpg', 'tove.jpg'))

    if message.content == '!restartbot':
        await message.channel.send('Rebooting!')
        await BOT.client.logout()
        sys.exit()

    if message.content == '!meow':
        await message.channel.send('No you')

    if message.content.lower() == 'yeet':
        yeet = BOT.get_yeet()
        if yeet:
            await message.channel.send(str(yeet))

    diff = datetime.datetime.now().timestamp() - BOT.next_meow.timestamp()
    if diff > 0:
        await message.channel.send('meow')
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
    print('Connected to {0}'.format(', '.join([server.name for server in BOT.client.guilds])))
    print('--------')


@BOT.client.event
async def on_guild_join(guild: discord.Guild) -> None:
    await guild.default_channel.send("Hi everyone! I'm a terrible idea given form")

@BOT.client.event
async def on_reaction_add(reaction: Reaction, author: User) -> None:
        c = reaction.count
        if reaction.me:
            c = c - 1
        if reaction.message.author == BOT.client.user:
            if c > 0 and not reaction.custom_emoji and reaction.emoji == "❎":
                await reaction.message.delete()

@BOT.client.event
async def on_member_update(before: discord.Member, after: discord.Member) -> None:

    pass

async def slurp_emoji(message: Message) -> None:
    emoji = re.findall(r'<:([^\d>]+):(\w+)>', message.content)
    print(repr(emoji))
    if not os.path.exists('emoji'):
        os.mkdir('emoji')
    for e in emoji:
        name = e[0]
        e_id = e[1]
        path = os.path.join('emoji', name + '.png')
        if not os.path.exists(path):
            response = requests.get(f'https://cdn.discordapp.com/emojis/{e_id}.png')
            with open(path, mode='wb') as fout:
                for chunk in response.iter_content(1024):
                    fout.write(chunk)

def init() -> None:
    BOT.init()

if __name__ == "__main__":
    init()
