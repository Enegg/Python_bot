import asyncio
import datetime
import typing

import discord
from discord.ext import commands

from functions import intify
from discotools import perms
from config import purge_confirm_emote, purge_cap

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=['wot','ins', 'info'], brief='Helper command used to retrieve data about the guild')
    @perms(2)
    async def inspect(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            guild = ctx.guild
            embed = discord.Embed(title=guild.name, color=guild.owner.color, timestamp=guild.created_at)
            embed.add_field(name='Owner', value=f'{guild.owner.mention}')
            embed.add_field(name='Text channels', value=f'{len(guild.text_channels)}')
            embed.add_field(name='Members', value=f'{guild.member_count}')
            embed.set_footer(text=f'Created {(datetime.datetime.today() - guild.created_at).days} days ago')
            embed.set_thumbnail(url=guild.icon_url)
            await ctx.send(embed=embed)

    @inspect.command(brief='Returns guild\'s channels and their id\'s')
    async def channels(self, ctx: commands.Context):
        result = '\n'.join(f'<#{x.id}>: {x.id}' for x in ctx.guild.channels if isinstance(x, discord.TextChannel))
        await ctx.send(result)

    @commands.command(aliases=['user'], brief='Returns info about the invoker or pinged member (you can use his ID)')
    @perms(2)
    async def userinfo(self, ctx: commands.Context, member: typing.Union[discord.Member, int]=None):
        if member is None:
            member = ctx.author
            is_fetched = False
        elif is_fetched := isinstance(member, int):
            if len(str(member)) != 18:
                await ctx.send('Invalid ID.')
                return
            botmsg = await ctx.send('User not found. Attempt fetching (API call)?')
            check = lambda m: m.channel == ctx.channel and m.author == ctx.author
            try:
                response = await ctx.bot.wait_for('message', timeout=10.0, check=check)
            except asyncio.TimeoutError:
                await botmsg.delete()
                return
            if response.content.lower() in 'yes':
                try:
                    member = await ctx.bot.fetch_user(member)
                except discord.NotFound:
                    await ctx.send("Couldn't find the user.")
                    return

        created_days = (datetime.datetime.today() - member.created_at).days
        data = (
            f'**User**: {member.mention}'
            f'\n**ID**: {member.id}'
            f'\n**Account created at**: {member.created_at.strftime(r"%d/%m/%Y")} ({created_days} days ago)')

        if not is_fetched:
            important = {'administrator', 'manage_guild', 'manage_channels', 'manage_messages', 'manage_roles'}
            if member.guild_permissions.administrator:
                high_rank = 'Server owner' if member.id == getattr(ctx.guild.owner, 'id', None) else 'Administrator'
            else:
                high_rank = ''
                privs = filter(lambda perm: perm[1] and perm[0] in important, member.guild_permissions)
            notable = high_rank or '\n'.join(x[0].title() for x in privs).replace('_', ' ') or 'Basic'
            join_days = (datetime.datetime.today() - member.joined_at).days
            roles = ', '.join(x.mention for x in reversed(member.roles[1:]))
            data += (
                f'\n**Joined at**: {member.joined_at.strftime(r"%d/%m/%Y")} ({join_days} days ago)'
                f'\n**Roles**: {roles}'
                f'\n**Notable privileges**:\n{notable}')
        embed = discord.Embed(title=f'{member.name}{f" ({member.nick})" if not is_fetched and member.nick else ""}',
            description=data, color=member.color)
        embed.set_thumbnail(url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(brief='Returns a dict of your roles')
    @perms(1)
    async def roles(self, ctx: commands.Context):
        await ctx.send(f'`{ctx.author.roles}`')

    @commands.command(
        aliases=['prune','pirge','puerg','p'],
        usage='[count] [optional: mention]',
        brief='Purges messages from a channel',
        help=('Deletes a specified number of messages from the channel it has been used in.'
              ' You can specify whose messages to purge by pinging one or more users'))
    @perms(1)
    async def purge(self, ctx: commands.Context, count: typing.Optional[int], members: commands.Greedy[discord.Member]):
        msg = ctx.message
        def purger(n):
            check = lambda m: not m.pinned and (not members or m.author in members)
            return ctx.channel.purge(limit=n, check=check)
        await msg.delete()
        if count is None:
            count = 1
        if count > purge_cap:
            count = purge_cap
        if count <= 10: 
            await purger(count)
        else:
            victims = f"messages of {', '.join(x.name for x in members)} in the recent " if members else ''
            botmsg = await ctx.send(f'You are going to purge {victims}{count} messages, continue?')
            await botmsg.add_reaction(purge_confirm_emote)
            check = lambda reaction, user: user == ctx.author and str(reaction.emoji) == purge_confirm_emote
            try: 
                await ctx.bot.wait_for('reaction_add', timeout=20.0, check=check)
            except asyncio.TimeoutError:
                await botmsg.delete()
            else:
                await botmsg.delete()
                while count >= 100: # 100 is hardcoded channel.purge default limit
                    await purger(100)
                    count -= 100
                if count > 0:
                    await purger(count)

    @commands.command(hidden=True, usage='[ActType] (args...)')
    @perms(5)
    async def activity(self, ctx: commands.Context, act: str, *args):
        if not act:
            return
        activity = discord.Activity(
            name=' '.join(args),
            type=getattr(discord.ActivityType, act, 3),
            url='https://discordapp.com/')
        await self.bot.change_presence(activity=activity)
        await ctx.message.add_reaction('✅')

def setup(bot):
    bot.add_cog(Moderation(bot))
    print('Moderation loaded')
