import socket
import logging
from typing import Optional
import os


import discord
from discord.ext import commands


from discotools import perms
from config import PREFIX_LOCAL, PREFIX_HOST, HOSTS, LOGS_CHANNEL


logging.basicConfig(level=logging.INFO)

TOKEN = None
if socket.gethostname() in HOSTS:
    import importlib
    TOKEN = importlib.import_module('TOKEN').TOKEN
    del importlib

    prefix = PREFIX_LOCAL
else:
    TOKEN = os.environ.get('TOKEN')

    prefix = PREFIX_HOST

if not TOKEN:
    raise Exception('Not running localy and TOKEN is not an environment variable')

intents = discord.Intents(guilds=True, members=True, emojis=True, messages=True, reactions=True)
bot = commands.Bot(command_prefix=prefix, intents=intents)

class Setup(commands.Cog, command_attrs={'hidden': True}):
    """Module management commands for development purposes."""
    def __init__(self):
        super().__init__()
        self.last_reload = None


    @commands.command(aliases=['ext'])
    @perms(5)
    async def extensions(self, ctx: commands.Context):
        """Show loaded extensions"""
        cont = 'Enabled modules:\n' + ('\n'.join(bot.extensions) or 'None')
        await ctx.send(cont)


    @commands.command()
    @perms(5)
    async def load(self, ctx: commands.Context, arg: str):
        """Loads an extension"""
        await ctx.message.add_reaction('☑️')
        if '.' in arg: ext = arg
        else: ext = f'Commands.{arg}'
        await ctx.send(f'Loading {ext}...', delete_after=5.0)
        print(f'Loading {ext}...')
        bot.load_extension(ext)


    @commands.command()
    @perms(5)
    async def reload(self, ctx: commands.Context, arg: Optional[str]):
        """Reloads an extension or all extensions"""
        if arg is None:
            if self.last_reload is not None:
                arg = self.last_reload
            else:
                await ctx.send('No module cached.')
                return
        await ctx.message.add_reaction('🔄')
        if arg == 'all':
            await ctx.send('Reloading all modules...', delete_after=5.0)
            #bot.extensions gets modified on reload so we have to pre-assign all loaded extensions
            [bot.reload_extension(ext) for ext in (ext for ext in bot.extensions)]
            return
        if '.' in arg: ext = arg
        else: ext = f'Commands.{arg}'
        if ext not in bot.extensions:
            await ctx.send(f'No extension "{ext}" found.')
            return
        self.last_reload = ext
        await ctx.send(f'Reloading {ext}...', delete_after=5.0)
        print(f'Reloading {ext}...')
        bot.reload_extension(ext)


    @commands.command()
    @perms(5)
    async def unload(self, ctx: commands.Context, arg: str):
        """Unload an extension"""
        await ctx.message.add_reaction('🚀')
        if '.' in arg: ext = arg
        else: ext = f'Commands.{arg}'
        await ctx.send(f'Unloading {ext}...', delete_after=5.0)
        print(f'Unloading {ext}...')
        bot.unload_extension(ext)


    @commands.command(aliases=['sd'])
    @perms(5)
    async def shutdown(self, ctx: commands.Context):
        """Terminates the bot connection."""
        await ctx.send('I will be back')
        await bot.logout()


    @commands.command()
    async def test(self, ctx: commands.Context, *args):
        count = len(args)
        await ctx.send(f"{count} argument{'s' * (count != 1)}{':' * bool(count)} {', '.join(args)}")


bot.add_cog(Setup())
disabled_modules = {'Testing'}

for file in os.scandir('Commands'):
    name, ext = os.path.splitext(file.name)

    if ext == '.py' and name not in disabled_modules:
        bot.load_extension(f'Commands.{name}')


if prefix == PREFIX_HOST:
    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.errors.CommandOnCooldown):
            await ctx.send(error, delete_after=5.0)
        elif isinstance((error, commands.errors.BadArgument)):
            await ctx.send('Invalid argument type passed.', delete_after=5.0)
        else:
            print(error, '\n', ctx)
            await bot.get_channel(LOGS_CHANNEL).send(f'{error}\n{ctx}')

@bot.event
async def on_ready():
    print(f'{bot.user.name} is here to take over the world')
    print('----------------')
    if prefix == PREFIX_HOST:
        await bot.get_channel(LOGS_CHANNEL).send("I'm back online")
    await bot.change_presence(activity=discord.Activity(name='grass grow', type=3))

bot.run(TOKEN)
