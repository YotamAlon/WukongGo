from peewee import Model, ForeignKeyField, ManyToManyField
from Models.User import User
from Models.Timer import Timer
from Models.State import State
from Models import db_proxy
from Models.BasicTypes import Move


class Game(Model):
    users = ManyToManyField(User, backref='games')
    timer = ForeignKeyField(Timer, backref='game')
    state = ForeignKeyField(State, backref='game')

    class Meta:
        database = db_proxy

    @classmethod
    def new_game(cls, size, rule_set, **query):
        state = State.new_game(size, rule_set)
        return cls.create(state=state, **query)

    def is_legal(self, move):
        assert isinstance(move, Move)
        return self.state.is_valid_move(move)

    def make_move(self, move):
        assert isinstance(move, Move)
        self.state = self.state.apply_move(move)

    @property
    def score(self):
        return self.state.score

    @property
    def grid(self):
        return self.state.board.grid


GameUser = Game.users.get_through_model()
