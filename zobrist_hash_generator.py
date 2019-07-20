import random
from dlgo.gotypes import Color, Point


def to_python(color_state):
    if color_state is None:
        return 'None'
    if color_state == Color.black:
        return Color.black
    return Color.white


MAX63 = 0x7fffffffffffffff

table = {}
empty_board = 0
for row in range(1, 20):
    for col in range(1, 20):
        for state in (Color.black, Color.white):
            code = random.randint(0, MAX63)
            table[Point(row, col), state] = code


print("from .gotypes import Color, Point")
print()
print("__all__ = ['HASH_CODE', 'EMPTY_BOARD']")
print()
print('HASH_CODE = {')
for (pt, state), hash_code in table.items():
    print('    (%r, %s): %r,' %(pt, to_python(state), hash_code))
print('}\n')
print('EMPTY_BOARD = %d' % (empty_board,))
