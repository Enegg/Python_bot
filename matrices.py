import random

# cases:
# ([a, b, c, d], )
# ([[a, b], [c, d]], )
# ([a, b], [c, d])

class Matrix:
    def __init__(self, wx: int, wy: int, *args):
        self.wx = int(abs(int(wx)))
        self.wy = int(abs(int(wy)))
        if not args:
            self._matrix = [[0] * self.wx for n in range(self.wy)]
            return
        if len(args) == 1: args = args[0]
        if (lt := len(args)) == self.wy and isinstance(args[0], (tuple, list)):
            self._matrix = list(args)
        elif lt == len(self):
            self._matrix = [list(args[n * self.wx:(n + 1) * self.wx]) for n in range(self.wy)]
        else:
            print(args)
            raise Exception('Matrix not initialized properly')
        for a in self._matrix:
            for x in a:
                if not isinstance(x, (int, float, bool, complex)):
                    print(args)
                    raise ValueError(f'Value "{x}" is not of type int, float, bool or complex')

    def __len__(self) -> int:
        return self.wx * self.wy

    def __getitem__(self, key: tuple):
        if not isinstance(key, tuple): raise TypeError(f'{key} is not a valid format')
        if len(key) != 2: raise ValueError
        if key[0] > self.wx - 1 or key[1] > self.wy - 1: raise IndexError # positive indexes
        if (key[0] < 0 and abs(key[0]) > self.wx) or (key[1] < 0 and abs(key[1]) > self.wy): raise IndexError # negative indexes
        return self._matrix[key[1]][key[0]]

    def __setitem__(self, key: tuple, value):
        if not isinstance(key, tuple): raise TypeError(f'{key} is not a valid format')
        if len(key) != 2: raise ValueError
        if key[0] > self.wx - 1 or key[1] > self.wy - 1: raise IndexError # positive indexes
        if (key[0] < 0 and abs(key[0]) > self.wx) or (key[1] < 0 and abs(key[1]) > self.wy): raise IndexError # negative indexes
        self._matrix[key[1]][key[0]] = value

    def __bool__(self) -> bool:
        return any(any(row) for row in self._matrix)

    def __str__(self) -> str:
        matrix = self._matrix
        if self.wy == 1: return str(matrix[0])
        _max = len(max([str(i) for row in matrix for i in row], key=len))
        row1 = '⎡ ' + ' '.join(str(i).rjust(_max) for i in matrix[0]) + ' ⎤\n'
        mid = ('⎢ ' + ' '.join(str(i).rjust(_max) for i in row) + ' ⎥\n' for row in matrix[1:-1])
        rowN = '⎣ ' + ' '.join(str(i).rjust(_max) for i in matrix[-1])+ ' ⎦'
        return row1 + ''.join(mid) + rowN

    def __repr__(self) -> str:
        return f'Matrix({self.wx}, {self.wy}, {self._matrix})'

    def set_row(self, row: int, iterable):
        row = int(row)
        if len(iterable) != self.wx:
            raise ValueError('Provided iterable\'s length does not match matrix size')
        if row > self.wy - 1 or (row < 0 and abs(row) > self.wy):
            raise IndexError
        self._matrix[row] = list(iterable)
        return self

    def set_col(self, col: int, iterable):
        col = int(col)
        if len(iterable) != self.wy:
            raise ValueError('Provided iterable\'s length does not match matrix size')
        if col > self.wx - 1 or (col < 0 and abs(col) > self.wx):
            raise IndexError
        for n in range(self.wy):
            self._matrix[n][col] = iterable[n]
        return self

    def __add__(self, other: object):
        if not isinstance(other, Matrix):
            raise TypeError(f'Unsupported operation for type {type(other)}')
        if self.wx != other.wx or self.wy != other.wy:
            raise ValueError(f'Matrices are of different size [{self.wx}, {self.wy}] vs [{other.wx}, {other.wy}]')
        new = Matrix(self.wx, self.wy, [self[x, y] + other[x, y] for x in range(self.wx) for y in range(self.wy)])
        return new

    def __sub__(self, other: object):
        if not isinstance(other, Matrix):
            raise TypeError(f'Unsupported operation for type {type(other)}')
        if self.wx != other.wx or self.wy != other.wy:
            raise ValueError(f'Matrices are of different size [{self.wx}, {self.wy}] vs [{other.wx}, {other.wy}]')
        new = Matrix(self.wx, self.wy, [self[x, y] - other[x, y] for x in range(self.wx) for y in range(self.wy)])
        return new

    def __mul__(self, other: object):
        if (isdigit := isinstance(other, (int, bool, float, complex))) or isinstance(other, Matrix):
            pass
        else: raise TypeError(f'Unsupported operation for type {type(other)}')
        if isdigit:
            return Matrix(self.wx, self.wy, [[n * other for n in row] for row in self._matrix])
        if self.wx != other.wy:
            raise ValueError(f'Matrix A\'s X size of {self.wx} does not match matrix B\'s Y size of {other.wy}')
        new = Matrix(other.wx, self.wy)
        for row in range(new.wy):
            for col in range(new.wx):
                new[col, row] = sum(self._matrix[row][n] * other._matrix[n][col] for n in range(self.wx))

        return new

    def __matmul__(self, other: object):
        if not isinstance(other, Matrix):
            raise TypeError(f'Unsupported operation for type {type(other)}')
        if self.wx != other.wy:
            raise ValueError(f'Matrix A\'s X size of {self.wx} does not match matrix B\'s Y size of {other.wy}')
        return Matrix(other.wx, self.wy, [sum(x * y for x, y in zip(a, b)) for a in self._matrix for b in zip(*other._matrix)])

    def __pow__(self, other: float):
        if not isinstance(other, (int, bool, float)):
            raise TypeError(f'Unsupported operation for type {type(other)}')
        if self.wx != self.wy:
            raise ValueError(f'Matrix is not square ({self.wy}x{self.wx})')
        if other == 1: return self
        if other == 0:
            new = Matrix(self.wx, self.wy)
            for n in range(self.wx):
                new[n, n] = 1
            return new
        if other < 0: raise ValueError(f'Matrix power must not be negative (got {other})')
        return self * self.__pow__(other - 1)

    def T(self):
        return Matrix(self.wy, self.wx, [list(x) for x in zip(*self._matrix)])

    def shape(self):
        return (self.wx, self.wy)

#--------------------------------- Testing Zone ---------------------------------

if __name__ == '__main__':
    e = [random.randint(0, 9) for n in range(64)]
    f = [random.randint(0, 9) for n in range(64)]

    A = Matrix(3, 1, [1, 2, 3])
    B = Matrix(3, 3, [1, 2, 3], [4, 5, 6], [7, 8, 9])

    C = Matrix(5, 1, [1, 2, 3, 4, 5])
    D = Matrix(1, 5, [5, 4, 3, 2, 1])

    I = Matrix(8, 8, e)
    J = Matrix(8, 8, f)
    while True:
        try:
            eval(input())
        except Exception as error:
            print(error)
