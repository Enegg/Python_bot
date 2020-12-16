import asyncio
import operator as op
import math
import random
import re

from matrices import Matrix

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
    return tuple(round(random.random() * 255) for n in range(3))

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

def matheval(exp: str, variables: dict = None) -> float:
    """Evaluates a math expression."""
    if (a := exp.count('(')) != (b := exp.count(')')):
        raise ValueError(f'Unbalanced braces ({a} right, {b} left)')
    exp = exp.replace(' ', '').replace('**', '^')
    match = re.split(r'((?<=[^(Ee+-,])[+-]|\/{1,2}|[,*^@%()])', exp) # splitting at operators: 1+2 => ['1', '+', '2']
    while '' in match: match.remove('')
    # powers = ('⁰', '¹', '²', '³', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹')
    values, ops_stack, call, call_stack, func_stack, var = [], [], [], [], [], ''

    ops = {
        ',': (0,),
        '+': (1, op.add),
        '-': (1, op.sub),
        '*': (2, op.mul),
        '/': (2, op.truediv),
        '%': (2, op.mod),
        '@': (2, op.matmul),
        '//': (2, op.floordiv),
        '^': (3, op.pow)}

    functions = {i: getattr(math, i) for i in dir(math)[5:]}
    functions.update({'int': int,
        'float': float, 'bool': bool,
        'complex': complex, 'sum': sum,
        'round': round, 'ord': ord,
        'abs': abs, 'min': min, 'max': max,
        'pow': pow, 'mat': Matrix,
        'random': random.random,
        'randint': random.randint})

    constants = {
        'pi': math.pi, 'π': math.pi,
        'tau': math.tau, 'τ': math.tau,
        'e': math.e, 'inf': math.inf,
        '∞': math.inf, 'nan': math.nan}

    def val_or_call() -> list:
        """returns call if func_stack is not empty, else values"""
        if func_stack: return call
        return values

    def call_operator(op: str):
        if op == ',': return
        cont = val_or_call()
        cont.append(ops[op][1](cont.pop(-2), cont.pop()))

    def return_attr(attr_chain: str, fn: bool, base_obj: object=None) -> float:
        """
        Takes in a str of object names and attempts to retrieve the value of highest object,
        returns None if fails
        """
        if base_obj is None:
            base_obj = (call if fn else values).pop()
        if isinstance(attr_chain, list):
            attributes = attr_chain
        else:
            attributes = attr_chain.split('.')
        if attributes[0] == '': attributes.remove('')
        if not hasattr(base_obj, attributes[0]):
            raise AttributeError(f'{base_obj} does not have attribute {attributes[0]}')
        attr = getattr(base_obj, attributes.pop(0))
        for chained_attr in attributes:
            if not hasattr(attr, chained_attr):
                raise AttributeError(f'{attr} does not have attribute {chained_attr}')
            attr = getattr(attr, chained_attr)
        return attr

    def get_var(var: str) -> float:
        """Searches and returns a variable, raises ValueError if fails to do so"""
        negative = var.startswith('-')
        var = var.lstrip('-')
        if var in constants:
            return -constants[var] if negative else constants[var]
        if variables is None:
            raise ValueError(f'No variable named {var} found')
        try: return -variables[var] if negative else variables[var]
        except KeyError:
            raise ValueError(f'No variable named {var} found')

    def ressolve_attr(var: str, fn: bool) -> float:
        if var.startswith('.'):
            return return_attr(var, fn)
        var, *attrs = var.split('.')
        const = get_var(var)
        if attrs:
            const = return_attr(attrs, fn, const)
        return const

    for i in match:
        if re.sub(r'^(-?\.|-)', '', i)[:1].isnumeric():
            if i[-1] in {'i', 'j'}: num = complex(i.replace('i', 'j'))
            elif '.' in i or 'e' in i.lower(): num = float(i)
            else: num = int(i)
            (call if bool(func_stack) else values).append(num)
            continue
        if i.replace('-', '').replace('.', '').isalnum():
            var = i
            continue
        if var:
            fn = bool(func_stack)
            if i == '(': # namespace is a function or you fucked up
                try:
                    attr = ressolve_attr(var, fn)
                except Exception:
                    attr = False
                if fn: # if there are pending functions, that means the function is nested
                    call_stack.append(call) # so we put on stack the current args for function call and empty the list
                    call = []
                try:
                    func_stack.append(attr or functions[var])
                except KeyError:
                    raise NameError(f"name '{var}' preceeded a '(' while not being a function")
            else:
                const = ressolve_attr(var, fn)
                val_or_call().append(const)
            var = ''
        if i == '(':
            ops_stack.append(i)
            continue
        if i == ')':
            while ops_stack and ops_stack[-1] != '(':
                call_operator(ops_stack.pop())
            ops_stack.pop() # removes the ")"
            if func_stack:
                result = func_stack.pop()(*call)
                call = call_stack.pop() if func_stack else []
                val_or_call().append(result)
            continue
        if i in ops:
            while ops_stack and ops_stack[-1] in ops and ops[i][0] <= ops[ops_stack[-1]][0]:
                call_operator(ops_stack.pop())
            ops_stack.append(i)

    if var:
        const = ressolve_attr(var, False)
        values.append(const)

    while ops_stack:
        call_operator(ops_stack.pop())

    return values[0]

def esc_join(s: str='\n') -> str.join:
    """Function to escape joining strings with newline in f-string"""
    return s.join