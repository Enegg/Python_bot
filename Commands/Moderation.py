import asyncio
import discord
from discord.ext import commands
import datetime
from functions import perms, intify
from config import purge_confirm_emote, purge_cap

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=['wot','ins'],brief='Helper command used to retrieve data about the guild')
    @perms(2)
    async def inspect(self, ctx):
        if ctx.invoked_subcommand is None:
            guild = ctx.guild
            thing = f'**Text channels**: {len(guild.text_channels)}\n**Members**: {guild.member_count}\n**Created at**: {guild.created_at.date()} ({(datetime.datetime.today() - guild.created_at).days} days ago)'
            embed = discord.Embed(title=guild.name, description=f'**Owner:** {guild.owner.mention}', color=guild.owner.color)
            embed.add_field(name='Statistics:', value=thing, inline=False)
            embed.set_thumbnail(url=guild.icon_url)
            await ctx.send(embed=embed)

    @inspect.command(brief='Returns guild\'s channels and their id\'s')
    async def channels(self, ctx):
        channel_list = [x for x in filter(lambda x: isinstance(x, discord.TextChannel), ctx.guild.channels)]
        result = ''.join(f'<#{x.id}>: {x.id}\n' for x in channel_list)
        await ctx.send(result)

    @inspect.command(brief='Returns info about the invoker or pinged member (you can use his ID)')
    async def user(self, ctx, *args):
        mentions = ctx.message.mentions
        mentioned = bool(mentions)
        provided_args = bool(args)
        if mentioned: member = mentions[0]
        elif not mentioned and not provided_args:
            member = ctx.author
        elif provided_args:
            member = ctx.guild.get_member(intify(args[0]))
            if member is None:
                await ctx.send('Invalid ID.')
                return
        important = ['administrator', 'manage_guild', 'manage_channels', 'manage_messages', 'manage_roles']
        if member.guild_permissions.administrator:
            high_rank = 'Guild owner' if member == ctx.guild.owner else 'Administrator'
        else: high_rank, privs = '', filter(lambda perm: perm[1] and perm[0] in important, dict(member.guild_permissions).items())
        notable = high_rank or '\n'.join(x[0].capitalize() for x in privs).replace('_', ' ') or 'None'
        creation_date = f'**Account created at**: {member.created_at.date()} ({(datetime.datetime.today() - member.created_at).days} days ago)\n'
        join_date = f'**Joined at**: {member.joined_at.date()} ({(datetime.datetime.today() - member.joined_at).days} days ago)\n'
        roles = ', '.join(x.mention for x in reversed(member.roles))
        data = f'**User ID**: {member.id}\n' + creation_date + join_date + f'**Roles**: {roles}\n' + f'**Notable privileges**:\n{notable}'
        embed = discord.Embed(title=f'{member.name}{f" ({member.nick})" if member.nick is not None else ""}', description=data, color=member.color)
        embed.set_thumbnail(url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(brief='Returns a dict of your roles')
    @perms(1)
    async def roles(self, ctx):
        await ctx.send('`{}`'.format(ctx.author.roles))

    @commands.command(aliases=['prune','pirge','puerg','p'],usage='[count] [optional: mention]',brief='Purges messages from a channel',help='Deletes a specified number of messages from the channel it has been used in. You can specify whose messages to purge by pinging one or more users')
    @perms(1)
    async def purge(self, ctx, *args):
        msg = ctx.message
        mentions = msg.mentions if (has_mentions := bool(msg.mentions)) else None
        def purger(n): return ctx.channel.purge(limit=n, check=lambda m: not m.pinned and (m.author in mentions if has_mentions else True))
        await msg.delete()
        count = intify(args[0]) if bool(args) else 1
        if count > purge_cap: count = purge_cap
        if count <= 10: await purger(count)
        else:
            botmsg = await ctx.send(f"You are going to purge {'messages of {} in the recent '.format(', '.join(x.name for x in mentions)) if has_mentions else ''}{count} messages, continue?")
            await botmsg.add_reaction(purge_confirm_emote)
            try: await ctx.bot.wait_for('reaction_add', timeout=20.0, check=lambda reaction, user: user == ctx.author and str(reaction.emoji) == purge_confirm_emote)
            except asyncio.TimeoutError: await botmsg.delete()
            else:
                await botmsg.delete()
                while count >= 100:
                    await purger(100)
                    count -= 100
                if count > 0: await purger(count)

    @commands.command(hidden=True)
    @perms(5)
    async def activity(self, ctx, *args):
        args = list(args)
        ActType = discord.ActivityType
        activities = {'watching': ActType.watching, 'listening': ActType.listening, 'playing': ActType.playing, 'streaming': ActType.streaming}
        for k in ['watching', 'listening', 'playing', 'streaming']:
            if k in args:
                args.pop(args.index(k))
                ActType = activities[k]
                break
        activity = discord.Activity(name=' '.join(args),type=ActType,url='https://discordapp.com/')
        await ctx.bot.change_presence(activity=activity)

def setup(bot):
    bot.add_cog(Moderation(bot))
    print('Moderation loaded')
