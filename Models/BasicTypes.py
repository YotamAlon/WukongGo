from __future__ import annotations

import dataclasses
import enum
import typing
from collections import namedtuple
from typing import Optional


class Point(namedtuple("Point", "row col")):
    def neighbors(self) -> tuple[typing.Self, typing.Self, typing.Self, typing.Self]:
        return (
            Point(self.row - 1, self.col),
            Point(self.row + 1, self.col),
            Point(self.row, self.col - 1),
            Point(self.row, self.col + 1),
        )

    def __hash__(self) -> int:
        return hash((self.row, self.col))

    def __str__(self) -> str:
        return f"({self.row}, {self.col})"

    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def _int_to_str(num: int) -> str:
        return chr(ord("a") + num - 1)

    @staticmethod
    def _str_to_int(string: str) -> int:
        return ord(string) - ord("a") + 1

    @property
    def sgf_str(self) -> str:
        return self._int_to_str(self.col) + self._int_to_str(self.row)

    @classmethod
    def from_sgf(cls, string: str) -> typing.Self:
        return cls(col=Point._str_to_int(string[0]), row=Point._str_to_int(string[1]))


class Color(enum.Enum):
    black = 1
    white = 2

    @property
    def other(self) -> typing.Self:
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

    @classmethod
    def from_sgf(cls, string: str) -> typing.Self:
        if string == "W":
            return Color.white
        if string == "B":
            return Color.black
        raise Exception("Color sgf string should be W or B")


class MoveType(enum.Enum):
    Pass = "pass"
    Resign = "resign"
    Play = "play"


@dataclasses.dataclass
class Move:
    _row: Optional[int]
    _col: Optional[int]
    _type: MoveType

    def __init__(self, point: Point = None, is_pass: bool = False, is_resign: bool = False):
        if (point is None) and not is_pass and not is_resign:
            raise Exception("Move must have a point or be a pass or a resign")
        super(Move, self).__init__()
        self.point = point
        if is_pass:
            self._type = MoveType.Pass
        elif is_resign:
            self._type = MoveType.Resign
        else:
            self._type = MoveType.Play

    @property
    def point(self) -> Optional[Point]:
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
        return self._type is MoveType.Play

    @property
    def is_pass(self) -> bool:
        return self._type is MoveType.Pass

    @property
    def is_resign(self) -> bool:
        return self._type is MoveType.Resign

    @classmethod
    def play(cls, point: Point) -> typing.Self:
        return cls(point=point, is_pass=False, is_resign=False)

    @classmethod
    def pass_turn(cls) -> typing.Self:
        return cls(point=None, is_pass=True, is_resign=False)

    @classmethod
    def resign(cls) -> typing.Self:
        return cls(point=None, is_pass=False, is_resign=True)

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

    @classmethod
    def from_sgf(cls, string: str) -> typing.Self:
        return cls(Point.from_sgf(string))
