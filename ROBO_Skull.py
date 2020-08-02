# Work with Python 3.6
import os
import importlib
import socket
from commands_module import bot
#ressolving token
TOKEN = None
if socket.gethostname() == 'Mystery_machine':
    TOKEN = importlib.import_module('TOKEN').TOKEN
else:
    TOKEN = os.environ.get('TOKEN')
if not TOKEN:
    raise 'Not running localy and TOKEN is not an environment variable'

bot.run(TOKEN)