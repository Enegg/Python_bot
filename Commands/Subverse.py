from discord.ext import commands
import discord
import json
import asyncio
from functions import intify, random_color
from discotools import supreme_listener, EmbedUI

with open("sub_loc_list.json") as file:
    loc_list = json.load(file)

class Subverse(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_loc(self, discriminator):
        if discriminator.isdigit() or len(discriminator) == 3:
            return [x for x in loc_list if ('coordinates' in x.keys() and x['coordinates'] == discriminator)]
        else:
            return [x for x in loc_list if discriminator.lower() in x['name'].lower() or ('coordinates' in x.keys() and x['coordinates'] == discriminator)]

    def key_parser(self, key):
        swap_dict = {'img': 'Dropzone', 'clues_to': 'Clues to', 'parent': 'Clued by', 'appearances': 'Appears in', 'region': 'Region', 'coordinates': 'Coordinates', 'area': 'Area', 'layer': 'Layer'}
        if str(key).startswith('sub'):
            if key[3:].isdigit():
                return f'Submachine {key[3:]}'
            key = key.replace('sub', '')
            if '_' in key:
                key = key.split('_')
            if isinstance(key, list):
                ver = ' ' + key[1]
                if key[0].isdigit(): return f'Submachine {key[0]}{ver}'
            else: ver = ''
            if 'flf' in key: return f'Submachine FLF{ver}'
            if 'verse' in key: return f'Submachine Universe{ver}'


        if str(key) in swap_dict: return swap_dict[key]
        return key

    @commands.command(brief='Get info about certain location from Submachine')
    async def loc(self, ctx, *args):
        if ctx.invoked_subcommand is None:
            keywords = ['path', 'noimg']
            args = list(args)
            flags = [args.pop(args.index(i)) for i in keywords if i in args]
            name_or_cords = ' '.join(args)

            #getting the location(s)
            matches = self.get_loc(name_or_cords)
            if not matches:
                await ctx.send('No entries.')
                return
            if (number := len(matches)) > 1:
                if number > 20:
                    await ctx.send(f'{number} matches found. Be more specific.')
                    return
                first_loc = matches[0]['name']
                final_loc = matches[-1]['name']
                filler = ''.join(map(lambda n: ', **{}** for **{}**'.format(n + 1, matches[n]['name']), range(1, number - 1))) if number > 2 else ''
                botmsg = await ctx.send(f'Found {number} items!\nType **1** for **{first_loc}**{filler} or **{number}** for **{final_loc}**')
                try: reply = await ctx.bot.wait_for('message', timeout=20.0, check=lambda m: m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit())
                except asyncio.TimeoutError:
                    await botmsg.add_reaction('⏰')
                    return
                choice = intify(reply.content) - 1
                if choice in range(0, number): location = matches[choice]
                else:
                    await reply.add_reaction('❌')
                    return
            #only 1 match found
            else: location = matches[0]

            keys = location.keys()

            if 'path' in flags:
                first_run = True
                new_loc = location.copy()
                if 'coordinates' in new_loc:
                    coords = new_loc['coordinates']
                    if isinstance(coords, list): coords = ', '.join(coords)
                else: coords = new_loc['name']
                path = [coords]
                new_keys = new_loc.keys()
                while True:
                    if 'parent' not in new_keys:
                        if first_run:
                            await ctx.send('This location has no parent data.')
                            return
                        break
                    first_run = False
                    coords = new_loc['parent']
                    # print(coords)
                    if coords in path:
                        print('In path', path)
                        path.append(coords)
                        break
                    path.append(coords)
                    new_loc = self.get_loc(coords)
                    if not bool(new_loc): break
                    new_loc = new_loc[0]
                    new_keys = new_loc.keys()

            noimg = bool('noimg' in flags)
            embed = EmbedUI(ctx=ctx, title=location['name'], color=discord.Color.from_rgb(*random_color())).set_author(name=f'Requested by {ctx.author.name}', icon_url=ctx.author.avatar_url)
            if not noimg: embed.set_image(url=location['links']['img'])
            cont = ''
            for key in keys:
                if key in ['name', 'links']: continue
                value = location.get(key)
                key = self.key_parser(key)
                if isinstance(value, list):
                    value = ', '.join(self.key_parser(x) for x in value).replace('*', r'\*')
                    cont += f'**{key}**: {value}\n'
                else:
                    value = str(value).replace('*', r'\*')
                    cont += f'**{key}**: {value}\n'
            if bool(cont): embed.add_field(name='Data:', value=cont)
            if 'path' in flags: embed.add_field(name='Path:', value=' -> '.join(reversed(path)) + f' ({len(path)})', inline=False)

            if noimg:
                await ctx.send(embed=embed)
                return
            links = location['links'].copy()
            if bool(len(links) - 1):
                links_names = [x for x in links.keys()]
                translated_link_names = [self.key_parser(x) for x in links_names]
                text = 'Available links: ' + ', '.join(translated_link_names)
                embed.set_footer(text=text)
                links_number = len(links_names)
                embed.set_count(links_number)
                selection = 0
                first_run = True
                while True:
                    link = links[links_names[selection]]
                    embed.set_image(url=link)
                    if first_run:
                        embed.add_field(name='Map:', value=translated_link_names[selection])
                        embed_msg = await ctx.send(embed=embed)
                        options = await embed.add_options(embed_msg, True)
                        first_run = False
                    else:
                        embed.set_field_at(-1, name='Map:', value=translated_link_names[selection])
                        await embed.edit(embed_msg)
                    try: selection = (await supreme_listener(ctx, *options, add_cancel=True))[0]
                    except asyncio.TimeoutError:
                        await embed_msg.clear_reactions()
                        await embed_msg.add_reaction('⏰')
                        break
                    if selection == -2:
                        await embed_msg.clear_reactions()
                        return
                    await embed_msg.remove_reaction(embed.numbers[selection], ctx.author)
            else: await ctx.send(embed=embed)

    @commands.command(name='list', brief='Get names of locations from given Submachine game')
    async def locator(self, ctx, game):
        keys = {'sub0', 'sub1', 'sub2', 'sub3', 'sub4', 'sub5', 'sub6', 'sub7', 'sub8', 'sub9', 'sub10', 'subflf', 'sub32', 'subverse'}
        game = game.lower()
        if game not in keys:
            await ctx.message.add_reaction('❌')
            return
        locs = [x['name'] for x in loc_list if game in x['appearances']]
        if (count := len(locs)) > 20:
            locs.sort(key=lambda i: (len(i), i))
            uneven = ''
            if count % 2:
                uneven = locs.pop()
                count -= 1
            count //= 2
            left, right = locs[:count], locs[count:]
            longest_entry = left[-1]
            left = [x.ljust(len(longest_entry)) for x in left]


            # longest_entry = max(locs, key=len)
            # right, left = [], []
            # [(left.append(x) if locs.index(x) % 2 else right.append(x.ljust(len(longest_entry)))) for x in locs]

            result = '```'
            limit = 2048
            fields = []
            for x in zip(left, right):
                if len(result + str(x)) > limit:
                    limit = 1024
                    result += '```'
                    fields.append(result)
                    result = '```'
                result += f'{x[0]}  {x[1]}\n'

            # if len(right) != len(left):
            #     uneven = max(right, left, key=len)
            #     last = uneven.pop(-1).strip()
            #     result += last

            result += f'{uneven}```'

            fields.append(result)
        else: fields = ['```{}```'.format('\n'.join(locs))]
        embed = discord.Embed(title='Locations list:', description=fields.pop(0), color=discord.Color.from_rgb(*random_color()))
        for field in fields:
            embed.add_field(name='<:none:742507182918074458>', value=field, inline=True)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Subverse(bot))
    print('Subverse loaded')
