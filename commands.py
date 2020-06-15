"""Commands handler module"""
import asyncio
import re
import discord
from random import randint
from config import purge_confirm_emote, prefix, purge_cap, authorid, abbreviations
from ROBO_Head import client

#general use

def permz(msg):
    permKeys, power = ['manage_messages', 'manage_guild', 'administrator'], 0
    for key in permKeys:
        for role in msg.author.roles:
            if getattr(role.permissions, key): 
                power = permKeys.index(key) + 1
                break
    if msg.author.id == authorid:
        return len(permKeys) + 1
    return power

def intify(s, default=0):
    r"""Takes any string and returns an integer if possible, else returns default value"""
    s = str(s)
    if s.isdigit():
        return int(s)
    elif s[0] in '-+':
        if s[1:].isdigit():
            if s[0] == '-':
                return int(s)
            return int(s[1:])
    return default

def channels(guild_name):
    guild_channels_cache = {}
    channel_id_cache = {}
    for guild in client.guilds:
        guild_channels_cache[guild.name] = guild.channels
    if guild_name not in guild_channels_cache:
        if guild_name not in abbreviations: return False
        guild_name = abbreviations[guild_name]
    for channel in guild_channels_cache[guild_name]:
        if not isinstance(channel, discord.channel.TextChannel): continue
        channel_id_cache[channel.name] = channel.id
    return channel_id_cache

def roll(a=1, b=6):
    min_, max_ = min(a, b), max(a, b)
    return randint(min_, max_)

#handlers
def prefix_handler(msg, sep=' '):
    txt = msg.content.replace(prefix, '')
    cmd = re.match(r'(^[^\s]+)', txt)[0]
    txt = txt.replace(cmd, '')
    txt = re.sub(r'(^\s+|\s+(?=\s)|\s+$)', '', txt)
    args = txt.split(sep)
    if sep != ' ':
        args = [arg for arg in map(lambda a: a.strip(), args)]
    return cmd, args

def trigger(message, cmd): return message.content.startswith(prefix + cmd)

def roll_handler(message):
    cont = prefix_handler(message)
    if cont[1] == ['']: return roll()
    cs = cont[1]
    a = intify(cs[0], 'ass')
    if len(cs) > 1: b = intify(cs[1], 'ass')
    else: b = 0
    if a == 'ass' or b == 'ass': return 'Wrong syntax'
    return roll(a, b)

#async def send(content, channel=message.channel): await channel.send(content)

async def purge(message, cap=purge_cap):
    channel = message.channel
    purger = lambda n: channel.purge(limit=n)
    await message.delete()
    cont = prefix_handler(message)[1][0]
    count = intify(cont)
    if count > cap: count = cap
    if count <= 10: await purger(count)
    else:
        botmsg = await channel.send('You are going to purge {} messages, continue?'.format(count))
        await botmsg.add_reaction(purge_confirm_emote)
        try:
            reaction, user = await client.wait_for('reaction_add', timeout=20.0, check=lambda reaction, user: user == message.author and reaction.emoji == purge_confirm_emote)
        except asyncio.TimeoutError:
            await botmsg.delete()
        else:
            await botmsg.delete()
            while count >= 100:
                await purger(100)
                count -= 100
            if count > 0: await purger(count)

async def epix_command(message):
    cont = message.content.split()
    await message.delete()
    cont.pop(0)
    if cont != []:
        pass
    elif message.author.id == authorid:
        cont = input().split()
    else:
        await message.channel.send('Empty fields', delete_after=3.0)
    server_name = cont.pop(0)
    channel_name = cont.pop(0)
    if channels(server_name) == False:
        await message.channel.send('Invalid entry', delete_after=3.0)
        return
    channelid = channels(server_name)[channel_name]
    channel = client.get_channel(channelid)
    await channel.send(' '.join(cont))

operation = {'add': ['health'],
    'mult': ['eneCap','heaCap','eneReg','heaCap','heaCol','phyDmg','expDmg','eleDmg','heaDmg','eneDmg'],
    'mult+': ['phyRes','expRes','eleRes'],
    'reduce': ['backfire']}

def buff(stat, value, enabled):
    #print(stat, value, enabled, sep=', ')
    if enabled == False: return value
    if stat not in operation['add'] and stat not in operation['mult'] and stat not in operation['mult+'] and stat not in operation['reduce']: return value
    if stat in operation['add']: result = value + 350
    if stat in operation['mult']: result = round(value * 1.2)
    if stat in operation['mult+']: result = round(value * 1.4)
    if stat in operation['reduce']: result = round(value * 0.8)
    return result