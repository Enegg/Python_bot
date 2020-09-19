from discord.ext import commands
import asyncio
import random
import re

def perms(lvl: int):
    '''Defines required user's lvl to access a command, following: 1 - manage messages, 2 - manage guild, 3 - admin, 4 - guild owner, 5 - bot author'''
    def extended_check(ctx) -> bool:
        if ctx.author.id == 190505392504045570:
            return True
        if ctx.guild is None:
            return False
        if int(lvl) <= 4 and ctx.guild.owner_id == ctx.author.id:
            return True
        permKeys = ['manage_messages', 'manage_guild', 'administrator']
        if int(lvl) <= len(permKeys):
            key = permKeys[int(lvl) - 1]
            return getattr(ctx.author.guild_permissions, key)
        return False
    return commands.check(extended_check)

def intify(s, default=0) -> int:
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

def random_color(seed=None) -> tuple:
    r'''Returns a RGB color tuple, can be based off a seed'''
    if seed is not None: random.seed(intify(seed))
    return tuple(round(random.random() * 255) for n in range(0, 3))

def helpie(x): return [x, type(x)]

def common_items(lists: list) -> list:
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

def search_for(phrase: str, iterable) -> list:
    r'''Helper func capable of finding a specific string following a name rule, like "_burn_" in "Half Burnt Scope"'''
    if not iterable: return iterable
    phrase = r'\b' + re.sub('[^a-z ]+', '', phrase).replace(' ', '.+ ')
    return [i for i in list(iterable) if re.search(phrase, i.lower())]

def roll(a=1, b=6): return random.randint(min(a, b), max(a, b))

async def supreme_listener(ctx, msg, emojis: list, listen_for_add=True, listen_for_remove=False, add_return=False, add_cancel=False) -> int:
    '''Returns the position of added/removed reaction'''
    if not bool(emojis): raise Exception('No emojis to check with')
    #return emoji is a reserved emoji for going back
    if add_return: emojis.append('↩️')
    #cross emoji is reserved for closing the menu
    if add_cancel: emojis.append('❌')
    check = lambda reaction, user: user == ctx.author and str(reaction.emoji) in emojis
    tasks = []

    if listen_for_add:
        wait_for_add = ctx.bot.wait_for('reaction_add', check=check)
        task_add = asyncio.create_task(wait_for_add)
        tasks.append(task_add)
    else: task_add = None

    if listen_for_remove:
        wait_for_del = ctx.bot.wait_for('reaction_remove', check=check)
        task_del = asyncio.create_task(wait_for_del)
        tasks.append(task_del)
    else: task_del = None

    if not tasks: raise Exception('There are no emoji add/remove events to listen for')

    done, pending = await asyncio.wait(tasks, timeout=20.0, return_when='FIRST_COMPLETED')
    if not done: raise asyncio.TimeoutError
    [task.cancel() for task in pending]
    for task in done:
        reaction = (await task)[0]
        action_type = None
        if task == task_add: action_type = True
        if task == task_del: action_type = False

    if add_return and str(reaction.emoji) == '↩️': return -1, action_type
    if add_cancel and str(reaction.emoji) == '❌': return -2, action_type
    return emojis.index(reaction.emoji), action_type

def set_default(embed, ctx):
    embed.set_author(name=f'Requested by {ctx.author.display_name}', icon_url=ctx.author.avatar_url)

def split_to_fields(all_items: list, splitter: str, field_limit=2048) -> list:
    '''Helper func designed to split a long list of items into discord embed fields so that they stay under character limit. field_limit should be an int or a tuple of two ints; in case of the latter the first int will be applied to the first field, and the second to any following field.'''
    if isinstance(field_limit, tuple):
        if len(field_limit) != 2:
            raise ValueError(f'Expected 2 integers, got {len(field_limit)} {field_limit}')
        main_limit, extra_limit = field_limit
    else: main_limit, extra_limit = int(field_limit), 0
    sliced_list = []
    
    all_items = list(all_items)

    while True:
        counter = 0
        if sliced_list and extra_limit: main_limit = extra_limit
        for i in all_items:
            if counter + len(i) > main_limit:
                index = all_items.index(i)
                sliced_list.append(all_items[:index])
                all_items = all_items[index:]
                break
            counter += len(i) + len(splitter)
        else:
            sliced_list.append(all_items)
            break
    return sliced_list
