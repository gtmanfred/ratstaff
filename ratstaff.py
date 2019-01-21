# Work with Python 3.6
import discord
import dice
import os
import sys

TOKEN = os.environ.get('RATSTAFF_TOKEN')
if TOKEN is None:
    print("Please provide a valid RATSTAFF_TOKEN env.")
    sys.exit(1)

client = discord.Client()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    try:
        if message.content.startswith('%'):
            roller = message.author.mention
            request = message.content.strip("%")
            result = dice.roll("{0}+0d1".format(request))
            msg = '{roller}: {result} ({request})'.format(
                roller=roller, result=result, request=request)
            await client.send_message(message.channel, msg)
    except:
        # do nothing if we cannot roll for now
        pass
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)
