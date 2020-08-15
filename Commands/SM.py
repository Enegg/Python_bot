from discord.ext import commands
import discord
import asyncio
from functions import search_for, intify, perms
import json
import re
items_list = json.loads(open("items.json").read())

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
            'sprite_path': 'https://workshop-unlimited.web.app/img/items/',
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
                'modl': '<:mod:730115649866694686>'},
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
        self.operation = {
            'mult': ['eneCap', 'heaCap', 'eneReg', 'heaCap', 'heaCol', 'phyDmg', 'expDmg', 'eleDmg', 'heaDmg', 'eneDmg'],
            'mult+': ['phyRes', 'expRes', 'eleRes'],
            'reduce': ['backfire']}
        self.abbrevs = None
        self.names = None

    def get_item_by_id_or_name(self, value: str):
        for item in items_list:
            if str(item['id']) == str(value) or item['name'].lower() == str(value).lower():
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

    @commands.command(brief='Show to a frantic user where is his place')
    async def frantic(self, ctx):
        await ctx.send('https://i.imgur.com/Bbbf4AH.mp4')

    def buff(self, stat, value, enabled, item):
        if not enabled:
            return value
        # if stat in self.operation['add'] and item['type'] == 'TORSO':
        #     return value + 350
        if stat in self.operation['mult']:
            return round(value * 1.2)
        if stat in self.operation['mult+']:
            return round(value * 1.4)
        if stat in self.operation['reduce']:
            return round(value * 0.8)
        return value

    @commands.command(usage='[item name] [optional: -b for arena buffs and/or -d for divine]',brief='Inspect an item\'s stats',help='To use the command, type in desired item\'s name or it\'s abbreviation, like "efa" for "energy free armor". Include a flag "-b" to enable arena buffs and "-d" to set the tier to divine (if applicable)')
    @commands.cooldown(2, 15.0, commands.BucketType.member)
    async def stats(self, ctx, *args):
        msg = ctx.message
        if not bool(args):
            await msg.add_reaction('❌')
            return
        args = list(args)
        #flags ['-d', '-b', '-r']
        flags = list(map(lambda e: args.pop(args.index(e)), filter(lambda i: i in args, ['-d', '-b', '-r'])))
        buffs = bool('-b' in flags)
        #solving for abbrevs
        name = ' '.join(args).lower()
        if intify(name) == 0 and len(name) < 2:
            await msg.add_reaction('❌')
            return

        #returning the exact item name from short user input
        if self.abbrevs is None or self.names is None: self.abbreviator()
        if name not in self.names:
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
            await msg.add_reaction('❌')
            return
        #test flag
        if '-r' in flags:
            await ctx.send(item)
            return
        #adding a note when -b flag is included
        divine = bool('-d' in flags) and bool('divine' in item)
        note = ' (buffs applied)' if buffs else ''
        #adding item stats
        item_stats = ''
        spaced = False
        self.WU_DB['WUabbrev']['uses'][0] = ('Use' if 'uses' in item['stats'] and item['stats']['uses'] == 1 else 'Uses')
        for k in item['stats']:
            if k in ['backfire', 'heaCost', 'eneCost'] and not spaced:
                item_stats += '\n'
                spaced = True
            #divine handler
            pool = 'divine' if divine and k in item['divine'] else 'stats'
            #number range handler
            if isinstance(item['stats'][k], list):
                if len(item['stats'][k]) == 1: value = self.buff(k, item[pool][k][0], buffs, item) #handling one spot range
                elif item[pool][k][1] == 0: value = item[pool][k][0]
                else: value = str(self.buff(k, item[pool][k][0], buffs, item)) + '-' + str(self.buff(k, item[pool][k][1], buffs, item))
            else: value = self.buff(k, item[pool][k], buffs, item)
            item_stats += f"{self.WU_DB['WUabbrev'][k][1]} **{value}** {self.WU_DB['WUabbrev'][k][0]}\n"
        if 'advance' in item['stats'] or 'retreat' in item['stats']: item_stats += f"{self.WU_DB['WUabbrev']['jump'][1]} **Jumping required**"
        #embedding
        embed = discord.Embed(title=item['name'], description=' '.join([item['element'].lower().capitalize(), item['type'].replace('_', ' ').lower()]), color=self.WU_DB['colors'][item['element']])
        fields = []
        #transform range
        min_, max_ = item['transform_range'].split('-')
        if (maximal := self.WU_DB['tiers'].index(max_)) < 4: selected = maximal
        elif divine: selected = 5
        else: selected = 4
        colors = self.WU_DB['trans_colors'].copy()
        colors.insert(selected, f'({colors.pop(selected)})')
        fields.append(['Transform range: ', f"{''.join(colors[self.WU_DB['tiers'].index(min_):self.WU_DB['tiers'].index(max_) + 1])}"])
        #the rest of the embed
        fields.append([f'Stats{note}:', item_stats])
        for field in fields: embed.add_field(name=field[0], value=field[1], inline=False)
        img_url = self.WU_DB['sprite_path'] + item['name'].replace(' ', '') + '.png'
        embed.set_image(url=img_url)
        embed.set_thumbnail(url=self.WU_DB['type'][item['type']])
        embed.set_author(name=f'Requested by {ctx.author}',icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(hidden=True,aliases=['MB'],brief='WIP command')
    @perms(3)
    async def mechbuilder(self, ctx, *args):
        title = 'Mech layout'
        slots = self.WU_DB['slots']
        line0 = 'Addresing items: `Weapon[n]:` `[name]`, `Module[n]:` `[name]`, `Torso:` `[name]` etc'
        line1 = '\n`1` – {0}{1}{2} – `2`      `1` – {3}{3} – `5`'.format(slots['topl'], slots['dron'], slots['topr'], slots['modl'])
        line2 = '\n`3` – {0}{1}{2} – `4`      `2` – {3}{3} – `6`'.format(slots['sidl'], slots['tors'], slots['sidr'], slots['modl'])
        line3 = '\n`5` – {0}{1}{2} – `6`      `3` – {3}{3} – `7`'.format(slots['sidl'], slots['legs'], slots['sidr'], slots['modl'])
        line4 = '\n`C` – {0}{1}{2} – `H`      `4` – {3}{3} – `8`'.format(slots['chrg'], slots['tele'], slots['hook'], slots['modl'])
        chars = max(len(line1), len(line2), len(line3), len(line4))
        print(chars)
        line1 = line1.center(chars, ' ')
        line2 = line2.center(chars, ' ')
        line3 = line3.center(chars, ' ')
        line4 = line4.center(chars, ' ')
        desc = line0 + line1 + line2 + line3 + line4
        embed = discord.Embed(title=title, description=desc)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(SuperMechs(bot))
    print('SM loaded')
