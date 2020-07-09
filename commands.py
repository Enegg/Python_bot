"""Commands handler module"""
import asyncio
import re
import discord
import socket
import json
import inspect
from random import randint
from config import prefix_host, prefix_local, purge_confirm_emote, purge_cap, authorid, abbreviations, WU_DB, security_lvl
client = discord.Client()
items_list = json.loads(open("items.json").read())

prefix = prefix_host
if socket.gethostname() == 'Mystery_machine':
    prefix = prefix_local

#------------------functions-------------------
def get_item_by_id_or_name(value):
  for item in items_list:
    if str(item['id']) == str(value) or item['name'].lower() == str(value).lower():
      return item
  return None

def abbreviator():
    abbrevs = {}
    for item in items_list:
        name = item['name']
        if len(name) < 8: continue
        if ' ' not in name and name[1:].islower(): abbreviation = name[:5].lower()
        else: abbreviation = re.sub('[^A-Z]+', '', name).lower()
        if abbreviation in abbrevs:
            if isinstance(abbrevs[abbreviation], list): abbrevs[abbreviation].append(name)
            else:
                assigned = abbrevs[abbreviation]
                del abbrevs[abbreviation]
                abbrevs[abbreviation] = [assigned, name]
        else: abbrevs[abbreviation] = name
    return abbrevs

abbrevs = abbreviator()

def permz(msg):
    '''0 - anyone, 1 - manage messages, 2 - manage guild, 3 - admin'''
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
    '''returns a dict of channels of a given server'''
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
    '''returns a random value between specified args, defaults to 1 - 6'''
    min_, max_ = min(a, b), max(a, b)
    return randint(min_, max_)

def prefix_handler(msg, sep=' '):
    '''retrieves arguments and the command itself from a command message'''
    txt = msg.content.replace(prefix, '', 1)
    cmd = re.match(r'(^[^\s]+)', txt)[0]
    txt = txt.replace(cmd, '')
    txt = re.sub(r'(^\s+|\s+(?=\s)|\s+$)', '', txt)
    args = txt.split(sep)
    if sep != ' ':
        args = [arg for arg in map(lambda a: a.strip(), args)]
    return cmd, args

#-------------------commands-------------------

def ping(): return 'Pong! {}ms'.format(round(client.latency * 1000))

async def wot(args):
    if args[1][0] == '':
        await args[0].add_reaction('❌')
        return
    await args[0].channel.send(channels(' '.join(args[1])))

def roles(args): return '`{}`'.format(args[0].author.roles)

def dice(args):
    if args[1] == ['']: return roll()
    cs = args[1]
    a = intify(cs[0], 'ass')
    if len(cs) > 1: b = intify(cs[1], 'ass')
    else: b = 0
    if a == 'ass' or b == 'ass': return 'Wrong syntax'
    return roll(a, b)

def react(args):
    name = args[1][0]
    return ':{}:'.format(name)

async def avatar(args):
    msg = args[0]
    user = msg.author
    if msg.mentions != []: user = msg.mentions[0]
    await msg.channel.send(user.avatar_url)

async def purge(args, cap=purge_cap):
    msg, cont = args
    def purger(n): return msg.channel.purge(limit=n)
    await msg.delete()
    count = intify(cont[0])
    if count > cap: count = cap
    if count <= 10: await purger(count)
    else:
        botmsg = await msg.channel.send('You are going to purge {} messages, continue?'.format(count))
        await botmsg.add_reaction(purge_confirm_emote)
        def check(reaction, user):
            return user == msg.author and str(reaction.emoji) == purge_confirm_emote
        try:
            await client.wait_for('reaction_add', timeout=20.0, check=check)
        except asyncio.TimeoutError:
            await botmsg.delete()
        else:
            await botmsg.delete()
            while count >= 100:
                purger(100)
                count -= 100
            if count > 0: await purger(count)

