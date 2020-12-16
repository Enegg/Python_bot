import asyncio
import math, cmath

import discord
from discord.ext import commands

from matrices import Matrix
from functions import matheval

class Math(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.vars = {}

    @commands.command(
        aliases=['rpn', 'math'],
        brief='Evaluates a mathematical expression',
        usage='[optional: variable =] (expr)')
    async def RPN(self, ctx: commands.Context, *args):
        exp = ''.join(args).replace('`', '').replace(' ', '')
        if not exp:
            return

        var = ''
        eq = exp.find('=')
        if eq != -1:
            var = exp[:eq]
            exp = exp[eq+1:]

        try:
            result = matheval(exp, self.vars if self.vars else None)
        except Exception as error:
            result = str(error)
        else:
            self.vars.update({var if var else 'ans': result})

        if var:
            spacer = (' ', '\n')['\n' in str(result)]
            result = f'{var} ={spacer}{result}'
        await ctx.send(f'`{result}`')

    @commands.command(aliases=['vars'])
    async def variables(self, ctx: commands.Context, *args):
        text = ''
        v = self.vars
        if not args:
            if v:
                nl = '\n'
                text = (
                '```fix\n'
                f"{nl.join(f'{k}({v[k].wx}x{v[k].wy})' if isinstance(v[k], Matrix) else f'{k} = {v[k]}' for k in v)}"
                '```')
            else:
                text = 'No variables stored.'

        elif args[0].lower() == 'clear':
            if not args[1:]:
                v.clear()
            else:
                [v.pop(arg) for arg in args[1:] if arg in v]
        else:
            text = v.get(str(args[0]), f'No variable named "{args[0]}" found.')
            if len(text) > 2000:
                text = 'Requested variable is too large to show'
        if text: await ctx.send(text)

def setup(bot):
    bot.add_cog(Math(bot))
    print('Math loaded')
