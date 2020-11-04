import discord
from discord.ext import commands
from matrices import Matrix
import asyncio

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
        while True:
            try:
                msg = await ctx.bot.wait_for('message', timeout=120.0, check=lambda m: m.channel == ctx.channel and m.author == ctx.author)
            except asyncio.TimeoutError:
                await bot_msg.add_reaction('⏰')
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
        pass

def setup(bot):
    bot.add_cog(Math(bot))
    print('Math loaded')