async def epix_command(args):
    msg, cont = args
    await msg.delete()
    if cont[0] != '':
        pass
    elif msg.author.id == authorid:
        cont = input().split()
    else:
        await msg.channel.send('Empty fields', delete_after=3.0)
    server_name = cont.pop(0)
    channel_name = cont.pop(0)
    if channels(server_name) == False:
        await msg.channel.send('Invalid entry', delete_after=3.0)
        return
    channelid = channels(server_name)[channel_name]
    channel = client.get_channel(channelid)
    await channel.send(' '.join(cont))

operation = {
    'add': ['health'],
    'mult': ['eneCap','heaCap','eneReg','heaCap','heaCol','phyDmg','expDmg','eleDmg','heaDmg','eneDmg'],
    'mult+': ['phyRes','expRes','eleRes'],
    'reduce': ['backfire']}

def buff(stat, value, enabled, item):
    if enabled == False: return value
    if stat in operation['add'] and item['type'] == 'TORSO': return value + 350
    if stat in operation['mult']: return round(value * 1.2)
    if stat in operation['mult+']: return round(value * 1.4)
    if stat in operation['reduce']: return round(value * 0.8)
    return value

async def stats(args):
    msg, args = args
    if args[0] == '':
        await msg.add_reaction('❌')
        return
    #flags
    flags = []
    for i in ['-d', '-b', '-r']:
        if i in args: flags.append(args.pop(args.index(i)))
    buffs = '-b' in flags
    #solving for abbrevs
    name = ' '.join(args).lower()
    if name in WU_DB['item_dict']: name = WU_DB['item_dict'][name]
    elif name in abbrevs:
        if isinstance(abbrevs[name], list):
            number = len(abbrevs[name])
            first_item = abbrevs[name][0]
            final_item = abbrevs[name][-1]
            filler = ''
            if number > 2:
                for n in range(1, number - 1):
                    filler += ', **{}** for **{}**'.format(n + 1, abbrevs[name][n])
            botmsg = await msg.channel.send('Found {0} items!\nType **1** for **{1}**{2} or **{0}** for **{3}**'.format(number, first_item, filler, final_item))
            def check(m):
                return m.author == msg.author and m.channel == msg.channel
            try: reply = await client.wait_for('message', timeout=20.0, check=check)
            except asyncio.TimeoutError:
                await botmsg.add_reaction('⏰')
                return
            cont = intify(reply.content) - 1
            print(cont)
            if cont in range(0, number):
                name = abbrevs[name][cont]
            else:
                await reply.add_reaction('❌')
                return
        else: name = abbrevs[name]
    #getting the item
    item = get_item_by_id_or_name(name.lower())
    if item == None:
        await msg.add_reaction('❌')
        return
    #test flag
    if '-r' in flags:
        if permz(msg) > 2:
            await msg.channel.send(item)
            return
        else:
            await msg.add_reaction('❌')
            return
    #adding a note when -d or -b flag is included
    note = ''
    divine = False
    beef = ', buffed' if buffs else ''
    if '-d' in flags:
        divine = 'divine' in item
        note = ' (divine{})'.format(beef) if divine else ' (~~divine~~{})'.format(beef)
    elif buffs == True: note = ' (buffed)'
    #adding item stats
    item_stats = ''
    spaced = False
    WU_DB['WUabbrev']['uses'][0] = 'Use' if 'uses' in item['stats'] and item['stats']['uses'] == 1 else 'Uses'
    for k in item['stats']:
        if k in ['backfire', 'heaCost', 'eneCost'] and spaced == False:
            item_stats += '\n'
            spaced = True
        #divine handler
        pool = 'stats'
        if divine == True and k in item['divine']: pool = 'divine'
        #number range handler
        if isinstance(item['stats'][k], list):
            if len(item['stats'][k]) == 1: value = buff(k, item[pool][k][0], buffs, item) #handling one spot range
            elif item[pool][k][1] == 0: value = item[pool][k][0]
            else: value = str(buff(k, item[pool][k][0], buffs, item)) + '-' + str(buff(k, item[pool][k][1], buffs, item))
        else: value = buff(k, item[pool][k], buffs, item)
        item_stats += '{} **{}** {}\n'.format(WU_DB['WUabbrev'][k][1], value, WU_DB['WUabbrev'][k][0])
    #transform range
    min, max = item['transform_range'].split('-')
    #embedding
    embed = discord.Embed(title=item['name'], description=' '.join([item['element'].lower().capitalize(), item['type'].replace('_', ' ').lower()]), color=WU_DB['colors'][item['element']])
    fields = []
    fields.append(['Transform range: ', '*{}*'.format(''.join(WU_DB['trans_colors'][WU_DB['tiers'].index(min):WU_DB['tiers'].index(max) + 1]))])
    fields.append(['Stats{}:'.format(note), item_stats])
    for field in fields: embed.add_field(name=field[0], value=field[1], inline=False)
    img_url = WU_DB['sprite_path'] + item['name'].replace(' ', '') + '.png'
    embed.set_image(url=img_url)
    await msg.channel.send(embed=embed)

