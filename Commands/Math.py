import discord
from discord.ext import commands
import asyncio
import importlib
Matrix = importlib.import_module('..matrices', 'Python_bot').Matrix

class Math(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['matrix'])
    async def create_matrix(self, ctx):
        embed = discord.Embed(title='Matrix manipulation')
        embed.add_field(name='Starting', value='To begin, create a matrix\n```"new" (A-Z) YxX elements...```')
        embed.set_footer(text='Type "exit" to exit')
        bot_msg = await ctx.send(embed=embed)
        exiting = False
        matrices = {}
        while True:
            try:
                msg = await ctx.bot.wait_for('message', timeout=120.0, check=lambda m: m.channel == ctx.channel and m.author == ctx.author)
            except asyncio.TimeoutError:
                await bot_msg.edit(embed=embed.set_footer(text='Session has expired'))
                break
            content = msg.content.split(' ')
            if exiting:
                if content and content[0].lower() == 'yes':
                    await bot_msg.edit(embed=embed.set_footer(text='Session has expired'))
                    break
                else:
                    exiting = False
                    embed.remove_field(-1)
                    await bot_msg.edit(embed=embed)
                    continue
            if (exiting := ('exit' in content)):
                embed.add_field(name='Do you wish to exit?', value='[yes/no]', inline=False)
                await bot_msg.edit(embed=embed)
                continue
            print(content)
            if 'new' in content:
                bad_input = ctx.send('Incorrect input format.', delete_after=5.0)
                if len(content) < 4 or 'x' not in content[2] or len(content[1]) != 1:
                    print(len(content) < 4, 'x' not in content[2], len(content[1]) != 1)
                    await bad_input
                    continue
                size = tuple(int(x) for x in content[2].split('x'))
                try:
                    values = [int(n) for n in content[3:]]
                except ValueError:
                    print('error')
                    await bad_input
                    continue
                if len(values) != size[0] * size[1]:
                    await ctx.send('Incorrect amount of values for the matrix.', delete_after=5.0)
                matrices[content[1]] = Matrix(*size, values)
                embed.insert_field_at(0, name='Matrices', value=f'{matrices}', inline=False)
                print(embed.fields[0])
                bot_msg.edit(embed=embed)
        pass

def setup(bot):
    bot.add_cog(Math(bot))
    print('Math loaded')
