from discord.ext import commands
import random
import re

def perms(lvl: int):
    '''Defines user's access to a command, following: 1 - manage messages, 2 - manage guild, 3 - admin, 4 - guild owner, 5 - bot author'''
    def extended_check(ctx):
        if ctx.guild is None:
            return False
        if ctx.author.id == 190505392504045570:
            return True
        permKeys = ['manage_messages', 'manage_guild', 'administrator']
        if int(lvl) <= len(permKeys):
            key = permKeys[int(lvl) - 1]
            for role in ctx.author.roles:
                if getattr(role.permissions, key):
                    return True
            return False
        else:
            return lvl == 4 and ctx.guild.owner_id == ctx.author.id
    return commands.check(extended_check)

def intify(s, default=0):
    r'''int() which returns the dafault value for non ints'''
    s = str(s)
    if s.isdigit():
        return int(s)
    elif s[0] in '-+':
        if s[1:].isdigit():
            if s[0] == '-':
                return int(s)
            return int(s[1:])
    return default

def random_color(seed=None):
    r'''Returns a RGB color tuple, can be based off a seed'''
    if seed is not None: random.seed(intify(seed))
    return tuple(round(random.random() * 255) for n in range(0, 3))

def helpie(x): return [x, type(x)]

def common_items(lists: list):
    r'''Helper func which returns a list of common items found in the input lists'''
    if not bool(lists): return lists
    result, first_run = [], True
    while len(lists) >= 1:
        a = lists.pop() if first_run else result
        result, first_run = [], False
        if len(lists) > 0:
            b = lists.pop()
            if len(a) > len(b): a, b = b, a
            result = [x for x in a if x in b]
    return result

def search_for(phrase: str, iterable):
    r'''Helper func capable of finding a specific string following a name rule, like "_burn_" in "Half Burnt Scope"'''
    if not iterable: return iterable
    phrase = r'\b' + re.sub('[^a-z ]+', '', phrase).replace(' ', '.+ ')
    return [i for i in list(iterable) if re.search(phrase, i.lower())]

def roll(a=1, b=6): return random.randint(min(a, b), max(a, b))
