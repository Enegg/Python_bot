from discord.ext import commands
import discord
import asyncio
from functions import search_for, intify, perms, supreme_listener, random_color, split_to_fields
import json
import re
import urllib
from Commands.Testing import EmbedUI
from typing import Dict, Iterable

with open('items.json') as file:
    items_list = json.load(file)

operation_lookup = {
    'mult': ['eneCap', 'heaCap', 'eneReg', 'heaCap', 'heaCol', 'phyDmg', 'expDmg', 'eleDmg', 'heaDmg', 'eneDmg'],
    'mult+': ['phyRes', 'expRes', 'eleRes'],
    'reduce': ['backfire']}
item_type = {
    'TOP_WEAPON': ['https://i.imgur.com/LW7ZCGZ.png', '<:topr:730115786735091762>'],
    'SIDE_WEAPON': ['https://i.imgur.com/CBbvOnQ.png', '<:sider:730115747799629940>'],
    'TORSO': ['https://i.imgur.com/iNtSziV.png', '<:torso:730115680363347968>'],
    'LEGS': ['https://i.imgur.com/6NBLOhU.png', '<:legs:730115699397361827>'],
    'DRONE': ['https://i.imgur.com/oqQmXTF.png', '<:drone:730115574763618394>'],
    'CHARGE': ['https://i.imgur.com/UnDqJx8.png', '<:charge:730115557239685281>'],
    'TELEPORTER': ['https://i.imgur.com/Fnq035A.png', '<:tele:730115603683213423>'],
    'HOOK': ['https://i.imgur.com/8oAoPcJ.png', '<:hook:730115622347735071>'],
    'MODULE': ['https://i.imgur.com/dQR8UgN.png', '<:mod:730115649866694686>']}
tier_colors = ['⚪', '🔵', '🟣', '🟠', '🟤', '⚪']
item_tiers = ['C', 'R', 'E', 'L', 'M', 'D']
element_colors = {'PHYSICAL': 0xffb800, 'EXPLOSIVE': 0xb71010, 'ELECTRIC': 0x106ed8, 'COMBINED': 0x211d1d}
slot_emojis = {
    'topl': '<:topl:730115768431280238>',
    'topr': '<:topr:730115786735091762>',
    'dron': '<:drone:730115574763618394>',
    'sidl': '<:sidel:730115729365663884>',
    'sidr': '<:sider:730115747799629940>',
    'tors': '<:torso:730115680363347968>',
    'legs': '<:legs:730115699397361827>',
    'chrg': '<:charge:730115557239685281>',
    'tele': '<:tele:730115603683213423>',
    'hook': '<:hook:730115622347735071>',
    'modl': '<:mod:730115649866694686>',
    'none': '<:none:772958360240128060>'}
stat_abbrev = {
    'weight': ['Weight', '<:weight:725870760484143174>'],
    'health': ['HP', '<:health:725870887588462652>'],
    'eneCap': ['Energy', '<:energy:725870941883859054>'],
    'eneReg': ['Regeneration', '<:regen:725871003665825822>'],
    'heaCap': ['Heat', '<:heat:725871043767435336>'],
    'heaCol': ['Cooling', '<:cooling:725871075778363422>'],
    'phyRes': ['Physical resistance', '<:phyres:725871121051811931>'],
    'expRes': ['Explosive resistance', '<:expres:725871136935772294>'],
    'eleRes': ['Electric resistance', '<:elecres:725871146716758077>'],
    'phyDmg': ['Damage', '<:phydmg:725871208830074929>'],
    'phyResDmg': ['Resistance drain', '<:phyresdmg:725871259635679263>'],
    'expDmg': ['Damage', '<:expdmg:725871223338172448>'],
    'heaDmg': ['Heat damage', '<:headmg:725871613639393290>'],
    'heaCapDmg': ['Heat capacity drain', '<:heatcapdmg:725871478083551272>'],
    'heaColDmg': ['Cooling damage', '<:coolingdmg:725871499281563728>'],
    'expResDmg': ['Resistance drain', '<:expresdmg:725871281311842314>'],
    'eleDmg': ['Damage', '<:eledmg:725871233614479443>'],
    'eneDmg': ['Energy drain', '<:enedmg:725871599517171719>'],
    'eneCapDmg': ['Energy capacity drain', '<:enecapdmg:725871420126789642>'],
    'eneRegDmg': ['Regeneration damage', '<:regendmg:725871443815956510>'],
    'eleResDmg': ['Resistance drain', '<:eleresdmg:725871296381976629>'],
    'range': ['Range', '<:range:725871752072134736>'],
    'push': ['Knockback', '<:push:725871716613488843>'],
    'pull': ['Pull', '<:pull:725871734141616219>'],
    'recoil': ['Recoil', '<:recoil:725871778282340384>'],
    'retreat': ['Retreat', '<:retreat:725871804236955668>'],
    'advance': ['Advance', '<:advance:725871818115907715>'],
    'walk': ['Walking', '<:walk:725871844581834774>'],
    'jump': ['Jumping', '<:jump:725871869793796116>'],
    'uses': ['', '<:uses:725871917923303688>'],
    'backfire': ['Backfire', '<:backfire:725871901062201404>'],
    'heaCost': ['Heat cost', '<:heatgen:725871674007879740>'],
    'eneCost': ['Energy cost', '<:eneusage:725871660237979759>']}
