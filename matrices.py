import random
from numbers import Number
from typing import List, Iterable
# cases:
# ([a, b, c, d], )
# ([[a, b], [c, d]], )
# ([a, b], [c, d])

class Matrix:
    """Class implementing matrices and operations related to them."""
    def __init__(self, wx: int, wy: int, *args: List[Number]):
        self.wx = int(wx).__abs__()
        self.wy = int(wy).__abs__() # this way it shows that self.wx is of type int, abs() does not
        if not args:
            self._matrix = [[0] * self.wx for n in range(self.wy)]
            return
        if len(args) == 1: args = args[0] # if args is a list or tuple
        if (lt := len(args)) == self.wy and isinstance(args[0], (tuple, list)):
            self._matrix = list(args)
        elif lt == len(self): # list is flattened
            self._matrix = [list(args[n * self.wx:(n + 1) * self.wx]) for n in range(self.wy)]
        else:
            print(args)
            raise Exception('Matrix not initialized properly')
        for a in self._matrix:
            for x in a:
                if not isinstance(x, Number):
                    print(args)
                    raise ValueError(f'Value "{x}" is not of {type(Number)}')

    def __len__(self) -> int:
        return self.wx * self.wy

    def __getitem__(self, key: tuple):
        if not isinstance(key, tuple):
            raise TypeError(f'{key} is not a valid format')
        if len(key) != 2:
            raise ValueError(f'expected 2, got {len(key)} indices')
        wx, wy = key
        if not (type(wx) is type(wy) is int):
            raise TypeError(f'matrix indices must be integers, not {type(wx)}, {type(wy)}')
        if wx > self.wx - 1 or wy > self.wy - 1 or -wx > self.wx or -wy > self.wy:
            raise IndexError('matrix indices out of range') # positive indexes
        return self._matrix[wy][wx]

    def __setitem__(self, key: tuple, value):
        if not isinstance(key, tuple):
            raise TypeError(f'{key} is not a valid format')
        if len(key) != 2:
            raise ValueError(f'expected 2, got {len(key)} indices')
        wx, wy = key
        if not (type(wx) is type(wy) is int):
            raise TypeError(f'matrix indices must be integers, not {type(wx)}, {type(wy)}')
        if wx > self.wx - 1 or wy > self.wy - 1 or -wx > self.wx or -wy > self.wy:
            raise IndexError('matrix indices out of range') # positive indexes
        self._matrix[wy][wx] = value

    def __bool__(self) -> bool:
        return any(any(row) for row in self._matrix)

    def __str__(self) -> str:
        matrix = self._matrix
        if self.wy == 1: return str(matrix[0])
        l = len(str(max(max(row) for row in matrix)))
        row1 = '⎡ ' + ' '.join(f'{i:>{l}}' for i in matrix[0]) + ' ⎤\n'
        mid = ('⎢ ' + ' '.join(f'{i:>{l}}' for i in row) + ' ⎥\n' for row in matrix[1:-1])
        rowN = '⎣ ' + ' '.join(f'{i:>{l}}' for i in matrix[-1])+ ' ⎦'
        return row1 + ''.join(mid) + rowN

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.wx}, {self.wy}, {self._matrix})'

    def set_row(self, row: int, iterable: Iterable):
        if len(iterable) != self.wx:
            raise ValueError('Provided iterable\'s length does not match matrix size')
        if row > self.wy - 1 or -row > self.wy:
            raise IndexError('row index out of range')
        self._matrix[row] = list(iterable)
        return self

    def set_col(self, col: int, iterable: Iterable):
        if len(iterable) != self.wy:
            raise ValueError('Provided iterable\'s length does not match matrix size')
        if col > self.wx - 1 or -col > self.wx:
            raise IndexError('column index out of range')
        for n in range(self.wy):
            self._matrix[n][col] = iterable[n]
        return self

    def __add__(self, other: object):
        if not isinstance(other, Matrix):
            return NotImplemented
        if self.wx != other.wx or self.wy != other.wy:
            raise ValueError(f'Matrices are of different size ({self.wx}x{self.wy} vs {other.wx}x{other.wy})')

        return Matrix(self.wx, self.wy, [sum(x) for a in zip(self._matrix, other._matrix) for x in zip(*a)])

    def __sub__(self, other: object):
        if not isinstance(other, Matrix):
            return NotImplemented
        if self.wx != other.wx or self.wy != other.wy:
            raise ValueError(f'Matrices are of different size [{self.wx}, {self.wy}] vs [{other.wx}, {other.wy}]')

        return Matrix(self.wx, self.wy, [b-c for a in zip(self._matrix, other._matrix) for b, c in zip(*a)])

    def __mul__(self, other: Number):
        if isinstance(other, Number):
            return Matrix(self.wx, self.wy, [[n * other for n in row] for row in self._matrix])
        else:
            return NotImplemented
        if self.wx != other.wy:
            raise ValueError(f'Matrix A\'s X size of {self.wx} does not match matrix B\'s Y size of {other.wy}')

    def __matmul__(self, other: object):
        if not isinstance(other, Matrix):
            return NotImplemented
        if self.wx != other.wy:
            raise ValueError(f'Matrix A\'s X size of {self.wx} does not match matrix B\'s Y size of {other.wy}')
        return Matrix(other.wx, self.wy, [sum(x * y for x, y in zip(a, b)) for a in self._matrix for b in zip(*other._matrix)])

    def __pow__(self, num: int):
        if not isinstance(num, int):
            return NotImplemented
        if self.wx != self.wy:
            raise ValueError(f'Matrix is not square ({self.wy}x{self.wx})')
        if num == 1: return self
        if num == 0:
            new = Matrix(self.wx, self.wy)
            for n in range(self.wx): new.__setitem__((n, n), 1)
            return new
        if num < 0: raise ValueError('Inverse matrix not implemented yet')
        return self @ self ** (num - 1)

    def T(self):
        return Matrix(self.wy, self.wx, [list(x) for x in zip(*self._matrix)])

    def shape(self):
        return (self.wx, self.wy)

#--------------------------------- Testing Zone ---------------------------------

if __name__ == '__main__':
    import random
    e = [random.randint(0, 9) for n in range(64)]
    f = [random.randint(0, 9) for n in range(64)]

    A = Matrix(3, 1, [1, 2, 3])
    B = Matrix(3, 3, [1, 2, 3], [4, 5, 6], [7, 8, 9])

    C = Matrix(5, 1, [1, 2, 3, 4, 5])
    D = Matrix(1, 5, [5, 4, 3, 2, 1])

    I = Matrix(8, 8, e)
    J = Matrix(8, 8, f)
    while True:
        # try:
        eval(input())
        # except Exception as error:
        #     print(error)
