# Work with Python 3.6
import asyncio
import os
import importlib
import socket
from commands import client, permz, trigger
TOKEN = None

if socket.gethostname() == 'Mystery_machine':
    TOKEN = importlib.import_module('TOKEN').TOKEN
else:
    TOKEN = os.environ.get('TOKEN')

if not TOKEN:
    raise 'Not running localy and TOKEN is not an environment variable'

@client.event
async def on_message(msg):
    if msg.author == client.user: return
    await trigger(msg)

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
