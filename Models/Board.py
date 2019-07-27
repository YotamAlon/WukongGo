from peewee import Model, IntegerField, TextField
from Models import db_proxy
from dlgo.rules import get_japanese_rule_set
from dlgo.goboard import Move, GameState


class Board(Model):
    size = IntegerField()
    # history = ManyToManyField(Move) - provided by backref from Move

    class Meta:
        database = db_proxy

    def __init__(self, *args, **kwargs):
        super(Board, self).__init__(*args, **kwargs)
        self.state = GameState.new_game(self.size, get_japanese_rule_set())

    def is_move_legal(self, point):
        move = Move.play(point)
        return self.state.is_valid_move(move)

    def make_move(self, point=None, is_pass=False, is_resign=False):
        move = Move(point, is_pass=is_pass, is_resign=is_resign)
        self.state = self.state.apply_move(move)

    @property
    def score(self):
        return self.state.score

    @property
    def grid(self):
        return self.state.board.get_grid()
