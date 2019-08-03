from peewee import Model, IntegerField, ForeignKeyField, BooleanField
import enum
from Models import db_proxy


class Point(Model):
    row = IntegerField()
    col = IntegerField()

    class Meta:
        database = db_proxy

    def neighbors(self):
        return [
            Point(self.row - 1, self.col),
            Point(self.row + 1, self.col),
            Point(self.row, self.col - 1),
            Point(self.row, self.col + 1)
        ]

    """def __hash__(self):
        return hash((self.row, self.col))"""  # hash is already implemented for any Model?

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


class Score(Model):
    w_score = IntegerField()
    b_score = IntegerField()

    class Meta:
        database = db_proxy

    def __str__(self):
        return f'black: {self.b_score}, white: {self.w_score}'

    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        assert isinstance(other, Score)
        return Score(self.w_score + other.w_score, self.b_score + other.b_score)


class Move(Model):
    point = ForeignKeyField(Point, backref="point")
    is_play = BooleanField()
    is_pass = BooleanField()
    is_resign = BooleanField()

    class Meta:
        database = db_proxy

    @classmethod
    def play(cls, point):
        return Move(point=point, is_play=True, is_pass=False, is_resign=False)

    @classmethod
    def pass_turn(cls):
        return cls.create(point=None, is_play=False, is_pass=True, is_resign=False)

    @classmethod
    def resign(cls):
        return cls.create(point=None, is_play=False, is_pass=False, is_resign=True)

    def __str__(self):
        if self.is_pass:
            return str(self.point)
        return "pass" if self.is_pass else "resign"

    def __repr__(self):
        return str(self)
