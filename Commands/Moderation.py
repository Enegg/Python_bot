import asyncio
import datetime
from typing import Union, Optional


import discord
from discord.ext import commands


from functions import intify
from discotools import perms
from config import PURGE_CONFIRM_EMOTE, PURGE_CAP, SAFE_PURGE_LIMIT


class Moderation(commands.Cog):
    """Tools for moderation purposes."""
    def __init__(self, bot):
        self.bot = bot


    @commands.group(aliases=['wot', 'ins', 'info'])
    @perms(2)
    async def inspect(self, ctx: commands.Context):
        """Helper command used to retrieve data about the guild"""
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


    @commands.command(aliases=['user'])
    @perms(2)
    async def userinfo(self, ctx: commands.Context,
    member:  Optional[Union[discord.Member, discord.User, int]],
    channel: Optional[Union[discord.TextChannel, discord.CategoryChannel]]):
        """Returns info about invoker or pinged user (ID / mention)"""
        is_user = isinstance(member, (discord.User, int))

        if member is None:
            member: discord.Member = ctx.author

        elif isinstance(member, int):
            if len(str(member)) != 18:
                await ctx.send('Invalid ID.')
                return

            botmsg = await ctx.send('User not found. Attempt fetching (API call)?')
            reacts = ('✅', '❌')
            for r in reacts:
                await botmsg.add_reaction(r)

            check = lambda r, u: r.message == botmsg and u == ctx.author and str(r.emoji) in reacts

            try:
                reaction, _ = await ctx.bot.wait_for('reaction_add', timeout=10.0, check=check)

            except asyncio.TimeoutError:
                await botmsg.delete()
                return

            if str(reaction.emoji) == '✅':
                try:
                    member = await ctx.bot.fetch_user(member)

                except discord.NotFound:
                    await ctx.send("Could not find the user.")
                    return

            else:
                await botmsg.delete()
                return

        created_days = (datetime.datetime.today() - member.created_at).days
        data = (
            f"**{'User' if is_user else 'Member'}**: {member.mention}"
            f'\n**ID**: {member.id}'
            f'\n**Account created at**: {member.created_at.strftime(r"%d/%m/%Y")} ({created_days} days ago)')

        if not is_user:
            important = {'manage_guild', 'manage_channels',
                'manage_messages', 'manage_roles', 'mention_everyone', 'view_guild_insights',
                'kick_members', 'ban_members', 'manage_emojis', 'view_audit_log'}
            check = lambda perm: perm[1] and perm[0] in important
            if member.guild_permissions.administrator:
                if member.id == getattr(ctx.guild.owner, 'id', None):
                    notable = 'Server owner'

                else:
                    notable = 'Administrator'

            else:
                privs = filter(check, member.guild_permissions)
                notable = '\n'.join(x[0].capitalize() for x in privs).replace('_', ' ') or 'Basic'

            join_days = (datetime.datetime.today() - member.joined_at).days
            data += (
                f'\n**Joined at**: {member.joined_at.strftime(r"%d/%m/%Y")} ({join_days} days ago)'
                f"\n**Roles**: {', '.join(x.mention for x in reversed(member.roles[1:]))}"
                f'\n**Global privileges**:\n{notable}')

            if channel is not None:
                if member.permissions_in(channel).administrator:
                    channel_perms = 'All'

                else:
                    privs = filter(lambda perm: perm[1], member.permissions_in(channel))
                    channel_perms = '\n'.join(x[0].capitalize() for x in privs).replace('_', ' ') or 'None'

                data += (
                    f'\n**Permissions in {channel.mention}**:'
                    f'\n{channel_perms}')

        embed = discord.Embed(title=f'{member.name}{f" ({member.nick})" if not is_user and member.nick else ""}',
            description=data, color=member.color)
        embed.set_thumbnail(url=member.avatar_url)
        await ctx.send(embed=embed)

    @userinfo.error
    async def info_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.BadUnionArgument):
            print(ctx.args, ctx.kwargs)
            print(error.param, type(error.param))
            await ctx.send(f'Invalid input for param "{error.param.name}"')


    @commands.command(brief='Returns a dict of your roles')
    @perms(1)
    async def roles(self, ctx: commands.Context):
        await ctx.send(f'`{ctx.author.roles}`')


    @commands.command(
        aliases=['prune', 'p'],
        usage='[count] [optional: mention]',
        brief='Purges messages from a channel')
    @perms(1)
    async def purge(self, ctx: commands.Context, count: Optional[int], members: commands.Greedy[discord.Member]):
        """Deletes number of messages from the channel it has been used in.
         You can specify whose messages to purge by pinging one or more users"""
        msg = ctx.message

        def purger(n):
            check = lambda m: not m.pinned and (not members or m.author in members)
            return ctx.channel.purge(limit=n, check=check)

        await msg.delete()

        if count is None:
            count = 1

        count = min(count, PURGE_CAP)

        if count <= SAFE_PURGE_LIMIT:
            await purger(count)

        else:
            victims = f"messages of {', '.join(x.name for x in members)} in the recent " if members else ''
            botmsg = await ctx.send(f'You are going to purge {victims}{count} messages, continue?')
            await botmsg.add_reaction(PURGE_CONFIRM_EMOTE)
            check = lambda reaction, user: user == ctx.author and str(reaction.emoji) == PURGE_CONFIRM_EMOTE
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


    @commands.command(hidden=True, usage='[ActType] (text...)')
    @perms(5)
    async def activity(self, ctx: commands.Context, act: str, *args):
        """Sets the bot activity"""

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
