# Work with Python 3.6
import discord
import asyncio
import json
import requests
import os
import importlib
import socket
from config import authorid, prefix, abbreviations, WUabbrev, trans_range, tiers, colors, item_dict, link
from commands import prefix_handler, trigger, purge, roll_handler, permz, epix_command, channels, buff
client = discord.Client()

TOKEN = None

if socket.gethostname() == 'Mystery_machine':
    TOKEN = importlib.import_module('TOKEN').TOKEN
else:
    TOKEN = os.environ.get('TOKEN')

if not TOKEN:
    raise 'Not running localy and TOKEN is not an environment variable'

@client.event
async def on_message(message):
    if message.author == client.user: return
    channel = message.channel

    if trigger(message, 'roles'): await channel.send('`{}`'.format(message.author.roles))

    if trigger(message, 'ping'): await channel.send('Pong! {}ms'.format(round(client.latency * 1000)))

    if trigger(message, 'pig'): await channel.send('🐷')

    if trigger(message, 'roll'): await channel.send(roll_handler(message))

    if trigger(message, 'wot') and permz(message) > 1: await channel.send(channels(prefix_handler(message)[1][0]))

    if trigger(message, 'purge') and permz(message) > 0: await purge(message)

    if trigger(message, 'sd') and permz(message) > 1:
        await channel.send('I will be back')
        await client.logout()

    if trigger(message, 'say') and permz(message) > 2: await epix_command(message)

    if trigger(message, 'stats'):
        args = prefix_handler(message)[1]
        if args[0] == '':
            await channel.send('Funny command huh')
            return
        #flags
        flags = []
        for i in ['-d', '-b', '-r']:
            if i in args: flags.append(args.pop(args.index(i)))
        buffs = '-b' in flags
        #solving for abbrevs
        name = ' '.join(args).lower()
        if name in item_dict: name = item_dict[name]
        item = json.loads(requests.get(link + name).text)
        #test flag
        if '-r' in flags:
            if permz(message) > 2:
                await channel.send(item)
                return
            else:
                await message.add_reaction('❌')
                return
        #error handling
        if 'message' in item:
            await message.add_reaction('❌')
            return
        #adding a note when -d or -b flag is included
        note = ''
        divine = False
        beef = ', buffed' if buffs else ''
        if '-d' in flags:
            divine = 'divine' in item
            note = ' (divine{})'.format(beef) if divine else ' (no divine stats yet{})'.format(beef)
        elif buffs == True: note = ' (buffed)'
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
                if k in item['divine']: y = 'divine'
            #number range handler
            if isinstance(item['stats'][k], list):
                #handling one spot range
                if len(item['stats'][k]) == 1:
                    value = buff(k, item[y][k][0], buffs)
                elif item[y][k][1] == 0: value = item[y][k][0]
                else: value = str(buff(k, item[y][k][0], buffs)) + '-' + str(buff(k, item[y][k][1], buffs))
            else: value = buff(k, item[y][k], buffs)
            item_stats = item_stats + '**{}**'.format(value) + ' {}\n'.format(WUabbrev[k])
        #embedding
        embed = discord.Embed(title=item['name'], description=' '.join([item['element'].lower().capitalize(), item['type'].replace('_', ' ').lower()]), color=colors[item['element']])
        #transform range
        min, max = item['transform_range'].split('-')
        fields = []
        fields.append(['Transform range: ', '{}'.format(''.join(trans_range[tiers.index(min):tiers.index(max) + 1]))])
        fields.append(['Stats{}:'.format(note), item_stats])
        for field in fields: embed.add_field(name=field[0], value=field[1], inline=False)
        img_url = 'https://workshopunlimited.herokuapp.com/img/items/' + item['name'].replace(' ', '') + '.png'
        embed.set_image(url=img_url)
        await channel.send(embed=embed)

@client.event
async def on_ready():
    print(client.user.name + ' is here to take over the world')
    print('----------------')

loop = asyncio.get_event_loop()
task = loop.create_task(client.run(TOKEN))
try:
    loop.run_until_complete(task)
except KeyboardInterrupt:
    pass
    #loop.run_until_complete(logout())
finally:
    loop.close()
