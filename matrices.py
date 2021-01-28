from __future__ import annotations


import random
from numbers import Number
from decimal import Decimal
from typing import Iterable, Callable
from math import floor, log10, ceil
from itertools import product, starmap as smap
from operator import mul


def flatten(sequence) -> ...:
    """Generator yielding items of a sequence and it's subsequences."""
    for element in sequence:
        if hasattr(element, '__iter__'):
            yield from flatten(element)
        else:
            yield element


def size(n: Number) -> int:
    """Returns an int representing the len of a number
    after casting to str and truncating unnecessary characters"""
    if isinstance(n, int):
        if neg := n < 0:
            n = -n
        return ceil(log10(n+1)) + neg or 1

    if isinstance(n, (float, Decimal, complex)):
        return len(f'{n:g}')

    # if isinstance(n, complex):
    #     return len(f'{n:g}')

    return len(str(n))


class Matrix:
    """Class implementing matrices and operations related to them.
    Available types:

    zero - matrix filled with 0's if no args provided

    following types require the matrix to be square, else raises ValueError

    diag - diagonal matrix, with no args provided defaults to identity matrix

    upper - triangle matrix filled with 0's below main diagonal

    lower - triangle matrix filled with 0's above main diagonal"""

    def __init__(self, wx: int, wy: int, *args: list[Number], type_='zero'):
        if not wx > 0 < wy:
            raise ValueError('Matrix size cannot be negative or zero')

        if type_ not in {'zero', 'diag', 'upper', 'lower'}:
            raise ValueError('Invalid type provided')

        self.wx, self.wy = wx, wy
        if type_ != 'zero' and not self.is_square():
            raise ValueError(f'matrix must be square for type <{type_}>')

        if not args:
            self._matrix = [[0] * self.wx for _ in range(self.wy)]
            if type_ == 'diag':
                for i in range(self.wx):
                    self._matrix[i][i] = 1
            return

        items = [*flatten(args)]
        for i in items:
            if not isinstance(i, Number):
                print(args)
                raise ValueError(f'Value "{i}" is not {Number}')

        triangle = (wx + 1) * wx // 2
        size = {'zero': len(self), 'diag': wx, 'upper': triangle, 'lower': triangle}[type_]

        item_count = len(items)
        if item_count < size: # filling in missing items
            items += [0] * (size - len(items))

        elif item_count > size:
            items = items[:size]


        if type_ == 'zero':
            self._matrix = [[*items[n*self.wx:(n+1)*self.wx]] for n in range(self.wy)]

        elif type_ in {'upper', 'lower'}:
            self._matrix = []
            isup = type_ == 'upper'
            i = 0
            for n in range(wx, 0, -1) if isup else range(1, wx+1):
                lst = ([0]*(wx-n) + items[i:i+n]) if isup else (items[i:i+n] + [0]*(wx-n)) # this makes the triangles
                self._matrix.append(lst)
                i += n
        else:
            self._matrix = [[0] * wx for _ in range(wx)] # diagonal matrix
            for i, v in enumerate(items[:wx]):
                self._matrix[i][i] = v


    def __len__(self) -> int:
        return self.wx * self.wy


    def __tuplecheck(self, key: tuple[int, int]):
        """Helper function for getitem and setitem"""
        if not isinstance(key, tuple):
            raise TypeError(f'{key} is not a valid format')
        if len(key) != 2:
            raise ValueError(f'expected 2, got {len(key)} indices')
        wx, wy = key
        if not (type(wx) is type(wy) is int):
            if type(wx) is slice or type(wy) is slice:
                raise NotImplementedError('Slices not implemented yet')
            raise TypeError(f'matrix indices must be integers, not {type(wx)}, {type(wy)}')
        if not (wx < self.wx >= -wx and wy < self.wy >= -wy):
            raise IndexError('matrix indices out of range')


    def __getitem__(self, key: tuple[int, int]) -> Number:
        self.__tuplecheck(key)
        wx, wy = key
        return self._matrix[wy][wx]


    def __setitem__(self, key: tuple[int, int], value: Number):
        self.__tuplecheck(key)
        if not isinstance(value, Number):
            raise ValueError(f'Value is not of type {Number}')
        wx, wy = key
        self._matrix[wy][wx] = value


    def __bool__(self) -> bool:
        return any(map(any, self._matrix))


    def __str__(self) -> str:
        mat = self._matrix
        if self.wy == 1:
            return str(mat[0])

        l = max(map(size, flatten(mat)))

        just = lambda i: f'{i:{l}g}'
        row1 = f"⎡ {' '.join(map(just, mat[0]))} ⎤\n"
        mid = (f"⎢ {' '.join(map(just, r))} ⎥\n" for r in mat[1:-1])
        rowN = f"⎣ {' '.join(map(just, mat[-1]))} ⎦"
        return row1 + ''.join(mid) + rowN


    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.wx}, {self.wy}, {self._matrix})'


    def set_row(self, row: int, iterable: Iterable) -> Matrix:
        if len(iterable) != self.wx:
            raise ValueError("iterable's length does not match matrix size")
        if not row < self.wy >= -row:
            raise IndexError('row index out of range')
        self._matrix[row] = list(iterable)
        return self


    def set_col(self, col: int, iterable: Iterable) -> Matrix:
        if len(iterable) != self.wy:
            raise ValueError("iterable's length does not match matrix size")
        if not col < self.wx >= -col:
            raise IndexError('column index out of range')
        for n in range(self.wy):
            self._matrix[n][col] = iterable[n]
        return self


    def get_row(self, row: int) -> list:
        if not row < self.wy >= -row:
            raise IndexError('row index out of range')
        return self._matrix[row]


    def get_col(self, col: int) -> list:
        if not col < self.wx >= -col:
            raise IndexError('column index out of range')
        return [self._matrix[n][col] for n in range(self.wy)]


    def __add__(self, other: Matrix) -> Matrix:
        if not isinstance(other, Matrix):
            return NotImplemented
        if self.wx != other.wx or self.wy != other.wy:
            raise ValueError(f'Matrices are of different size ({self.wx}x{self.wy} vs {other.wx}x{other.wy})')

        return Matrix(self.wx, self.wy, (sum(x) for a in zip(self._matrix, other._matrix) for x in zip(*a)))


    def __sub__(self, other: Matrix) -> Matrix:
        if not isinstance(other, Matrix):
            return NotImplemented
        if self.wx != other.wx or self.wy != other.wy:
            raise ValueError(f'Matrices are of different size ({self.wx}x{self.wy} vs {other.wx}x{other.wy})')

        return Matrix(self.wx, self.wy, (b-c for a in zip(self._matrix, other._matrix) for b, c in zip(*a)))


    def __mul__(self, other: Number) -> Matrix:
        if not isinstance(other, Number):
            return NotImplemented
        return Matrix(self.wx, self.wy, map(lambda n: n * other, flatten(self._matrix)))


    def __matmul__(self, other: Matrix) -> Matrix:
        if not isinstance(other, Matrix):
            return NotImplemented
        if self.wx != other.wy:
            raise ValueError(f"Matrix A's X size of {self.wx} does not match matrix B's Y size of {other.wy}")
        return Matrix(other.wx, self.wy, (sum(smap(mul, a)) for a in smap(zip, product(self._matrix, zip(*other._matrix)))))


    def __pow__(self, num: int) -> Matrix:
        if floor(num) != num:
            return NotImplemented
        if not self.is_square():
            raise ValueError(f'Matrix is not square ({self.wy}x{self.wx})')
        if num == 1:
            return Matrix(self.wx, self.wy, self._matrix)
        if num == 0:
            return Matrix(self.wx, self.wy, type_='diag')
        if num < 0:
            raise ValueError('Inverse matrix not implemented yet')
        return self @ self ** (num - 1)


    def __iter__(self):
        for row in self._matrix:
            yield from row


    def T(self) -> Matrix:
        return Matrix(self.wy, self.wx, zip(*self._matrix))


    def shape(self) -> tuple:
        """Returns the dimensions of the matrix"""
        return self.wx, self.wy


    def is_square(self) -> bool:
        """Return True if the matrix is square, False otherwise"""
        return self.wx == self.wy


    def filter(self, predicate: Callable):
        """Takes in a function that accepts matrix' item as a sole argument
        and which returns a bool. Items for which it returns False are set to 0."""
        for i, row in enumerate(self._matrix):
            self._matrix[i] = list(smap(mul, zip(row, map(predicate, row))))

        return self


    def apply(self, callable: Callable, value: Number=None):
        """Passes values from matrix to callable and saves back the results.
        If value is passed, callable should accept two arguments and will be called
        with values from matrix + the passed value."""
        if value is not None:
            callable = lambda x: callable(x, value)

        for row in self._matrix:
            for i, item in enumerate(row):
                row[i] = callable(item)

        return self


#--------------------------------- Testing Zone ---------------------------------

if __name__ == '__main__':
    e = [random.random() for n in range(64)]
    f = [random.randint(0, 9) for n in range(64)]

    A = Matrix(3, 1, [1, 2, 3])
    B = Matrix(3, 3, [1, 2, 3], [4, 5, 6], [7, 8, 9])

    C = Matrix(5, 1, [1, 2, 3, 4, 5])
    D = Matrix(1, 5, [5, 4, 3, 2, 1])

    z: complex = 1-1j
    zz = 2j
    E = Matrix(3, 3, z, z, zz, z, z, z, zz, z, z)

    I = Matrix(8, 8, e)
    J = Matrix(8, 8, f)

    h = input('Enter P to print ').lower() == 'p'
    while True:
        if h:
            print(eval(input()))
        else:
            eval(input())
