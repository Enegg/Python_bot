import discord
from discord.ext import commands
import socket
from functions import perms
from config import prefix_local, prefix_host

TOKEN = None
if socket.gethostname() == 'Mystery_machine':
    import importlib
    TOKEN = importlib.import_module('TOKEN').TOKEN

    prefix = prefix_local
else:
    from os import environ
    TOKEN = environ.get('TOKEN')

    prefix = prefix_host

if not TOKEN: raise Exception('Not running localy and TOKEN is not an environment variable')

bot = commands.Bot(command_prefix=prefix)

class Setup(commands.Cog):
    def __init__(self):
        super().__init__()
        self.last_reload = None

    @commands.group(hidden=True, brief='Extensions manager')
    @perms(5)
    async def ext(self, ctx):
        if ctx.invoked_subcommand is None:
            cont = 'Enabled modules:\n' + ('\n'.join(x for x in bot.extensions) or 'None')
            await ctx.send(cont)

    @ext.command()
    @perms(5)
    async def load(self, ctx, arg):
        await ctx.message.add_reaction('☑️')
        if '.' in arg: ext = arg
        else: ext = 'Commands.' + arg
        await ctx.send(f'Loading {ext}...', delete_after=5.0)
        print(f'Loading {ext}...')
        bot.load_extension(ext)

    @commands.command(hidden=True)
    @perms(5)
    async def reload(self, ctx, arg=None):
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
        else: ext = 'Commands.' + arg
        if ext not in bot.extensions:
            await ctx.send(f'No extension "{ext}" found.')
            return
        self.last_reload = ext
        await ctx.send(f'Reloading {ext}...', delete_after=5.0)
        print(f'Reloading {ext}...')
        bot.reload_extension(ext)

    @ext.command()
    @perms(5)
    async def unload(self, ctx, arg):
        await ctx.message.add_reaction('🚀')
        if '.' in arg: ext = arg
        else: ext = 'Commands.' + arg
        await ctx.send(f'Unloading {ext}...', delete_after=5.0)
        print(f'Unloading {ext}...')
        bot.unload_extension(ext)

    @commands.command(hidden=True)
    @perms(5)
    async def shutdown(self, ctx):
        await ctx.send('I will be back')
        await bot.logout()

    @commands.command(hidden=True)
    async def test(self, ctx, *args):
        count = len(args)
        await ctx.send(f"{count} argument{'s' if count != 1 else ''}{':' if bool(count) else ''} {', '.join(args)}")

bot.add_cog(Setup())
bot.load_extension('Commands.Moderation')
bot.load_extension('Commands.Misc')
bot.load_extension('Commands.SM')
bot.load_extension('Commands.Testing')
bot.load_extension('Commands.Subverse')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandOnCooldown): await ctx.send(error, delete_after=5.0)
    else: print(error, '\n', ctx)

@bot.event
async def on_ready():
    print(f'{bot.user.name} is here to take over the world')
    print('----------------')
    await bot.change_presence(activity=discord.Game('with portals'))

bot.run(TOKEN)
