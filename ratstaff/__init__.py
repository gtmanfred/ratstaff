# -*- coding: utf-8 -*-
import asyncio
import click
import discord
import xdice


class RatStaff(discord.Client):
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        super(RatStaff, self).__init__(loop=self.loop)

    async def roll_dice(self, message):
        roller = message.author.mention
        request = message.content.strip('%')
        result = xdice.roll(f'{request}')
        await self.send_message(message.channel,
                                f'{roller}: {result.format()} => {result}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith('%'):
            asyncio.ensure_future(self.roll_dice(message), loop=self.loop)

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')


@click.command()
@click.option('token', '--token', '-t', required=True, envvar='RATSTAFF_TOKEN')
def main(token):
    rat = RatStaff()
    rat.run(token)
