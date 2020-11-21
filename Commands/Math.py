import discord
from discord.ext import commands
import asyncio
from matrices import Matrix
from functions import matheval
import math, cmath

class Math(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.vars = {}

    async def create_new(self, state):
        """
        Creates a new matrix and adds it to the internal cache.
        """
        content = state.content
        embed = state.embed
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

        self.vars[content[1]] = Matrix(*size, values) if values else Matrix(*size)
        matrices_cont = ', '.join(f'{M}({self.vars[M].wy}x{self.vars[M].wx})' for M in self.vars)
        data = {'index': 0, 'name': 'Matrices', 'value': f'{matrices_cont}', 'inline': False}
        str_matrix = f'```{str(self.vars[content[1]])}```'
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
        cont = state.content
        try:
            res = matheval(cont)
            await state.ctx.send(f'`{res}`')
        except Exception as error:
            await state.ctx.send(error)

    @commands.command(aliases=['matrix'])
    async def create_matrix(self, ctx):
        embed = discord.Embed(title='Matrix manipulation')
        embed.add_field(name='Starting', value='To begin, create a matrix\n```"new" (A-Z) YxX elements...```')
        embed.set_footer(text='Type "exit" to exit')
        bot_msg = await ctx.send(embed=embed)
        exiting = False
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
            state.ctx = ctx
            commands_dict = {'new': self.create_new}
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

    @commands.command(aliases=['rpn', 'math'])
    async def RPN(self, ctx, *args):
        args = ''.join(args).replace('`', '').replace(' ', '')
        prefix = ''
        if '=' in args:
            prefix = args[:args.index('=')]
            args = args[args.index('=')+1:]
        try:
            result = matheval(args, self.vars if self.vars else None)
            self.vars.update({prefix if prefix else 'ans': result})
        except Exception as e:
            result = str(e)
        if prefix: result = '{} ={}'.format(prefix, '\n' if isinstance(result, Matrix) else ' ') + str(result)
        await ctx.send(f'`{result}`')

    @commands.command(aliases=['vars'])
    async def variables(self, ctx, *args):
        text = ''
        if not args:
            text = ('```py\n' + '\n'.join(f'{k}({self.vars[k].wx}x{self.vars[k].wy})' if isinstance(self.vars[k], Matrix) else f'{k} = {self.vars[k]}' for k in self.vars) + '```') if self.vars else 'No variables stored.'
        elif args[0].lower() == 'clear':
            if not args[1:]: self.vars.clear()
            else:
                [self.vars.pop(arg) for arg in args[1:] if arg in self.vars]
        else:
            text = self.vars.get(str(args[0]), f'No variable named "{args[0]}" found.')
            if len(text) > 2000:
                text = 'Requested variable is too large to show'
        if text: await ctx.send(text)

def setup(bot):
    bot.add_cog(Math(bot))
    print('Math loaded')
