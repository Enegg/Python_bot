import asyncio
import json
from typing import Union


import discord
from discord.ext import commands


from functions import intify, njoin
from discotools import EmbedUI, scheduler


with open("sub_loc_list.json") as file:
    loc_list = json.load(file)

class Subverse(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.link_template = 'https://vignette.wikia.nocookie.net/submachine/images/{}.png'


    @staticmethod
    def get_loc(coord: str) -> list:
        if coord.isdigit() or len(coord) == 3 or '(' in coord:
            return [x for x in loc_list if ('coordinates' in x.keys() and x['coordinates'] == coord)]

        else:
            return [x for x in loc_list if coord.lower() in x['name'].lower() or coord in x.get('coordinates', '')]


    @staticmethod
    def key_parser(key: str) -> str:
        swap_dict = {'img': 'Dropzone', 'clues_to': 'Clues to',
            'parent': 'Clued by', 'appearances': 'Appears in', 'region': 'Region',
            'coordinates': 'Coordinates', 'area': 'Area', 'layer': 'Layer'}

        if key.startswith('sub'):
            if key[3:].isdigit():
                return f'Submachine {key[3:]}'

            key = key.replace('sub', '')

            if '_' in key:
                key = key.split('_')

            if isinstance(key, list):
                ver = ' ' + key[1]

                if key[0].isdigit():
                    return f'Submachine {key[0]}{ver}'

            else:
                ver = ''

            if 'flf' in key:
                return f'Submachine FLF{ver}'

            if 'verse' in key:
                return f'Submachine Universe{ver}'

        if str(key) in swap_dict:
            return swap_dict[key]

        return key


    @commands.command(brief='Get info about certain location from Submachine')
    async def locinfo(self, ctx: commands.Context, *args):
        keywords = {'path', 'noimg'}

        flags = keywords.intersection(args)
        name_or_cords = ' '.join(s for s in args if s not in flags).lower()

        #getting the location(s)
        matches = self.get_loc(name_or_cords)
        if not matches:
            await ctx.send('No entries.')
            return

        number = len(matches)
        if number > 1:
            if number > 20:
                await ctx.send(f'{number} matches found. Be more specific.')
                return

            first_loc = matches[0]['name']
            final_loc = matches[-1]['name']
            filler = ''.join(f', **{n + 1}** for **{matches[n]["name"]}**' for n in range(1, number - 1)) if number > 2 else ''
            botmsg = await ctx.send(
                f'Found {number} items!\n'
                f'Type **1** for **{first_loc}**{filler} or **{number}** for **{final_loc}**')
            check = lambda m: m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()

            try:
                reply = await ctx.bot.wait_for('message', timeout=20.0, check=check)

            except asyncio.TimeoutError:
                await botmsg.add_reaction('⏰')
                return

            choice = intify(reply.content) - 1
            if choice in range(number):
                location: dict = matches[choice]

            else:
                await reply.add_reaction('❌')
                return

        #only 1 match found
        else:
            location: dict = matches[0]

        if 'path' in flags:
            new_loc = location.copy()

            if 'coordinates' in new_loc:
                coords: str = new_loc['coordinates']

            else:
                coords: str = new_loc['name']

            path = [coords]

            while True:
                coords: str = new_loc.get('parent', None)

                if coords is None:
                    break
                # print(coords)

                if coords in path:
                    print('In path', path)
                    path.append(coords)
                    break

                path.append(coords)
                new_loc = self.get_loc(coords)

                if not bool(new_loc):
                    break

                new_loc = new_loc[0]

        noimg = bool('noimg' in flags)
        embed = EmbedUI(title=location['name'], color=ctx.author.color)
        embed.set_author(name=f'Requested by {ctx.author.name}', icon_url=ctx.author.avatar_url)

        if not noimg:
            embed.set_image(url=self.link_template.format(location['links']['img']))

        cont = ''
        for key, value in location.items():
            if key in {'name', 'links'}:
                continue

            key = self.key_parser(key)

            if isinstance(value, list):
                value = ', '.join(self.key_parser(x) for x in value).replace('*', r'\*')

            else:
                value = str(value).replace('*', r'\*')

            cont += f'**{key}**: {value}\n'

        if bool(cont):
            embed.add_field(name='Data:', value=cont)

        if 'path' in flags:
            embed.add_field(
                name='Path:',
                value=f"{' -> '.join(reversed(path))} ({len(path)})",
                inline=False)

        if noimg:
            await ctx.send(embed=embed)
            return

        links: dict = location['links'].copy()

        if len(links) > 1:
            links_names = [*links.keys()]
            parsed_names = [self.key_parser(x) for x in links_names]
            embed.set_footer(text=f"Available maps: {', '.join(parsed_names)}")
            embed.set_count(len(links_names))
            selection = 0
            first_run = True

            while True:
                link = self.link_template.format(links[links_names[selection]])
                embed.set_image(url=link)

                if first_run:
                    embed.add_field(name='Map:', value=parsed_names[selection])
                    embed_msg = await ctx.send(embed=embed)
                    options = await embed.add_options(embed_msg, True)
                    first_run = False

                else:
                    embed.set_field_at(-1, name='Map:', value=parsed_names[selection])
                    await embed.edit(embed_msg)

                check = lambda r, u: u == ctx.author and str(r.emoji) in options and r.message == embed_msg

                try:
                    async for (reaction, _), _ in scheduler(ctx, {'reaction_add'}, check=check, timeout=20.0):
                        if str(reaction) == '❌':
                            await embed_msg.clear_reactions()
                            raise StopAsyncIteration

                        await embed_msg.remove_reaction(reaction, ctx.author)
                        selection = embed.numbers.index(str(reaction))

                except (asyncio.TimeoutError, StopAsyncIteration) as e:
                    await embed_msg.clear_reactions()

                    if isinstance(e, asyncio.TimeoutError):
                        await embed_msg.add_reaction('⏰')

                    break
        else:
            await ctx.send(embed=embed)


    @commands.command(name='list', brief='Get names of locations from given Submachine game')
    async def locator(self, ctx: commands.Context, game: str):
        games = {f'sub{n}' for n in range(11)} | {'subflf', 'sub32', 'subverse'}
        game = game.lower()

        if game not in games:
            await ctx.message.add_reaction('❌')
            return

        locs = [x['name'] for x in loc_list if game in x['appearances']]
        count = len(locs)
        if count > 20:
            locs.sort(key=lambda i: (len(i), i))
            uneven = ''

            if count % 2:
                uneven: str = locs.pop()

            count //= 2
            left, right = locs[:count], locs[count:]
            l = len(left[-1])
            left = [f'{x:<{l}}' for x in left]
            # left = [x.ljust(l) for x in left]

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

            result += f'{uneven}```'

            fields.append(result)

        else:
            fields = [f'```{njoin(locs)}```']

        embed = discord.Embed(
            title='Locations list:',
            description=fields.pop(0),
            color=discord.Color.random())
    
        for field in fields:
            embed.add_field(name='<:none:772958360240128060>', value=field)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Subverse(bot))
    print('Subverse loaded')
