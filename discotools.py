from discord.ext import commands
import discord
import asyncio

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

async def supreme_listener(ctx, msg, emojis: list, on_add=True, on_remove=False, add_return=False, add_cancel=False) -> int:
    '''Returns the position of added/removed reaction'''
    if not emojis:
        raise ValueError('No emojis to check with')
    #return emoji is a reserved emoji for going back
    if add_return: emojis.append('↩️')
    #cross emoji is reserved for closing the menu
    if add_cancel: emojis.append('❌')
    check = lambda reaction, user: user == ctx.author and str(reaction.emoji) in emojis
    tasks = []
    specifiers = set()

    if on_add:
        specifiers.add('reaction_add')
    if on_remove:
        specifiers.add('reaction_remove')

    if not specifiers:
        raise ValueError('No events to listen to specified.')

    # for listener in specifiers:
    #     wait_for = ctx.bot.wait_for(listener, check=check)
    #     task = asyncio.create_task(wait_for)
    #     tasks.append(task)

    if on_add:
        print('on add')
        wait_for_add = ctx.bot.wait_for('reaction_add', check=check)
        task_add = asyncio.create_task(wait_for_add)
        tasks.append(task_add)
    else: task_add = None

    if on_remove:
        print('on remove')
        wait_for_del = ctx.bot.wait_for('reaction_remove', check=check)
        task_del = asyncio.create_task(wait_for_del)
        tasks.append(task_del)
    else: task_del = None

    done, pending = await asyncio.wait(tasks, timeout=20.0, return_when='FIRST_COMPLETED')
    if not done:
        raise asyncio.TimeoutError
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
        main_limit, extra_limit = tuple(field_limit)
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

class EmbedUI(discord.Embed):
    '''Preset for an embed creating a choice menu'''

    numbers = ('0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟')

    def __init__(self, ctx, emojis=[], **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx
        self.emojis = emojis or self.numbers
        self.count = 0

    def add_choice_field(self, name, values: list):
        """Transform a list of values into a choice menu"""
        if not bool(values):
            return self
        list_of_items = [[value, self.emojis[values.index(value)]] for value in values[:len(self.emojis)]]
        cont = '\n'.join(f'{x[1]} {x[0]}' for x in list_of_items)
        self.add_field(name=name, value=cont, inline=False)
        self.count += len(values)
        return self

    def set_count(self, count):
        self.count = count
        return self

    async def add_options(self, msg, add_cancel=False):
        """Reacts to a message with emojis as options"""
        if not bool(count := self.count): raise ValueError('No emojis to add')
        len_emojis = len(self.emojis)
        number = count if count < len_emojis else len_emojis
        #adding reactions
        for x in (new_emojis := self.emojis[:number]):
            await msg.add_reaction(x)
        if add_cancel: await msg.add_reaction('❌')
        return msg, new_emojis

    async def edit(self, msg, add_return=False):
        """Edits the message"""
        await msg.edit(embed=self)
        if add_return:
            await msg.add_reaction('↩️')
        return self
