import asyncio
from typing import Callable, Tuple

import discord
from discord.ext import commands

def perms(lvl: int):
    """\
    Defines required user's lvl to access a command, following:
    1 - manage messages, 2 - manage guild, 3 - admin, 4 - guild owner, 5 - bot author"""
    def extended_check(ctx) -> bool:
        if ctx.author.id == 190505392504045570:
            return True
        if ctx.guild is None:
            return False
        if lvl <= 4 and ctx.guild.owner_id == ctx.author.id:
            return True
        permKeys = ('manage_messages', 'manage_guild', 'administrator')
        if lvl <= len(permKeys):
            key = permKeys[lvl - 1]
            return getattr(ctx.author.permissions_in(ctx.channel), key, False)
        return False
    return commands.check(extended_check)


# async def supreme_listener(ctx, emojis: list, on_add=True, on_remove=False, add_return=False, add_cancel=False) -> int:
#     """Returns the position of added/removed reaction"""
#     if not emojis:
#         raise ValueError('No emojis to check with')
#     # return emoji is a reserved emoji for going back
#     if add_return: emojis.append('↩️')
#     # cross emoji is reserved for closing the menu
#     if add_cancel: emojis.append('❌')
#     check = lambda reaction, user: user.id == ctx.author.id and str(reaction.emoji) in emojis
#     tasks = []
#     specifiers = set()

#     if on_add:
#         specifiers.add('reaction_add')
#     if on_remove:
#         specifiers.add('reaction_remove')

#     if not specifiers:
#         raise ValueError('No events to listen to specified.')

#     for listener in specifiers:
#         wait_for = ctx.bot.wait_for(listener, check=check)
#         task = asyncio.create_task(wait_for, name=listener)
#         tasks.append(task)

#     done, pending = await asyncio.wait(tasks, timeout=20.0, return_when='FIRST_COMPLETED')
#     if not done:
#         raise asyncio.TimeoutError
#     [task.cancel() for task in pending]
#     # done is a set so we can't index it, but it *should* contain only one item
#     if len(done) != 1: # something fucked up
#         print(done)
#         raise Exception('Something falied with tasks')
#     else:
#         task = done.pop()
#         reaction = (await task)[0]
#         action_type = None
#         if task.get_name() == 'reaction_add': action_type = True
#         if task.get_name() == 'reaction_remove': action_type = False

#     if add_return and str(reaction.emoji) == '↩️': return -1, action_type
#     if add_cancel and str(reaction.emoji) == '❌': return -2, action_type
#     return emojis.index(reaction.emoji), action_type


def set_default(embed: discord.Embed, ctx: discord.ext.commands.Context):
    """Sets embed author"""
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
    """Preset for an embed creating a choice menu

    By default, it holds these emojis:
    0️⃣1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣8️⃣9️⃣🔟
    """

    numbers = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    # numbers has to be a list

    def __init__(self, emojis: list=[], **kwargs):
        super().__init__(**kwargs)
        self.emojis = emojis or self.numbers
        self.count = 0


    def add_choice_field(self, name: str, values: list):
        """Transform a list of values into a choice menu"""
        if not values:
            return self
        items = [[value, self.emojis[values.index(value)]] for value in values[:len(self.emojis)]]
        cont = '\n'.join(f'{x[1]} {x[0]}' for x in items)
        self.add_field(name=name, value=cont, inline=False)
        self.count += len(values)
        return self

    def set_count(self, count):
        self.count = count
        return self


    async def add_options(self, msg, add_cancel=False):
        """Reacts to a message with emojis as options, returns a list of emojis"""
        if self.count == 0:
            raise ValueError('No emojis to add')
        emoji_count = len(self.emojis)
        number = self.count if self.count < emoji_count else emoji_count
        #adding reactions
        reactions = self.emojis[:number]
        if add_cancel:
            reactions.append('❌')
        for x in reactions:
            await msg.add_reaction(x)
        return reactions


    async def edit(self, msg, add_return=False):
        """Edits the message"""
        await msg.edit(embed=self)
        if add_return:
            await msg.add_reaction('↩️')
        return self


async def scheduler(ctx: commands.Context, events: set, check: Callable, timeout=None, return_when: str ='FIRST_COMPLETED') -> Tuple[tuple, str]:
    """Wrapper for asyncio.wait designed for discord events. Returns the outcome of the event and its name."""
    if not events:
        raise ValueError('No events to await')
    tasks = set()

    for event in events:
        wait_for = ctx.bot.wait_for(event, check=check)
        task = asyncio.create_task(wait_for, name=event)
        tasks.add(task)

    done, pending = await asyncio.wait(tasks, timeout=timeout, return_when=return_when)
    if not done:
        raise asyncio.TimeoutError

    for task in pending:
        task.cancel()

    for task in done:
        outcome = await task
        name = task.get_name()
        yield outcome, name
