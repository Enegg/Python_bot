import discord
from discord.ext import commands
import asyncio
from matrices import Matrix
from functions import RPN

class Math(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def print_matrix(self, state):
        """
        Returns a stringified matrix.
        """
        cont = state.content[1:]
        ctx = state.ctx
        cache = state.cache
        if not cont:
            raise ValueError('Incorrect syntax.')
        if cont[0] not in cache:
            raise ValueError(f'Did not find any matrix named "{cont[0]}".')
        if state.delmsg:
            await state.msg.delete()
        matrix = cache[cont[0]]
        str_matrix = '```' + f'({matrix.wy}x{matrix.wx})' + '\n' + str(matrix) + '```'
        if len(str_matrix) > 2000:
            str_matrix = 'Matrix is too big to display :('
        await ctx.send(str_matrix)

    async def create_new(self, state):
        """
        Creates a new matrix and adds it to the internal cache.
        """
        content = state.content
        embed = state.embed
        cache = state.cache
        bot_msg = state.bot_msg
        if len(content) < 3 or 'x' not in content[2] or len(content[1]) != 1:
            print(len(content) < 3, 'x' not in content[2], len(content[1]) != 1)
            raise ValueError('Incorrect input format.')
        try:
            size = tuple(int(x) for x in content[2].split('x'))
            values = [int(n) for n in content[3:]]
        except ValueError:
            raise ValueError('Incorrect input format.')
        if values and len(values) != size[0] * size[1]:
            raise ValueError('Incorrect amount of values for the matrix.')

        cache[content[1]] = Matrix(*size, values) if values else Matrix(*size)
        matrices_cont = ', '.join(f'{M}({cache[M].wy}x{cache[M].wx})' for M in cache)
        data = {'index': 0, 'name': 'Matrices', 'value': f'{matrices_cont}', 'inline': False}
        str_matrix = f'```{str(cache[content[1]])}```'
        if len(str_matrix) > 2000:
            str_matrix = 'Too big to display'
        recent_matrix = {'index': -1, 'name': 'Last matrix:', 'value': str_matrix, 'inline': False}
        if state.delmsg:
            await state.msg.delete()
        if embed.fields[0].name != data['name']:
            embed.insert_field_at(**data)
        else:
            embed.set_field_at(**data)
        embed.set_field_at(**recent_matrix)
        await bot_msg.edit(embed=embed)

    async def parse(self, state):
        await state.ctx.send('What')

    @commands.command(aliases=['matrix'])
    async def create_matrix(self, ctx):
        embed = discord.Embed(title='Matrix manipulation')
        embed.add_field(name='Starting', value='To begin, create a matrix\n```"new" (A-Z) YxX elements...```')
        embed.set_footer(text='Type "exit" to exit')
        bot_msg = await ctx.send(embed=embed)
        exiting = False
        matrices = {}
        class state:
            pass
        state.delmsg = False
        while True:
            try:
                msg = await ctx.bot.wait_for('message', timeout=120.0, check=lambda m: m.channel == ctx.channel and m.author == ctx.author)
            except asyncio.TimeoutError:
                await bot_msg.edit(embed=embed.set_footer(text='Session has expired'))
                break
            content = msg.content.split(' ')
            if exiting:
                if content and content[0].lower() == 'yes':
                    await bot_msg.edit(embed=embed.set_footer(text='Session has expired'))
                    break
                else:
                    exiting = False
                    embed.remove_field(-1)
                    await bot_msg.edit(embed=embed)
                    continue
            if (exiting := ('exit' in content)):
                embed.add_field(name='Do you wish to exit?', value='[yes/no]', inline=False)
                await bot_msg.edit(embed=embed)
                continue
            print(content)
            if 'delmsg' in content:
                if len(content) < 2 or content[1].lower() not in {'true', 'false'}:
                    await ctx.send('You need to specify value which is either true or false.', delete_after=5.0)
                state.delmsg = content[1].lower() == 'true'
                await msg.add_reaction('✅')
                continue


            # handling various commands
            state.msg = msg
            state.bot_msg = bot_msg
            state.embed = embed
            state.content = content
            state.cache = matrices
            state.ctx = ctx
            commands_dict = {'new': self.create_new, 'print': self.print_matrix}
            if (cmd := content[0].lower()) in commands_dict:
                command = commands_dict[cmd]
            else:
                command = self.parse
            try:
                await command(state)
            except ValueError as error:
                await ctx.send(error, delete_after=5.0)
                continue

        pass

    @commands.command(aliases=['rpn', 'onp', 'ONP'])
    async def RPN(self, ctx, *args):
        args = ''.join(args).replace('`', '')
        result = RPN(args)
        await ctx.send('`' + ' '.join(result) + '`')

def setup(bot):
    bot.add_cog(Math(bot))
    print('Math loaded')
