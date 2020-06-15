"""Commands handler module"""
import asyncio
import re
import discord
import socket
import json
import requests
from random import randint
from config import prefix_host, prefix_local, purge_confirm_emote, purge_cap, authorid, abbreviations, WU_DB
client = discord.Client()
prefix = prefix_host

#general use
if socket.gethostname() == 'Mystery_machine':
    prefix = prefix_local

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
    txt = msg.content.replace(prefix, '', 1)
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
    if enabled == False: return value
    if stat not in operation['add'] and stat not in operation['mult'] and stat not in operation['mult+'] and stat not in operation['reduce']: return value
    if stat in operation['add']: result = value + 350
    if stat in operation['mult']: result = round(value * 1.2)
    if stat in operation['mult+']: result = round(value * 1.4)
    if stat in operation['reduce']: result = round(value * 0.8)
    return result

async def stats(message):
    args = prefix_handler(message)[1]
    if args[0] == '':
        await message.channel.send('Funny command huh')
        return
    #flags
    flags = []
    for i in ['-d', '-b', '-r']:
        if i in args:
            flags.append(args.pop(args.index(i)))
    buffs = '-b' in flags
    #solving for abbrevs
    name = ' '.join(args).lower()
    if name in WU_DB['item_dict']:
        name = WU_DB['item_dict'][name]
    item = json.loads(requests.get(WU_DB['api_link'] + name).text)
    #test flag
    if '-r' in flags:
        if permz(message) > 2:
            await message.channel.send(item)
            return
        else:
            await message.add_reaction('❌')
            return
    #error handling
    if 'message' in item:
        await message.add_reaction('❌')
        if permz(message) > 3:
            print(item)
        return
    #adding a note when -d or -b flag is included
    note = ''
    divine = False
    beef = ', buffed' if buffs else ''
    if '-d' in flags:
        divine = 'divine' in item
        note = ' (divine{})'.format(beef) if divine else ' (~~divine~~{})'.format(beef)
    elif buffs == True:
        note = ' (buffed)'
    #adding item stats
    item_stats = ''
    spaced = False
    for k in item['stats']:
        if k in ['backfire', 'heaCost', 'eneCost'] and spaced == False:
            item_stats += '\n'
            spaced = True
        y = 'stats'
        #divine handler
        if divine == True:
            if k in item['divine']:
                y = 'divine'
        #number range handler
        if isinstance(item['stats'][k], list):
            #handling one spot range
            if len(item['stats'][k]) == 1:
                value = buff(k, item[y][k][0], buffs)
            elif item[y][k][1] == 0:
                value = item[y][k][0]
            else:
                value = str(buff(k, item[y][k][0], buffs)) + '-' + str(buff(k, item[y][k][1], buffs))
        else:
            value = buff(k, item[y][k], buffs)
        item_stats = item_stats + '**{}**'.format(value) + ' {}\n'.format(WU_DB['WUabbrev'][k])
    #embedding
    embed = discord.Embed(title=item['name'], description=' '.join([item['element'].lower().capitalize(), item['type'].replace('_', ' ').lower()]), color=WU_DB['colors'][item['element']])
    #transform range
    min, max = item['transform_range'].split('-')
    fields = []
    fields.append(['Transform range: ', '{}'.format(''.join(WU_DB['trans_range'][WU_DB['tiers'].index(min):WU_DB['tiers'].index(max) + 1]))])
    fields.append(['Stats{}:'.format(note), item_stats])
    for field in fields:
        embed.add_field(name=field[0], value=field[1], inline=False)
    img_url = WU_DB['sprite_path'] + item['name'].replace(' ', '') + '.png'
    embed.set_image(url=img_url)
    await message.channel.send(embed=embed)
