import enum
from collections import namedtuple


class Point(namedtuple('Point', 'row col')):
    def neighbors(self):
        return [
            Point(self.row - 1, self.col),
            Point(self.row + 1, self.col),
            Point(self.row, self.col - 1),
            Point(self.row, self.col + 1)
        ]

    def __hash__(self):
        return hash((self.row, self.col))

    def __str__(self):
        return f'({self.row}, {self.col})'

    def __repr__(self):
        return self.__str__()


class Color(enum.Enum):
    black = 1
    white = 2

    @property
    def other(self):
        return Color.black if self == Color.white else Color.white

    def __str__(self):
        if self == Color.white:
            return "white"
        return "black"

    def __repr__(self):
        return self.__str__()


class Move:
    def __init__(self, point=None, is_pass=False, is_resign=False):
        assert (point is not None) ^ is_pass ^ is_resign
        self.point = point
        self.is_play = (self.point is not None)
        self.is_pass = is_pass
        self.is_resign = is_resign

    @staticmethod
    def play(point):
        return Move(point=point, is_pass=False, is_resign=False)

    @staticmethod
    def pass_turn():
        return Move(point=None, is_pass=True, is_resign=False)

    @staticmethod
    def resign():
        return Move(point=None, is_pass=False, is_resign=True)

    def __str__(self):
        if self.is_play:
            return str(self.point)
        return "pass" if self.is_pass else "resign"

    def __repr__(self):
        return str(self)
