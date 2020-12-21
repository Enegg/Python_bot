import asyncio
import math

import discord
from discord.ext import commands

from matrices import Matrix
from functions import matheval, njoin

class Math(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.vars = {}


    @commands.command(
        aliases=['rpn', 'math', 'm'],
        usage='[optional: variable =] (expr)')
    async def RPN(self, ctx: commands.Context, *args):
        """Evaluates a mathematical expression"""
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

        result = str(result)
        newl = '\n' in result
        if newl:
            result = result.replace('\n', '`\n`')
        if var:
            spacer = (' ', '`\n`')[newl]
            result = f'{var} ={spacer}{result}'
        await ctx.send(f'`{result}`')


    @commands.command(aliases=['vars'])
    async def variables(self, ctx: commands.Context, *args):
        text = ''
        va: dict = self.vars
        if not args:
            if va:
                text = (
                '```fix\n'
                f"{njoin(f'{k}({v.wx}x{v.wy})' if isinstance(v, Matrix) else f'{k} = {v}' for k, v in va.items())}"
                '```')
            else:
                text = 'No variables stored.'

        elif args[0].lower() == 'clear':
            if not args[1:]:
                va.clear()
            else:
                [va.pop(arg) for arg in args[1:] if arg in va]
        else:
            text = va.get(str(args[0]), f'No variable named "{args[0]}" found.')
            if len(text) > 2000:
                text = 'Requested variable is too large to show'
        if text: await ctx.send(text)


def setup(bot):
    bot.add_cog(Math(bot))
    print('Math loaded')
