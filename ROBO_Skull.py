import discord
from discord.ext import commands
import socket
from functions import perms
from config import prefix_local, prefix_host
default_activity = discord.Game('with portals')

prefix = prefix_local if socket.gethostname() == 'Mystery_machine' else prefix_host
bot = commands.Bot(command_prefix=prefix)

class Setup(commands.Cog):
    @commands.group(hidden=True)
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

    @ext.command()
    @perms(5)
    async def reload(self, ctx, arg):
        await ctx.message.add_reaction('🔄')
        if arg == 'all':
            await ctx.send('Reloading all modules...', delete_after=5.0)
            #bot.extensions gets modified on reload so we have to pre-assign all loaded extensions
            [bot.reload_extension(ext) for ext in [ext for ext in bot.extensions]]
            return
        if '.' in arg: ext = arg
        else: ext = 'Commands.' + arg
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
    @perms(3)
    async def shutdown(self, ctx):
        await ctx.send('I will be back')
        await bot.logout()

    @commands.command(hidden=True)
    async def test(self, ctx, *args):
        count = len(args)
        await ctx.send(f"{count} argument{'s' if count != 1 else ''}{':' if bool(count) else ''} {', '.join(args)}")

bot.add_cog(Setup(bot))
bot.load_extension('Commands.Moderation')
bot.load_extension('Commands.Misc')
bot.load_extension('Commands.SM')
bot.load_extension('Commands.Testing')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandOnCooldown): await ctx.send(error, delete_after=5.0)
    else: print(error, '\n', ctx)

@bot.event
async def on_ready():
    print(f'{bot.user.name} is here to take over the world')
    print('----------------')
    await bot.change_presence(activity=default_activity)

TOKEN = None
if socket.gethostname() != 'Mystery_machine':
    import os
    TOKEN = os.environ.get('TOKEN')
else:
    import importlib
    TOKEN = importlib.import_module('TOKEN').TOKEN
if not TOKEN:
    raise 'Not running localy and TOKEN is not an environment variable'

bot.run(TOKEN)
