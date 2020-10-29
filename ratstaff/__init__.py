# -*- coding: utf-8 -*-
import asyncio
import logging
import sys

import click
import discord
import dicetray
import sly.lex

log = logging.getLogger('discord')


class RatStaff(discord.Client):
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        super().__init__()

    async def roll_dice(self, message, request):
        roller = message.author.mention
        tray = dicetray.Dicetray(request)
        try:
            result = tray.roll()
        except sly.lex.LexError:
            return
        await message.channel.send(
            f'{roller}: {tray.format(verbose=True)} => {result}',
        )

    async def on_message(self, message):
        if message.author == self.user:
            return

        content = message.content.lstrip('%')
        if content.startswith('roll '):
            self.loop.create_task(self.roll_dice(message, content[5:]))
            self.loop.create_task(message.delete())
        elif content[0].isdigit():
            self.loop.create_task(self.roll_dice(message, content))

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')


def _setup_logging(level):
    log.setLevel(getattr(logging, level.upper(), 'INFO'))
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    log.addHandler(handler)


@click.command()
@click.option('token', '--token', '-t', required=True, envvar='RATSTAFF_TOKEN')
@click.option(
    'level', '--log-level', '-l',
    type=click.Choice(['INFO', 'DEBUG', 'WARNING', 'CRITICAL']),
    default='INFO',
    help='level of logs to print out',
)
def main(token, level):
    _setup_logging(level)
    RatStaff().run(token)
