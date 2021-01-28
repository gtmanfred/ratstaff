# -*- coding: utf-8 -*-
import asyncio
import logging
import textwrap
import sys

import click
import discord
import dicetray.parser
import sly.lex

log = logging.getLogger('discord')


class RatStaff(discord.Client):
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        super().__init__()

    @staticmethod
    def roll(request):
        tray = dicetray.Dicetray(request)
        try:
            result = tray.roll()
        except (
            sly.lex.LexError,
            dicetray.MaxDiceExceeded,
            dicetray.parser.ParserError,
        ):
            return False, None
        return result, tray


    async def roll_dice(self, message, request, delete=False):
        if 'd' not in request:
            return
        log.debug('rolling dice %s', request)
        label = ''
        roller = message.author.mention
        result, tray = self.roll(request)
        while result is False and request:
            request, next_label = request.rsplit(' ', 1)
            label = f'{next_label} {label}'
            result, tray = self.roll(request)
            log.debug('Roll response %s: result=%s,tray=%s', request, result, tray)
        if result is False:
            log.debug('unable to parse roll: %s', message.content)
            return

        data = textwrap.shorten(
            tray.format(verbose=True, markdown=True),
            width=1500,
            placeholder='...',
        )
        await message.channel.send(
            f'{roller}: :game_die:\n'
            f'**{label or "Result"}**: {data}\n'
            f'**Total**: {result}'
        )
        if delete is True:
            log.debug('Deleting message: %s', message)
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
                response.append(f'{tray.format(verbose=True, markdown=True)} => {result}')
        except (
            sly.lex.LexError,
            dicetray.MaxDiceExceeded,
            dicetray.parser.ParserError,
        ):
            return
        response.append(f'**Total**: {total}')
        await message.channel.send('\n'.join(response))
        if delete is True:
            self.loop.create_task(message.delete())

    async def on_message(self, message):
        if message.author == self.user or not message.content:
            return

        content = message.content.lstrip('%/!@#.')
        if content.startswith('roll '):
            _, *request = content.split(' ')
            request = ' '.join(request)
            self.loop.create_task(
                self.roll_dice(message, request, delete=True),
            )
        elif content.startswith('multiroll') or content.startswith('rr'):
            _, number, roll = content.split(' ', 2)
            self.loop.create_task(
                self.multi_roll_dice(message, roll, int(number))
            )
        elif self._check_msg_for_roll(content):
            self.loop.create_task(
                self.roll_dice(message, content),
            )

    @staticmethod
    def _check_msg_for_roll(content):
        if content[0] == 'd':
            return True
        if content[0].isdigit() and 'd' in content.split(' ', 1)[0]:
            return True
        return False

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
    envvar='LOGLEVEL',
    default='INFO',
    help='level of logs to print out',
)
def main(token, level):
    _setup_logging(level)
    RatStaff().run(token)
