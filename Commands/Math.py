import discord
from discord.ext import commands
from matrices import Matrix

class Math(commands.cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['matrix'])
    async def create_matrix(self, ctx):
        embed = discord.Embed(title='Matrix manipulation')
        embed.add_field(name='Starting', value='To begin, create a matrix\n```"new" (A-Z) YxX elements...```')
        bot_msg = await ctx.send(embed=embed)
        exiting = False
        while True:
            msg = await ctx.bot.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author)
            content = msg.content.split(' ')
            if exiting:
                if content and content[0].lower() == 'yes': break
                else:
                    exiting = False
                    embed.remove_field(-1)
                    await bot_msg.edit(embed=embed)
                    continue
            if (exiting := (len(content) == 0)):
                embed.add_field(name='Do you wish to exit?', value='[yes/no]', inline=False)
                await bot_msg.edit(embed=embed)
                continue

        pass

def setup(bot):
    bot.add_cog(Math(bot))
    print('Math loaded')