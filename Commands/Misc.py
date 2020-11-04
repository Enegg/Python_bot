import asyncio
import discord
import datetime
from discord.ext import commands
from functions import roll, intify

class Misc(commands.Cog):
    def emojifier(self):
        r'''Helper func running on the bot init, caches all emojis the bot has access to in a dict{name:emoji}'''
        emojis, normal_dict, animated_dict = {}, {}, {}
        for guild in self.bot.guilds:
            normal_list, animated_list = [], []
            for emoji in guild.emojis:
                name = emoji.name.lower()
                (animated_list if emoji.animated else normal_list).append(emoji)
                if name in emojis:
                    if isinstance(emojis[name], list): emojis[name].append(emoji)
                    else: emojis.update({name:[emojis[name], emoji]})
                else: emojis.update({name:emoji})
            if bool(normal_list): normal_dict.update({guild.name:normal_list})
            if bool(animated_list): animated_dict.update({guild.name:animated_list})
        emojis.update({'normal': normal_dict, 'animated': animated_dict})
        self.emojis = emojis

    def __init__(self, bot):
        self.bot = bot
        self.emojis = None
        self.emojifier()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, ctx):
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

    @commands.command(name='roll',usage='<nothing|number|number1, number2|"frantic">',brief='Roll a dice or provide custom range to get a random number')
    async def dice(self, ctx, *args):
        if args == ():
            await ctx.send(roll())
            return
        if args[0] == 'frantic': a, b = 84, 779
        else:
            a = intify(args[0])
            b = intify(args[1]) if len(args) > 1 else 0
        await ctx.send(roll(a, b))

    @commands.command(brief='Pings the bot')
    async def ping(self, ctx):
        await ctx.send(f'Pong! {round(ctx.bot.latency * 1000)}ms')

    @commands.command(aliases=['av'],usage='[optional: mention]',brief='Get a link to your or someone\'s avatar')
    async def avatar(self, ctx):
        await ctx.send((ctx.message.mentions[0] if ctx.message.mentions != [] else ctx.author).avatar_url)

    @commands.command(aliases=['r'],usage='[emoji] [opt: ^ to react to message above] / while in DM: [normal|animated]',brief='Makes the bot send or react with an emoji')
    @commands.cooldown(3, 15.0, commands.BucketType.member)
    async def react(self, ctx, *args):
        args = list(args)
        msg = None
        channel_check = bool(isinstance(ctx.channel, discord.DMChannel))
        if up := bool('^' in args):
            args.pop(args.index('^'))
            async for m in ctx.channel.history(limit=2): msg = m
        arg = ' '.join(args)
        if self.emojis is None: self.emojifier()

        if arg in ['animated', 'normal']:
            if not channel_check:
                await ctx.send('You can use that only in DMs.', delete_after=6.0)
                await ctx.message.delete()
                return
            bank = self.emojis[arg]
            for guild in bank:
                string = f'{guild}: '
                list_strings = []
                for item in bank[guild]:
                    emoji = f"<{'a' if item.animated else ''}:{item.name}:{item.id}>"
                    if len(string + emoji) > 2000:
                        list_strings.append(string)
                        string = ''
                    string += emoji
                list_strings.append(string)
                for x in list_strings: await ctx.send(x)
            return

        if arg in self.emojis:
            if isinstance(self.emojis[arg], list):
                for emoji in self.emojis[arg]:
                    await ctx.message.add_reaction(emoji)
                try: reaction = await ctx.bot.wait_for('reaction_add', timeout=10.0, check=lambda reaction, user: user == ctx.author and bool(reaction.emoji in self.emojis[arg]))
                except asyncio.TimeoutError:
                    await ctx.message.delete()
                    return
                await msg.add_reaction(reaction[0]) if up else await ctx.send(reaction[0])
            else:
                await msg.add_reaction(self.emojis[arg]) if up else await ctx.send(self.emojis[arg])
        if not channel_check: await ctx.message.delete()

    @commands.command()
    @commands.cooldown(1, 15.0, commands.BucketType.guild)
    async def hleo(self, ctx):
        await ctx.message.delete()
        botmsg = await ctx.send('<:ooh:704392385580498955>')
        try: victim = await ctx.bot.wait_for('message', timeout=600.0, check=lambda m: not m.author.bot and m.channel == ctx.channel)
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
