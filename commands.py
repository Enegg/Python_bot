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
default_activity = discord.Game('with portals')

prefix = prefix_local if socket.gethostname() == 'Mystery_machine' else prefix_host

#------------------functions-------------------
def get_item_by_id_or_name(value):
  for item in items_list:
    if str(item['id']) == str(value) or item['name'].lower() == str(value).lower():
      return item
  return None

def emojifier():
    emojis, normal, animated = {}, [], []
    for guild in client.guilds:
        for emoji in guild.emojis:
            name = emoji.name
            if emoji.animated: animated.append(emoji)
            else: normal.append(emoji)
            if name in emojis:
                if isinstance(emojis[name], list): emojis[name].append(emoji)
                else:
                    assigned = emojis[name]
                    del emojis[name]
                    emojis[name] = [assigned, emoji]
            else: emojis[name] = emoji
    emojis['normal'], emojis['animated'] = normal, animated
    return emojis

def common_items(lists):
    if len(lists) == 0: return lists
    result, first_run = [], True
    while len(lists) >= 1:
        a = lists.pop() if first_run else result
        result, first_run = [], False
        if len(lists) > 0:
            b = lists.pop()
            if len(a) > len(b): a, b = b, a
            result = list(filter(lambda x: x in b, a))
    return result

def search_for(phrase, iterable):
    if not iterable: return iterable
    phrase = r'\b' + re.sub('[^a-z ]+', '', phrase).replace(' ', '.+ ')
    return list(filter(lambda i: re.search(phrase, i.lower()), list(iterable)))

def abbreviator():
    names = []
    abbrevs = {}
    for item in items_list:
        name = item['name']
        names.append(name)
        if len(name) < 8: continue
        if ' ' in name or not name[1:].islower(): abbreviation = re.sub('[^A-Z]+', '', name).lower()
        else: continue
        abbrevs[abbreviation].append(name) if abbreviation in abbrevs else abbrevs.update({abbreviation: [name]})
    return abbrevs, names

abbrevs, names = abbreviator()

def permz(msg):
    '''0 - no perms, 1 - manage messages, 2 - manage guild, 3 - admin'''
    permKeys, power = ['manage_messages', 'manage_guild', 'administrator'], 0
    if msg.author.id == authorid: return len(permKeys) + 1
    if isinstance(msg.channel, discord.DMChannel): return 0 
    for key in permKeys:
        for role in msg.author.roles:
            if getattr(role.permissions, key):
                power = permKeys.index(key) + 1
                break
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

def guilds_channels(): return dict(map(lambda guild: (guild.name, guild.channels), client.guilds))

roll = lambda a=1, b=6: randint(min(a, b), max(a, b))

def prefix_handler(msg, sep=' '):
    '''retrieves arguments and the command itself from a command message'''
    txt = msg.content.replace(prefix, '', 1)
    cmd = re.match(r'(^[^\s]+)', txt)[0]
    args = re.sub(r'(^\s+|\s+(?=\s)|\s+$)', '', txt.replace(cmd, '')).split(sep)
    if sep != ' ': args = [arg for arg in map(lambda a: a.strip(), args)]
    return cmd, args

@client.event
async def on_ready():
    print(client.user.name + ' is here to take over the world')
    print('----------------')
    global emojis, guild_channels_cache
    emojis = emojifier()
    guild_channels_cache = guilds_channels()
    await client.change_presence(activity=default_activity)

def channels_id(guild_name):
    '''returns a dict of channels' id's of a given server'''
    if guild_name not in guild_channels_cache:
        if guild_name not in abbreviations: return {}
        guild_name = abbreviations[guild_name]
    return dict(map(lambda channel: (channel.name, channel.id), filter(lambda channel: isinstance(channel, discord.channel.TextChannel), guild_channels_cache[guild_name])))
     

#-------------------commands-------------------

def ping(): return f'Pong! {round(client.latency * 1000)}ms'

def frantic(): return 'https://i.imgur.com/Bbbf4AH.mp4'

