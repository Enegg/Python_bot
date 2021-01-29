import asyncio
import datetime

import discord
from discord.ext import commands

from discotools import perms, EmbedUI, scheduler

class Testing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def edit(self, embed, new_field: dict):
        """Edits the embed"""
        embed.clear_fields()
        embed.add_field(**new_field)
        return embed

    @commands.command()
    @perms(1)
    async def smth(self, ctx: commands.Context, *args):
        #checking for custom emojis
        emojis = []
        args = list(args)

        #changing the emotes
        for x in args:
            if x.startswith('emo '):
                args.pop(args.index(x))
                emojis = x[4:].split()
                break

        #creating the embed
        ui = EmbedUI(emojis=emojis)
        ui.set_author(name=f'Requested by {ctx.author.name}', icon_url=ctx.author.avatar_url)

        #now for the real part, editing it accordingly
        stuff = [
        {'name': 'Page 1', 'value': 'content of page 1', 'inline': False},
        {'name': 'Page 2', 'value': 'content of page 2', 'inline': False},
        {'name': 'Page 3', 'value': 'content of page 3', 'inline': False},
        {'name': 'Page 4', 'value': 'content of page 4', 'inline': False}]
        reaction = '↩️'
        first_run = True
        def check(reaction, user) -> bool:
            return user.id == ctx.author.id and str(reaction.emoji) in []

        while True:
            if reaction == '↩️':
                ui.clear_fields()
                ui.add_choice_field(name='Item list:', values=args)
                if first_run:
                    msg = await ctx.send(embed=ui)
                    options = await ui.add_options(msg, True)
                else:
                    await msg.clear_reaction('↩️')
            else:
                ui.clear_fields()
                ui.add_field(**stuff[emojis.index(reaction)])
            if not first_run:
                await ui.edit(msg, add_return=(False if reaction == '↩️' else True))

            try:
                selection = (await supreme_listener(ctx, *options, listen_for_add=True, listen_for_remove=True, add_return=bool(selection != -1), add_cancel=True))[0]
                async for reaction, _, _ in scheduler(ctx, {'reaction_add', 'reaction_remove'}, check=check, timeout=20.0):
                    reaction = str(reaction.emoji)
                    pass
            except asyncio.TimeoutError:
                await msg.clear_reactions()
                await msg.add_reaction('⏰')
                break
            if first_run:
                first_run = False
            if emojis.index(reaction) > len(stuff) - 1:
                await ctx.send('Out of range')
                return
            if reaction == '❌':
                await msg.clear_reactions()
                return
            await msg.remove_reaction(ui.numbers[selection], ctx.author)
        print('Loop exited')

    @commands.command()
    @perms(5)
    async def editit(self, ctx: commands.Context, name, value):
        msg = None
        async for m in ctx.channel.history(limit=10):
            if m.author == ctx.bot.user and bool(m.embeds):
                msg = m
                break
        if msg is None: return
        field = {'name': name, 'value': value, 'inline': False}
        await msg.edit(embed=self.edit(msg.embeds[0], field))
        await ctx.message.delete()

    @commands.command()
    async def testembed(self, ctx: commands.Context):
        embed = discord.Embed(title='Yeah embed', description=f'[Embed nothing else]({ctx.message.jump_url})', timestamp=ctx.message.created_at)
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url).set_footer(text='Footer', icon_url=ctx.author.avatar_url).set_thumbnail(url=ctx.bot.user.avatar_url)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Testing(bot))
    print('Testing loaded')
