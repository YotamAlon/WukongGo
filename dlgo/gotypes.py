import enum
from collections import namedtuple


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


class Score:
    def __init__(self, white_score=None, black_score=None, score_dict=None):
        if score_dict is not None:
            self.white_score = score_dict[Color.white]
            self.black_score = score_dict[Color.black]
        elif white_score is not None and black_score is not None:
            self.white_score = white_score
            self.black_score = black_score
        else:
            print(white_score, black_score, score_dict)
            raise Exception("improper values have been passed to score")

    def __str__(self):
        return "{black: " + str(self.black_score) + ", white: " + str(self.white_score) + "}"

    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        if not isinstance(other, Score):
            print(other)
            print(type(other))
        assert isinstance(other, Score)
        return Score(self.white_score + other.white_score, self.black_score + other.black_score)
