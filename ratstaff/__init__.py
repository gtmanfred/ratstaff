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

    async def roll_dice(self, message, request, label=None, delete=False):
        roller = message.author.mention
        tray = dicetray.Dicetray(request)
        try:
            result = tray.roll()
        except sly.lex.LexError:
            return
        await message.channel.send(
            f'{roller}: :game_die:\n'
            f'**{label or "Result"}**: {tray.format(verbose=True)}\n'
            f'**Total**: {result}'
        )
        if delete is True:
            self.loop.create_task(message.delete())

    async def multi_roll_dice(self, message, request, count, delete=False):
        roller = message.author.mention
        tray = dicetray.Dicetray(request)
        response = [f'{roller}: Rolling {count} iterations...']
        total = 0
        try:
            for _ in range(count):
                result = tray.roll()
                total += result
                response.append(f'{tray.format(verbose=True)} => {result}')
        except sly.lex.LexError:
            return
        response.append(f'**Total**: {total}')
        await message.channel.send('\n'.join(response))
        if delete is True:
            self.loop.create_task(message.delete())

    async def on_message(self, message):
        if message.author == self.user:
            return

        content = message.content.lstrip('%')
        if content.startswith('roll '):
            _, request, *label = content.split(' ')
            label = ' '.join(label)
            self.loop.create_task(
                self.roll_dice(message, request, label=label, delete=True),
            )
        elif content.startswith('multiroll') or content.startswith('rr'):
            _, number, roll = content.split(' ', 2)
            self.loop.create_task(
                self.multi_roll_dice(message, roll, int(number))
            )
        elif content[0].isdigit():
            _, request, *label = content.split(' ')
            label = ' '.join(label)
            self.loop.create_task(self.roll_dice(message, request, label=label))

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')


def _setup_logging(level):
    log.setLevel(getattr(logging, level.upper(), 'INFO'))
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            '%(asctime)s:%(levelname)s:%(name)s: %(message)s',
        ),
    )
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