async def wot(args):
    if args[1][0] == '':
        await args[0].add_reaction('❌')
        return
    cont = channels_id(' '.join(args[1]))
    if cont == {}:
        await args[0].add_reaction('❌')
        return
    await args[0].channel.send(cont)

async def activity(args):
    args = args[1]
    ActType = discord.ActivityType
    activities = {'watching': ActType.watching, 'listening': ActType.listening, 'playing': ActType.playing, 'streaming': ActType.streaming}
    for k in ['watching', 'listening', 'playing', 'streaming']:
        if k in args:
            args.pop(args.index(k))
            ActType = activities[k]
    activity = discord.Activity(name=' '.join(args),type=ActType)
    await client.change_presence(activity=activity)

def roles(args): return '`{}`'.format(args[0].author.roles)

def dice(args):
    if args[1] == ['']: return roll()
    cs = args[1]
    a = intify(cs[0])
    if len(cs) > 1: b = intify(cs[1])
    else: b = 0
    return roll(a, b)

async def react(args):
    msg = args[0]
    channel = msg.channel
    channel_check = isinstance(channel, discord.DMChannel)
    arg = ' '.join(args[1])
    if arg == 'animated' or arg == 'normal':
        if not channel_check:
            await channel.send('You can use that only in DMs.', delete_after=10.0)
            return
        bank = emojis[arg]
        string = ''
        list_strings = []
        for item in bank:
            emoji = '<{}:{}:{}>'.format('a' if item.animated else '', item.name, item.id)
            if len(string + emoji) > 2000:
                list_strings.append(string)
                string = ''
            string += emoji
        list_strings.append(string)
        for x in list_strings: await channel.send(x)
        return
    if arg in emojis:
        if isinstance(emojis[arg], list):
            for emoji in emojis[arg]:
                await msg.add_reaction(emoji)
            try: reaction = await client.wait_for('reaction_add', timeout=10.0, check=lambda reaction, user: user == msg.author and reaction.emoji in emojis[arg])
            except asyncio.TimeoutError:
                await msg.delete()
                return
            await channel.send(reaction[0])
        else:
            await channel.send(emojis[arg])
    if not channel_check: await msg.delete()

def avatar(args): return (args[0].mentions[0] if args[0].mentions != [] else args[0].author).avatar_url

async def purge(args, cap=purge_cap):
    msg, cont = args
    def purger(n): return msg.channel.purge(limit=n, check=lambda m: not m.pinned and (m.author == msg.mentions[0] if msg.mentions != [] else True))
    await msg.delete()
    count = intify(cont[0])
    if count > cap: count = cap
    if count <= 10: await purger(count)
    else:
        botmsg = await msg.channel.send('You are going to purge {} messages{}, continue?'.format(count, f' of {msg.mentions[0]}' if msg.mentions[0] != [] else ''))
        await botmsg.add_reaction(purge_confirm_emote)
        try: await client.wait_for('reaction_add', timeout=20.0, check=lambda reaction, user: user == msg.author and str(reaction.emoji) == purge_confirm_emote)
        except asyncio.TimeoutError: await botmsg.delete()
        else:
            await botmsg.delete()
            while count >= 100:
                purger(100)
                count -= 100
            if count > 0: await purger(count)