async def mechbuilder(args):
    msg = args[0]
    #title = args[1][0]
    #desc = ''.join(args[1][1:])
    title = 'Mech layout'
    slots = WU_DB['slots']
    line0 = 'Addresing items: `Weapon[n]:` `[name]`, `Module[n]:` `[name]`, `Torso:` `[name]` etc'
    line1 = '\n`1` – {0}{1}{2} – `2`      `1` – {3}{3} – `5`'.format(slots['topl'], slots['dron'], slots['topr'], slots['modl'])
    line2 = '\n`3` – {0}{1}{2} – `4`      `2` – {3}{3} – `6`'.format(slots['sidl'], slots['tors'], slots['sidr'], slots['modl'])
    line3 = '\n`5` – {0}{1}{2} – `6`      `3` – {3}{3} – `7`'.format(slots['sidl'], slots['legs'], slots['sidr'], slots['modl'])
    line4 = '\n         {0}{1}{2}               `4` – {3}{3} – `8`'.format(slots['chrg'], slots['tele'], slots['hook'], slots['modl'])
    chars = max(len(line1), len(line2), len(line3), len(line4))
    print(chars)
    line1 = line1.center(chars, ' ')
    line2 = line2.center(chars, ' ')
    line3 = line3.center(chars, ' ')
    line4 = line4.center(chars, ' ')
    desc = line0 + line1 + line2 + line3 + line4
    embed = discord.Embed(title=title, description=desc)
    await msg.channel.send(embed=embed)

async def shutdown(args):
    await args[0].channel.send('I will be back')
    await client.logout()

commands = {'ping': ping, 'say': epix_command, 'stats': stats, 'sd': shutdown, 'avatar': avatar, 'roll': dice, 'roles': roles, 'purge': purge, 'embed': mechbuilder, 'react': react}

async def trigger(msg):
    if not msg.content.startswith(prefix): return
    channel = msg.channel # default channel
    cmd, args = prefix_handler(msg)
    # checking if the command is valid
    if cmd not in commands:
        await msg.add_reaction('❌')
        return
    # checking if the user has adequate priviledges, if any necessary
    if cmd in security_lvl and permz(msg) < security_lvl[cmd]:
            await msg.add_reaction('❌')
            return
    pack = [msg, args]
    iscoroutine = inspect.iscoroutinefunction(commands[cmd])
    sig = inspect.signature(commands[cmd])
    params = sig.parameters

    if iscoroutine == False: # executing non-coros
        if len(params) == 0: result = commands[cmd]() # running no arg function
        else: result = commands[cmd](pack)
        if result != None: await channel.send(result)
        return
    else: await commands[cmd](pack)