url_template = 'https://raw.githubusercontent.com/ctrl-raul/workshop-unlimited/master/items/{}.png'
item_element = {
    'PHYSICAL': stat_abbrev['phyDmg'][1],
    'EXPLOSIVE': stat_abbrev['expDmg'][1],
    'ELECTRIC': stat_abbrev['eleDmg'][1],
    'COMBINED': '🔰'}

class SuperMechs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.abbrevs = {}
        self.names = []
        self.image_url_cache = {}

    def get_item_by_id_or_name(self, value: str):
        for item in items_list:
            if str(item['id']) == str(value) or item['name'].lower() == str(value):
                return item
        return None

    def abbreviator(self):
        r'''Helper func which creates abbrevs for items'''
        names = []
        abbrevs = {}
        for item in items_list:
            name = item['name']
            names.append(name)
            if len(name) < 8:
                continue
            if ' ' in name or not name[1:].islower():
                abbreviation = re.sub('[^A-Z]+', '', name).lower()
            else:
                continue
            abbrevs[abbreviation].append(name) if abbreviation in abbrevs else abbrevs.update({abbreviation: [name]})
        self.abbrevs, self.names = abbrevs, names

    def get_image(self, item) -> str('ItemImageLink'):
        safe_name = item['name'].replace(' ', '')
        url = url_template.format(safe_name)

        if not item['id'] in self.image_url_cache:
            try:
                urllib.request.urlopen(url)
            except urllib.error.HTTPError:
                self.image_url_cache[item['id']] = item_type[item['type']][0]
            else: self.image_url_cache[item['id']] = url
        return self.image_url_cache[item['id']]

    def ressolve_args(self, args: Iterable):
        '''Takes command arguments as an input and tries to match them as key item pairs'''
        args = [a.lower() for a in args]
        specs = {}  # dict of data type: desired data, like 'element': 'explosive'
        ingored_args = set()
        for arg in args:
            if ':' not in arg:
                ingored_args.add(arg)
                continue
            if arg.endswith(':'):  # if True, the next item in args should be treated as a value
                index = args.index(arg)
                if index + 1 >= len(args):
                    raise Exception(f'Obscure argument "{arg}"')
                value = args.pop(index + 1).lower()
                if ':' in value:
                    raise SyntaxError(f'"{value}" preceeding "{arg}"')
                specs.update({arg.replace(':', ''): value})
            else:
                arg, value = arg.lower().split(':')
                specs.update({arg: value.strip()})
        return specs, ingored_args

    def specs(self, item):
        return {'type': item_type[item['type']][1], 'element': item_element[item['element']], 'tier': tier_colors[item_tiers.index(item['transform_range'].split('-')[0])]}

    def emoji_for_browseitems(self, item, spec_filter: Dict['ItemStat', 'StatValue']):
        specs = self.specs(item)
        return ''.join(specs[spec] for spec in specs if spec not in spec_filter)

    @commands.command(brief='Show to a frantic user where is his place')
    async def frantic(self, ctx):
        await ctx.send('https://i.imgur.com/Bbbf4AH.mp4')

    def buff(self, stat, value: int, enabled: bool, item) -> int:
        if not enabled: # the function is always called, that probably could be improved
            return value
        if stat in operation_lookup['mult']:
            return round(value * 1.2)
        if stat in operation_lookup['mult+']:
            return round(value * 1.4)
        if stat in operation_lookup['reduce']:
            return round(value * 0.8)
        return value

    @commands.command(usage='[item name / part of the name]', brief='Inspect an item\'s stats', help='To use the command, type in desired item\'s name or its abbreviation, like "efa" for "energy free armor".')
    @commands.cooldown(2, 15.0, commands.BucketType.member)
    async def stats(self, ctx, *args):
        msg = ctx.message
        add_x = msg.add_reaction
        if not bool(args):
            await add_x('❌')
            return
        args = list(args)
        #flags {'-r'}
        flags = [args.pop(args.index(i)) for i in {'-r'} if i in args]
        #solving for abbrevs
        name = ' '.join(args).lower()
        if intify(name) == 0 and len(name) < 2:
            await add_x('❌')
            return

        #returning the exact item name from short user input
        if not self.abbrevs or not self.names: self.abbreviator()
        if name not in self.names and not name.isdigit():
            results = search_for(name, self.names)
            is_in_abbrevs = bool(name in self.abbrevs)
            is_in_results = bool(results)
            if is_in_abbrevs or is_in_results:
                match = self.abbrevs[name] if is_in_abbrevs else []
                matches = match + results
                for match in matches:
                    while matches.count(match) > 1: matches.remove(match)
                number = len(matches)
                if number > 10:
                    await ctx.send('Over 10 matches found, be more specific.')
                    return
                #more than 1 match found
                if number > 1:
                    first_item = matches[0]
                    final_item = matches[-1]
                    filler = ''.join(f', **{n}** for **{matches[n-1]}**' for n in range(2, number)) if number > 2 else ''
                    botmsg = await ctx.send(f'Found {number} items!\nType **1** for **{first_item}**{filler} or **{number}** for **{final_item}**')
                    try: reply = await ctx.bot.wait_for('message', timeout=20.0, check=lambda m: m.author == msg.author and m.channel == ctx.channel and m.content.isdigit())
                    except asyncio.TimeoutError:
                        await botmsg.add_reaction('⏰')
                        return
                    choice = intify(reply.content) - 1
                    if choice in range(number): name = matches[choice]
                    else:
                        await reply.add_reaction('❌')
                        return
                #only 1 match found
                else: name = matches[0]
        
        #getting the item
        item = self.get_item_by_id_or_name(name.lower())
        if item is None:
            await add_x('❌')
            return
        #test flag
        if '-r' in flags:
            await ctx.send(item)
            return
        #adding a note when -b flag is included
        emojis = ['🇧']
        if bool('divine' in item): emojis.append('🇩')
        #embedding
        embed = EmbedUI(ctx, emojis, title=item['name'], description=' '.join([item['element'].lower().capitalize(), item['type'].replace('_', ' ').lower()]), color=element_colors[item['element']])
        img_url = self.get_image(item)
        has_image = bool('imgur' not in img_url) #yeah I know, hack
        embed.set_image(url=img_url)
        if has_image: embed.set_thumbnail(url=item_type[item['type']][0])
        embed.set_author(name=f'Requested by {ctx.author.display_name}', icon_url=ctx.author.avatar_url)
        embed.set_footer(text='React with B for arena buffs or D for divine stats (if applicable)')
        stat_abbrev['uses'][0] = ('Use' if 'uses' in item['stats'] and item['stats']['uses'] == 1 else 'Uses')
        #adding item stats
        _min, _max = item['transform_range'].split('-')

        first_run, divine, buffs = True, False, False
        while True:
            item_stats = ''
            spaced = False
            for stat in item['stats']:
                if stat in {'backfire', 'heaCost', 'eneCost'} and not spaced:
                    item_stats += '\n'
                    spaced = True
                #divine handler
                pool = 'divine' if divine and stat in item['divine'] else 'stats'
                #number range handler
                if isinstance(item['stats'][stat], list):
                    if len(item['stats'][stat]) == 1:
                        value = self.buff(stat, item[pool][stat][0], buffs, item) #handling one spot range

                    elif item[pool][stat][1] == 0:
                        value = item[pool][stat][0]

                    else:
                        value = str(self.buff(stat, item[pool][stat][0], buffs, item)) + '-' + str(self.buff(stat, item[pool][stat][1], buffs, item))
                else:
                    value = self.buff(stat, item[pool][stat], buffs, item)

                item_stats += f"{stat_abbrev[stat][1]} **{value}** {stat_abbrev[stat][0]}\n"
            if 'advance' in item['stats'] or 'retreat' in item['stats']: item_stats += f"{stat_abbrev['jump'][1]} **Jumping required**"
            #transform range
            if (maximal := item_tiers.index(_max)) < 4: tier = maximal
            elif divine: tier = 5
            else: tier = 4
            colors = tier_colors.copy()
            colors.insert(tier, f'({colors.pop(tier)})')
            fields = []
            note = ' (buffs applied)' if buffs else ''
            fields.append({'name': 'Transform range: ', 'value': f"{''.join(colors[item_tiers.index(_min):item_tiers.index(_max) + 1])}", 'inline': False})
            fields.append({'name': f'Stats{note}:', 'value': item_stats, 'inline': False})
            for field in fields: embed.add_field(**field)

            if first_run:
                embed.set_count(len(emojis))
                msg = await ctx.send(embed=embed)
                options = await embed.add_options(msg, True)
            else: await embed.edit(msg)
            try: selection, action_type = await supreme_listener(ctx, *options, listen_for_add=True, listen_for_remove=True, add_cancel=True)
            except asyncio.TimeoutError:
                break
            if first_run: first_run = False
            if selection == -2:
                break
            embed.clear_fields()
            if bool('divine' in item):
                if selection == 0: buffs = action_type
                if selection == 1: divine = action_type
            else: buffs = action_type
        await embed.set_footer().edit(msg)
        await msg.clear_reactions()

    @commands.command(aliases=['bi'], brief='WIP command')
    async def browseitems(self, ctx, *args):
        args = list(args)
        # flags = [args.pop(args.index(flag)) for flag in {'-reverse'} if flag in args]
        # reverse = bool('-reverse' in flags)
        try:
            specs, ignored_args = self.ressolve_args(args)
        except Exception as error:
            await ctx.send(error)
            return
        valid_specs = {}
        search_keys = ['type', 'element', 'tier']
        for key, value in specs.items():
            result = search_for(key, search_keys)
            if not result or len(result) > 1:
                await ctx.send(f'Argument must match exactly one data type; "{key}" matched {result or "nothing"}')
                return
            key = result[0]
            spec = [item_type, element_colors, item_tiers][search_keys.index(key)]

            values = search_for(value, spec)
            if not values or len(values) > 1:
                val = bool(values)
                await ctx.send(f'Value "{value}" for parameter "{key}" has {("no", "too many")[val]} matches{("", ": ")[val]}{", ".join(values).lower()}')
                return
            valid_specs.update({key: values[0]})
        if not valid_specs:
            await ctx.send('No valid arguments were given.')
            return
        items = []
        for item in items_list:
            matching_specs = set()
            for key, value in valid_specs.items():
                if key == 'tier':
                    _min, _max = item['transform_range'].split('-')
                    _range = item_tiers[item_tiers.index(_min):item_tiers.index(_max) + 1]
                    matching_specs.add(value in _range and not _range.index(value))
                    continue
                matching_specs.add(item[key] == value)
            if all(matching_specs): items.append(item)

        def sort_by_tier_elem_name(item):
            return (
                list(reversed(item_tiers)).index(item['transform_range'].split('-')[0]),
                list(element_colors.keys()).index(item['element']),
                # list(item_type.keys()).index(item['type']),
                item['name'])

        items.sort(key=sort_by_tier_elem_name)

        item_names = [self.emoji_for_browseitems(item, valid_specs) + ' ' + item['name'] for item in items]
        fields = split_to_fields(item_names, '\n', field_limit=1024)

        color = element_colors[valid_specs['element']] if 'element' in valid_specs else discord.Color.from_rgb(*random_color())

        embed = discord.Embed(title=f'Matching items ({len(items)})', description='\n'.join(spec.capitalize().replace('_', ' ') + ': ' + self.specs(items[0])[spec] for spec in valid_specs), color=color)

        embed.set_author(name=f'Requested by {ctx.author.display_name}', icon_url=ctx.author.avatar_url)

        for field in fields:
            embed.add_field(name='<:none:772958360240128060>', value='\n'.join(field), inline=True)
            if len(embed) > 6000:
                x = sum(len(field) for field in fields[fields.index(field):])
                embed.set_field_at(index=-1, name='<:none:772958360240128060>', value=f'...and {x} more', inline=False)
                break

        embed.set_footer(text=f'Character count: {len(embed) + 17}')
        await ctx.send(embed=embed)

    @commands.command(hidden=True, aliases=['MB'], brief='WIP command')
    @perms(3)
    async def mechbuilder(self, ctx, *args):
        title = 'Mech builder' #'      '
        icon = slot_emojis
        none, mods = icon['none'], icon['modl']*2
        line0 = 'Addresing items: `Weapon[n]:` `[name]`, `Module[n]:` `[name]`, `Torso:` `[name]` etc'
        line1 = '\n' + f"`1` – {icon['topl']}{icon['dron']}{icon['topr']} – `2`{none}`1` – {mods} – `5`"
        line2 = '\n' + f"`3` – {icon['sidl']}{icon['tors']}{icon['sidr']} – `4`{none}`2` – {mods} – `6`"
        line3 = '\n' + f"`5` – {icon['sidl']}{icon['legs']}{icon['sidr']} – `6`{none}`3` – {mods} – `7`"
        line4 = '\n' + f"`C` – {icon['chrg']}{icon['tele']}{icon['hook']} – `H`{none}`4` – {mods} – `8`"
        desc = line0 + line1 + line2 + line3 + line4
        embed = discord.Embed(title=title, description=desc)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(SuperMechs(bot))
    print('SM loaded')
