"""Config file containing items like bot token, purge cap and prefix."""
#general vars
prefix_local = '-'
prefix_host = ','
authorid = 190505392504045570
security_lvl = {'say': 3, 'sd': 2, 'roles': 1, 'purge': 1}
#purge
purge_cap = 2000
purge_confirm_emote = '<:kamehameha:704775089044062278>'
#say
abbreviations = {'WU': 'Workshop Unlimited', 'M': 'Matrix', 'WB': 'W&BS', 'AC': 'Axis Convergence'}
#stats
WU_DB = {
    'trans_colors': ['⚪', '🔵', '🟣', '🟠', '🟤', '⚪'],
    'tiers': ['COMMON', 'RARE', 'EPIC', 'LEGENDARY', 'MYTHICAL', 'DIVINE'],
    'sprite_path': 'https://workshop-unlimited.web.app/img/items/',
    'colors': {'EXPLOSIVE': 0xb71010, 'ELECTRIC': 0x106ed8, 'PHYSICAL': 0xffb800},
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
        'uses': [None, '<:uses:725871917923303688>'],
        'backfire': ['Backfire', '<:backfire:725871901062201404>'],
        'heaCost': ['Heat cost', '<:heatgen:725871674007879740>'],
        'eneCost': ['Energy cost', '<:eneusage:725871660237979759>']},
    'item_dict': {
        #'recko': 'Reckoning',
        'abo': 'Abomination',
        'heron': 'HeronMark',
        'claw': 'The Claw',
        'zark': 'Zarkares'
        }
    }
