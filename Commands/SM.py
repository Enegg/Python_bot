from discord.ext import commands
import discord
import asyncio
from functions import search_for, intify, perms, supreme_listener, random_color
import json
import re
import urllib
from Commands.Testing import EmbedUI

with open("items.json") as file:
    items_list = json.loads(file.read())

operation_lookup = {
    'mult': ['eneCap', 'heaCap', 'eneReg', 'heaCap', 'heaCol', 'phyDmg', 'expDmg', 'eleDmg', 'heaDmg', 'eneDmg'],
    'mult+': ['phyRes', 'expRes', 'eleRes'],
    'reduce': ['backfire']}
common_item_data = {'type', 'element', 'tier'}
item_type_to_slot = {
    'TOP_WEAPON': 'topr',
    'SIDE_WEAPON': 'sidr',
    'TORSO': 'tors',
    'LEGS': 'legs',
    'DRONE': 'dron',
    'CHARGE': 'chrg',
    'TELEPORTER': 'tele',
    'HOOK': 'hook',
    'MODULE': 'modl'}

class SuperMechs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.WU_DB = {
            'type': {
                'TOP_WEAPON': 'https://i.imgur.com/LW7ZCGZ.png',
                'SIDE_WEAPON': 'https://i.imgur.com/CBbvOnQ.png',
                'TORSO': 'https://i.imgur.com/iNtSziV.png',
                'LEGS': 'https://i.imgur.com/6NBLOhU.png',
                'DRONE': 'https://i.imgur.com/oqQmXTF.png',
                'CHARGE': 'https://i.imgur.com/UnDqJx8.png',
                'TELEPORTER': 'https://i.imgur.com/Fnq035A.png',
                'HOOK': 'https://i.imgur.com/8oAoPcJ.png',
                'MODULE': 'https://i.imgur.com/dQR8UgN.png'},
            'trans_colors': ['⚪', '🔵', '🟣', '🟠', '🟤', '⚪'],
            'tiers': ['COMMON', 'RARE', 'EPIC', 'LEGENDARY', 'MYTHICAL', 'DIVINE'],
            'colors': {'EXPLOSIVE': 0xb71010, 'ELECTRIC': 0x106ed8, 'PHYSICAL': 0xffb800, 'COMBINED': 0x211d1d},
            'slots': {
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
                'none': '<:none:742507182918074458>'},
            'WUabbrev': {
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
                'eneCost': ['Energy cost', '<:eneusage:725871660237979759>']}}
        self.abbrevs = None
        self.names = None
        self.image_url_cache = {}
        self.url_template = 'https://raw.githubusercontent.com/ctrl-raul/workshop-unlimited/master/public/assets/items/{}.png'
        self.item_element = {'PHYSICAL': self.WU_DB['WUabbrev']['phyDmg'][1], 'EXPLOSIVE': self.WU_DB['WUabbrev']['expDmg'][1], 'ELECTRIC': self.WU_DB['WUabbrev']['eleDmg'][1], 'COMBINED': '🔰'}

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

    def get_image(self, item: object) -> str:
        slot_images = self.WU_DB['type']

        safe_name = item['name'].replace(' ', '')
        url = self.url_template.format(safe_name)

        if not item['id'] in self.image_url_cache:
            try:
                urllib.request.urlopen(url)
            except urllib.error.HTTPError:
                self.image_url_cache[item['id']] = slot_images[item['type']]
            else: self.image_url_cache[item['id']] = url
        return self.image_url_cache[item['id']]

    def ressolve_args(self, args: tuple):
        '''Takes command arguments as an input and tries to match them as key item pairs'''
        args = [a.lower() for a in args]
        specs = {}  # dict of data type: desired data, like 'element': 'explosive'
        ingored_args = set()
        for arg in args:
            print(arg)
            if ':' not in arg:
                ingored_args.add(arg)
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

    def specs(self, item: object):
        return {'type': self.WU_DB['slots'][item_type_to_slot[item['type']]], 'element': self.item_element[item['element']], 'transform_range': self.WU_DB['trans_colors'][self.WU_DB['tiers'].index(item['transform_range'].split('-')[0])]}

    def emoji_for_browseitems(self, item: object, spec_filter: dict):
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
        if self.abbrevs is None or self.names is None: self.abbreviator()
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
                    filler = ''.join(map(lambda n: ', **{}** for **{}**'.format(n + 1, matches[n]), range(1, number - 1))) if number > 2 else ''
                    botmsg = await ctx.send(f'Found {number} items!\nType **1** for **{first_item}**{filler} or **{number}** for **{final_item}**')
                    try: reply = await ctx.bot.wait_for('message', timeout=20.0, check=lambda m: m.author == msg.author and m.channel == ctx.channel and m.content.isdigit())
                    except asyncio.TimeoutError:
                        await botmsg.add_reaction('⏰')
                        return
                    choice = intify(reply.content) - 1
                    if choice in range(0, number): name = matches[choice]
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
        embed = EmbedUI(ctx, emojis, title=item['name'], description=' '.join([item['element'].lower().capitalize(), item['type'].replace('_', ' ').lower()]), color=self.WU_DB['colors'][item['element']])
        img_url = self.get_image(item)
        has_image = bool('imgur' not in img_url) #yeah I know, hack
        embed.set_image(url=img_url)
        if has_image: embed.set_thumbnail(url=self.WU_DB['type'][item['type']])
        embed.set_author(name=f'Requested by {ctx.author.display_name}', icon_url=ctx.author.avatar_url)
        embed.set_footer(text='React with B for arena buffs or D for divine stats (if applicable)')
        self.WU_DB['WUabbrev']['uses'][0] = ('Use' if 'uses' in item['stats'] and item['stats']['uses'] == 1 else 'Uses')
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

                item_stats += f"{self.WU_DB['WUabbrev'][stat][1]} **{value}** {self.WU_DB['WUabbrev'][stat][0]}\n"
            if 'advance' in item['stats'] or 'retreat' in item['stats']: item_stats += f"{self.WU_DB['WUabbrev']['jump'][1]} **Jumping required**"
            #transform range
            if (maximal := self.WU_DB['tiers'].index(_max)) < 4: tier = maximal
            elif divine: tier = 5
            else: tier = 4
            colors = self.WU_DB['trans_colors'].copy()
            colors.insert(tier, f'({colors.pop(tier)})')
            fields = []
            note = ' (buffs applied)' if buffs else ''
            fields.append({'name': 'Transform range: ', 'value': f"{''.join(colors[self.WU_DB['tiers'].index(_min):self.WU_DB['tiers'].index(_max) + 1])}", 'inline': False})
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
        flags = [args.pop(args.index(flag)) for flag in {'-reverse'} if flag in args]
        reverse = bool('-reverse' in flags)
        try:
            specs, ingored_args = self.ressolve_args(args)
        except Exception as error:
            await ctx.send(error)
            return
        valid_specs = {}
        for key, value in specs.items():
            result = search_for(key, common_item_data)
            if not result or len(result) > 1:
                await ctx.send(f'Argument must match exactly one data type; "{key}" matched {result or "nothing"}')
                return
            key = result[0]
            keyname = key
            if key == 'tier':
                keyname = 'tiers'
                key = 'transform_range'
            if key == 'element':
                keyname = 'colors'
            values = search_for(value, self.WU_DB[keyname])
            if not values or len(values) > 1:
                await ctx.send(f'Key "{key}" got no or more than 1 value: {values}')
                return
            valid_specs.update({key: values[0]})
        if not valid_specs:
            await ctx.send('No valid arguments were given.')
            return
        items = [item for item in items_list if all((bool(item[key] != value) if reverse else bool(item[key] == value)) for key, value in valid_specs.items())]
        print(len(items))
        text = '\n'.join(self.emoji_for_browseitems(item, valid_specs) + ' ' + item['name'] for item in items)

        color = self.WU_DB['colors'][valid_specs['element']] if 'element' in valid_specs else discord.Color.from_rgb(*random_color())

        embed = discord.Embed(title=f'Matching items ({len(items)}):', description=text, color=color).set_author(name=f'Requested by {ctx.author.display_name}', icon_url=ctx.author.avatar_url)
        new_specs = self.specs(items[0])
        embed.add_field(name=f'Match criteria{" (inverted)" if reverse else ""}:', value='\n'.join(spec.capitalize().replace('_', ' ') + ': ' + new_specs[spec] for spec in valid_specs), inline=False)
        await ctx.send(embed=embed)


    @commands.command(hidden=True, aliases=['MB'], brief='WIP command')
    @perms(3)
    async def mechbuilder(self, ctx, *args):
        title = 'Mech builder'
        slots = self.WU_DB['slots'] #'      '
        line0 = 'Addresing items: `Weapon[n]:` `[name]`, `Module[n]:` `[name]`, `Torso:` `[name]` etc'
        line1 = '\n`1` – {0}{1}{2} – `2`{4}`1` – {3}{3} – `5`'.format(slots['topl'], slots['dron'], slots['topr'], slots['modl'], slots['none'])
        line2 = '\n`3` – {0}{1}{2} – `4`{4}`2` – {3}{3} – `6`'.format(slots['sidl'], slots['tors'], slots['sidr'], slots['modl'], slots['none'])
        line3 = '\n`5` – {0}{1}{2} – `6`{4}`3` – {3}{3} – `7`'.format(slots['sidl'], slots['legs'], slots['sidr'], slots['modl'], slots['none'])
        line4 = '\n`C` – {0}{1}{2} – `H`{4}`4` – {3}{3} – `8`'.format(slots['chrg'], slots['tele'], slots['hook'], slots['modl'], slots['none'])
        # chars = max(len(line1), len(line2), len(line3), len(line4))
        # print(chars)
        # line1 = line1.center(chars, ' ')
        # line2 = line2.center(chars, ' ')
        # line3 = line3.center(chars, ' ')
        # line4 = line4.center(chars, ' ')
        desc = line0 + line1 + line2 + line3 + line4
        embed = discord.Embed(title=title, description=desc)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(SuperMechs(bot))
    print('SM loaded')
