import asyncio
import datetime
from typing import Optional, Union


import discord
from discord.ext import commands


from functions import roll, intify


class Misc(commands.Cog):
    """Commands not fitting in other categories."""
    def __init__(self, bot):
        self.bot = bot
        self.emojis = None


    def emojifier(self):
        """Caches all emojis the bot has access to in a dict{name: emoji}"""
        emojis, normal_dict, animated_dict = {}, {}, {}
        for guild in self.bot.guilds:
            normal_list, animated_list = [], []
            for emoji in guild.emojis:
                emojis.setdefault(emoji.name.lower(), []).append(emoji)
                (animated_list if emoji.animated else normal_list).append(emoji)

            if normal_list:
                normal_dict[guild.name] = normal_list
            if animated_list:
                animated_dict[guild.name] = animated_list
        emojis.update({'normal': normal_dict, 'animated': animated_dict})
        self.emojis = emojis


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, ctx: commands.Context):
        if ctx.member.bot: return
        if str(ctx.emoji) == '🖇️':
            msg = await (channel := self.bot.get_channel(ctx.channel_id)).fetch_message(ctx.message_id)
            author = msg.author
            link = msg.jump_url
            embed = discord.Embed(description=(f'```{msg.content}```' if msg.content else None), timestamp=datetime.datetime.now(tz=datetime.timezone.utc), color=author.color)
            embed.set_author(name=f'Message by {author.display_name} from {msg.created_at.isoformat(sep=" ", timespec="minutes")}', url=link, icon_url=author.avatar_url)
            embed.set_footer(text=f'Quoted by {ctx.member.display_name}', icon_url=ctx.member.avatar_url)
            if msg.embeds:
                quoted_embed = msg.embeds[0]
                title_desc_field = {'name': quoted_embed.title, 'value': quoted_embed.description, 'inline': False}
                quoted_fields = [{'name': field.name, 'value': field.value, 'inline': field.inline} for field in quoted_embed.fields]
                embed.add_field(**title_desc_field).set_image(url=quoted_embed.image.url).set_thumbnail(url=quoted_embed.thumbnail.url)
                [embed.add_field(**field) for field in quoted_fields]

            await channel.send(embed=embed, files=[await x.to_file() for x in msg.attachments])


    @commands.Cog.listener()
    async def on_ready(self):
        self.emojifier()


    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.emojifier()


    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        self.emojifier()


    @commands.command(
        aliases=['roll'],
        usage='<nothing|number|number1, number2|"frantic">')
    async def dice(self, ctx: commands.Context, a: Optional[Union[int, str]], b: Optional[int]=0):
        """Roll a dice or provide custom range to get a random number"""
        if not a:
            await ctx.send(roll())
            return
        if a == 'frantic':
            a, b = 84, 779
        await ctx.send(roll(a, b))


    @commands.command()
    async def ping(self, ctx: commands.Context):
        """Pings the bot"""
        await ctx.send(f'Pong! {round(ctx.bot.latency * 1000)}ms')


    @commands.command(aliases=['av'])
    async def avatar(self, ctx: commands.Context, member: Optional[discord.Member]):
        """Get a link to your or someone\'s avatar"""
        await ctx.send((ctx.author if member is None else member).avatar_url)


    @commands.command(
        aliases=['r'],
        usage='[emoji] [opt: ^ to react to message above] / while in DM: [normal|animated]')
    @commands.cooldown(3, 15.0, commands.BucketType.member)
    async def react(self, ctx: commands.Context, *args):
        """Makes the bot send or react with emoji(s)"""
        args = list(args)
        flags = {args.pop(args.index(i)) for i in {'^', '-r'} if i in args}
        up = bool('^' in flags)
        raw = bool('-r' in flags)
        msg = ctx.message
        if not args:
            await msg.add_reaction('❓')
            return
        is_dm = bool(isinstance(ctx.channel, discord.DMChannel))

        rmsg = None
        if up and not raw:
            async for m in ctx.channel.history(limit=2):
                rmsg = m
            if rmsg is None:
                return

        if self.emojis is None:
            self.emojifier()

        if args[0] in {'animated', 'normal'}:
            if not is_dm:
                await ctx.send('You can use that only in DMs.', delete_after=6.0)
                await msg.delete()
                return

            bank = self.emojis[args[0]]
            for guild in bank:
                string = f'**{guild}**: '
                list_strings = []
                for item in bank[guild]:
                    emoji = raw * '\\' + str(item)
                    if len(string + emoji) > 2000:
                        list_strings.append(string)
                        string = ''
                    string += emoji
                list_strings.append(string)
                for x in list_strings:
                    await ctx.send(x)
            return

        if args[0] in {'uwu', 'dontuwu'}:
            uwu = ''.join(
                f"{''.join(str(self.emojis[f'dontuwu{n}'][0]) for n in range(i, 16+i, 5))}\n" for i in range(5))
            await ctx.send(uwu)
            if not is_dm:
                await msg.delete()
            return

        emojis = []
        for arg in args:
            if arg in self.emojis:
                check = lambda r, u: r.message == msg and u == ctx.author and r.emoji in self.emojis[arg]
                if len(self.emojis[arg]) > 1:
                    if emojis:
                        await msg.clear_reactions()
                    for emoji in self.emojis[arg]:
                        await msg.add_reaction(emoji)
                    try:
                        reaction, _ = await ctx.bot.wait_for('reaction_add', timeout=10.0, check=check)
                    except asyncio.TimeoutError:
                        if emojis:
                            await ctx.send(''.join(emojis))
                        await msg.delete()
                        return
                    emoji = str(reaction)
                else:
                    emoji = str(self.emojis[arg][0])
                if raw:
                    emoji = f'\\{emoji}'
                emojis.append(emoji)
            elif arg == '\\n':
                emojis.append('\n')
        if up and not raw and '\n' not in emojis:
            for emoji in emojis:
                await rmsg.add_reaction(emoji)
        else:
            if emojis:
                await ctx.send(''.join(emojis))
        if not is_dm:
            await msg.delete()


    @commands.command()
    @commands.cooldown(1, 15.0, commands.BucketType.guild)
    async def hleo(self, ctx: commands.Context):
        """Deletes the next message sent to a channel"""
        await ctx.message.delete()
        botmsg = await ctx.send('<:ooh:704392385580498955>')
        try:
            victim = await ctx.bot.wait_for('message', timeout=600.0, check=lambda m: not m.author.bot and m.channel == ctx.channel)
        except asyncio.TimeoutError:
            await botmsg.delete()
            return
        await botmsg.edit(content='<:duh:705900542001545246>')
        await asyncio.sleep(0.5)
        await botmsg.edit(content='<:none:772958360240128060><:duh:705900542001545246>\n<:none:772958360240128060><:legs:730115699397361827>')
        await asyncio.sleep(0.5)
        await botmsg.edit(content='<:none:772958360240128060><:duh:705900542001545246>\n<:none:772958360240128060><:gunload:742508424427995167>')
        await asyncio.sleep(0.5)
        await botmsg.edit(content='<:none:772958360240128060><:duh:705900542001545246>\n<:gun:742508449073463328>')
        await asyncio.sleep(0.5)
        await victim.delete()
        await botmsg.edit(content='<:epix:724331507162021959>',delete_after=2.0)


def setup(bot):
    bot.add_cog(Misc(bot))
    print('Misc loaded')
