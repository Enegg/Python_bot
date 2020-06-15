# Work with Python 3.6
import discord
import asyncio
import json
import requests
import os
import importlib
import socket
from config import authorid, abbreviations
from commands import prefix, client, prefix_handler, trigger, purge, roll_handler, permz, epix_command, channels, stats
TOKEN = None

if socket.gethostname() == 'Mystery_machine':
    TOKEN = importlib.import_module('TOKEN').TOKEN
else:
    TOKEN = os.environ.get('TOKEN')

if not TOKEN:
    raise 'Not running localy and TOKEN is not an environment variable'

@client.event
async def on_message(message):
    if message.author == client.user: return
    channel = message.channel

    if trigger(message, 'roles'): await channel.send('`{}`'.format(message.author.roles))

    if trigger(message, 'ping'): await channel.send('Pong! {}ms'.format(round(client.latency * 1000)))

    if trigger(message, 'pig'): await channel.send('🐷')

    if trigger(message, 'roll'): await channel.send(roll_handler(message))

    if trigger(message, 'wot') and permz(message) > 1: await channel.send(channels(prefix_handler(message)[1][0]))

    if trigger(message, 'purge') and permz(message) > 0: await purge(message)

    if trigger(message, 'sd') and permz(message) > 1:
        await channel.send('I will be back')
        await client.logout()

    if trigger(message, 'say') and permz(message) > 2: await epix_command(message)

    if trigger(message, 'stats'): await stats(message)

@client.event
async def on_ready():
    print(client.user.name + ' is here to take over the world')
    print('----------------')

loop = asyncio.get_event_loop()
task = loop.create_task(client.run(TOKEN))
try:
    loop.run_until_complete(task)
except KeyboardInterrupt:
    pass
    #loop.run_until_complete(logout())
finally:
    loop.close()
