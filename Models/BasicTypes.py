from __future__ import annotations

import enum
from collections import namedtuple

from peewee import Model, CharField, IntegerField

from Models import db_proxy


class Point(namedtuple('Point', 'row col')):
    def neighbors(self) -> tuple[Point, Point, Point, Point]:
        return (
            Point(self.row - 1, self.col),
            Point(self.row + 1, self.col),
            Point(self.row, self.col - 1),
            Point(self.row, self.col + 1)
        )

    def __hash__(self) -> int:
        return hash((self.row, self.col))

    def __str__(self) -> str:
        return f'({self.row}, {self.col})'

    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def _int_to_str(num: int) -> str:
        return chr(ord('a') + num - 1)

    @staticmethod
    def _str_to_int(string: str) -> int:
        return ord(string) - ord('a') + 1

    @property
    def sgf_str(self) -> str:
        return self._int_to_str(self.col) + self._int_to_str(self.row)

    @staticmethod
    def from_sgf(string: str) -> Point:
        return Point(col=Point._str_to_int(string[0]), row=Point._str_to_int(string[1]))


class Color(enum.Enum):
    black = 1
    white = 2

    @property
    def other(self) -> Color:
        return Color.black if self == Color.white else Color.white

    def __str__(self) -> str:
        if self == Color.white:
            return "white"
        return "black"

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def sgf_str(self) -> str:
        return "W" if self == Color.white else "B"

    @staticmethod
    def from_sgf(string: str) -> Color:
        if string == "W":
            return Color.white
        if string == "B":
            return Color.black
        raise Exception("Color sgf string should be W or B")


class Move(Model):
    _row = IntegerField(null=True)
    _col = IntegerField(null=True)
    _type = CharField()

    class Meta:
        database = db_proxy

    def __init__(self, point: Point = None, is_pass: bool = False, is_resign: bool = False):
        if (point is None) and not is_pass and not is_resign:
            raise Exception('Move must have a point or be a pass or a resign')
        super(Move, self).__init__()
        self.point = point
        if is_pass:
            self._type = 'pass'
        elif is_resign:
            self._type = 'resign'
        else:
            self._type = 'play'

    @property
    def point(self) -> Point:
        if self._row is None and self._col is None:
            return None
        return Point(self._row, self._col)

    @point.setter
    def point(self, value: Point) -> None:
        if value is None:
            self._row = self._col = None
        else:
            self._row = value.row
            self._col = value.col

    @property
    def is_play(self) -> bool:
        return self._type == 'play'

    @property
    def is_pass(self) -> bool:
        return self._type == 'pass'

    @property
    def is_resign(self) -> bool:
        return self._type == 'resign'

    @staticmethod
    def play(point: Point) -> Move:
        return Move(point=point, is_pass=False, is_resign=False)

    @staticmethod
    def pass_turn() -> Move:
        return Move(point=None, is_pass=True, is_resign=False)

    @staticmethod
    def resign() -> Move:
        return Move(point=None, is_pass=False, is_resign=True)

    def __str__(self) -> str:
        if self.is_play:
            return str(self.point)
        return "pass" if self.is_pass else "resign"

    def __repr__(self) -> str:
        return str(self)

    @property
    def sgf_str(self) -> str:
        if self.is_play:
            return self.point.sgf_str
        if self.is_pass:
            raise Exception("pass type moves shouldn't be converted to sgf")
        if self.is_resign:
            raise Exception("resign type moves shouldn't be converted to sgf")

    @staticmethod
    def from_sgf(string: str) -> Move:
        return Move(Point.from_sgf(string))