async def epix_command(args):
    msg, cont = args
    await msg.delete()
    if cont[0] != '': pass
    elif msg.author.id == authorid: cont = input().split()
    else: await msg.channel.send('Empty fields', delete_after=3.0)
    server_name, channel_name = cont.pop(0), cont.pop(0)
    if channels_id(server_name) == {}:
        await msg.channel.send('Invalid entry', delete_after=3.0)
        return
    channelid = channels_id(server_name)[channel_name]
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
    #flags ['-d', '-b', '-r']
    flags = list(map(lambda e: args.pop(args.index(e)), filter(lambda i: i in args, ['-d', '-b', '-r'])))
    buffs = '-b' in flags
    #solving for abbrevs
    name = ' '.join(args).lower()
    if intify(name) == 0 and len(name) < 2:
        await msg.add_reaction('❌')
        return
    if name not in names:
        results = search_for(name, names)
        abbrev_1 = True if name in abbrevs else False
        abbrev_2 = True if results != [] else False
        if abbrev_1 or abbrev_2:
            match_1 = abbrevs[name] if abbrev_1 else []
            match_2 = results if abbrev_2 else []
            matches = match_1 + match_2
            for match in matches:
                while matches.count(match) > 1: matches.remove(match)
            number = len(matches)
            if number > 10:
                await msg.channel.send('Over 10 matches found, be more specific.')
                return
            if number > 1:
                first_item = matches[0]
                final_item = matches[-1]
                filler = ''.join(map(lambda n: ', **{}** for **{}**'.format(n + 1, matches[n]), range(1, number - 1))) if number > 2 else ''
                botmsg = await msg.channel.send(f'Found {number} items!\nType **1** for **{first_item}**{filler} or **{number}** for **{final_item}**')
                try: reply = await client.wait_for('message', timeout=20.0, check=lambda m: m.author == msg.author and m.channel == msg.channel and m.content.isdigit())
                except asyncio.TimeoutError:
                    await botmsg.add_reaction('⏰')
                    return
                cont = intify(reply.content) - 1
                if cont in range(0, number): name = matches[cont]
                else:
                    await reply.add_reaction('❌')
                    return
            else: name = matches[0]
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
        note = f' (divine{beef})' if divine else f' (~~divine~~{beef})'
    elif buffs: note = ' (buffed)'
    #adding item stats
    item_stats = ''
    spaced = False
    WU_DB['WUabbrev']['uses'][0] = 'Use' if 'uses' in item['stats'] and item['stats']['uses'] == 1 else 'Uses'
    for k in item['stats']:
        if k in ['backfire', 'heaCost', 'eneCost'] and not spaced:
            item_stats += '\n'
            spaced = True
        #divine handler
        pool = 'divine' if divine and k in item['divine'] else 'stats'
        #number range handler
        if isinstance(item['stats'][k], list):
            if len(item['stats'][k]) == 1: value = buff(k, item[pool][k][0], buffs, item) #handling one spot range
            elif item[pool][k][1] == 0: value = item[pool][k][0]
            else: value = str(buff(k, item[pool][k][0], buffs, item)) + '-' + str(buff(k, item[pool][k][1], buffs, item))
        else: value = buff(k, item[pool][k], buffs, item)
        item_stats += '{} **{}** {}\n'.format(WU_DB['WUabbrev'][k][1], value, WU_DB['WUabbrev'][k][0])
    if 'advance' in item['stats'] or 'retreat' in item['stats']: item_stats += '{} **Jumping required**'.format(WU_DB['WUabbrev']['jump'][1])
    #transform range
    min_, max_ = item['transform_range'].split('-')
    #embedding
    embed = discord.Embed(title=item['name'], description=' '.join([item['element'].lower().capitalize(), item['type'].replace('_', ' ').lower()]), color=WU_DB['colors'][item['element']])
    fields = []
    fields.append(['Transform range: ', '*{}*'.format(''.join(WU_DB['trans_colors'][WU_DB['tiers'].index(min_):WU_DB['tiers'].index(max_) + 1]))])
    fields.append([f'Stats{note}:', item_stats])
    for field in fields: embed.add_field(name=field[0], value=field[1], inline=False)
    img_url = WU_DB['sprite_path'] + item['name'].replace(' ', '') + '.png'
    embed.set_image(url=img_url)
    embed.set_thumbnail(url=WU_DB['type'][item['type']])
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

commands = {'ping': ping, 'say': epix_command, 'stats': stats, 'sd': shutdown, 'avatar': avatar, 'roll': dice, 'roles': roles, 'purge': purge, 'embed': mechbuilder, 'react': react, 'activity': activity, 'wot': wot, 'frantic': frantic}

async def trigger(msg):
    if not msg.content.startswith(prefix): return
    if prefix == prefix_local and permz(msg) < 3: return
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
        if isinstance(result, tuple):
            result, delete = result
            if delete and not isinstance(msg.channel, discord.DMChannel): await msg.delete()
        if result != None: await channel.send(result)
        return
    else: await commands[cmd](pack)
