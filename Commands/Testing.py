from discord.ext import commands
import discord
import asyncio
import datetime
from functions import perms, supreme_listener

class EmbedUI(discord.Embed):
    '''Preset for an embed creating a choice menu'''

    numbers = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

    def __init__(self, ctx, emojis=[], **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx
        self.emojis = emojis or self.numbers
        self.count = 0

    def add_choice_field(self, name, values: list):
        '''Transform a list of values into a choice menu'''
        if not bool(values): return self
        list_of_items = [[value, self.emojis[values.index(value)]] for value in values[:len(self.emojis)]]
        cont = '\n'.join(x[1] + ' ' + str(x[0]) for x in list_of_items)
        self.add_field(name=name, value=cont, inline=False)
        self.count += len(values)
        return self

    def set_count(self, count):
        self.count = count
        return self

    async def add_options(self, msg, add_cancel=False):
        """Reacts to a message with emojis as options"""
        if not bool(count := self.count): raise ValueError('No emojis to add')
        len_emojis = len(self.emojis)
        number = count if count < len_emojis else len_emojis
        #adding reactions
        for x in (new_emojis := self.emojis[:number]):
            await msg.add_reaction(x)
        if add_cancel: await msg.add_reaction('❌')
        return msg, new_emojis

    async def edit(self, msg, add_return=False):
        """Edits the message"""
        await msg.edit(embed=self)
        if add_return:
            await msg.add_reaction('↩️')
        return self

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
    async def smth(self, ctx, *args):
        #checking for custom emojis
        emojis = []
        args = list(args)

        #changing the emotes
        for x in args:
            if x.startswith('emo '):
                args.pop(args.index(x))
                emojis = x.replace('emo ', '').split()
                break

        #creating the embed
        ui = EmbedUI(ctx, emojis=emojis)
        ui.set_author(name=f'Requested by {ctx.author.name}', icon_url=ctx.author.avatar_url)

        #now for the real part, editing it accordingly
        stuff = [
        {'name': 'Page 1', 'value': 'content of page 1', 'inline': False},
        {'name': 'Page 2', 'value': 'content of page 2', 'inline': False},
        {'name': 'Page 3', 'value': 'content of page 3', 'inline': False},
        {'name': 'Page 4', 'value': 'content of page 4', 'inline': False}]
        selection = -1
        first_run = True
        while True:
            if selection == -1:
                ui.clear_fields()
                ui.add_choice_field(name='Item list:', values=args)
                if first_run:
                    msg = await ctx.send(embed=ui)
                    options = await ui.add_options(msg, True)
                else: await msg.clear_reaction('↩️')
            else:
                ui.clear_fields()
                ui.add_field(**stuff[selection])
            if not first_run: await ui.edit(msg, add_return=(False if selection == -1 else True))
            try: selection = (await supreme_listener(ctx, *options, listen_for_add=True, listen_for_remove=True, add_return=(False if selection == -1 else True), add_cancel=True))[0]
            except asyncio.TimeoutError:
                await msg.clear_reactions()
                await msg.add_reaction('⏰')
                break
            if first_run: first_run = False
            if selection > len(stuff) - 1:
                await ctx.send('Out of range')
                return
            if selection == -2:
                await msg.clear_reactions()
                return
            await msg.remove_reaction(ui.numbers[selection], ctx.author)
        print('Loop exited')

    @commands.command()
    @perms(5)
    async def editit(self, ctx, name, value):
        msg = None
        async for m in ctx.channel.history(limit=10):
            if m.author == ctx.bot.user and bool(m.embeds):
                msg = m
                break
        if msg is None: return
        field = {'name': name, 'value': value, 'inline': False}
        await self.edit(msg, field)

    @commands.command()
    async def testembed(self, ctx):
        embed = discord.Embed(title='Embed', description='Just Embed', url='https://www.youtube.com/watch?v=qEGP0Weug3k', timestamp=datetime.datetime.now())
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url).set_footer(text='Footer',icon_url=ctx.author.avatar_url).set_thumbnail(url=ctx.bot.user.avatar_url)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Testing(bot))
    print('Testing loaded')
