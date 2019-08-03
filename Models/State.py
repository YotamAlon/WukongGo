from peewee import Model, ForeignKeyField
from Models.Board import Board
from Models import db_proxy
from copy import copy
from Models.BasicTypes import Move, Color
# equivalent to GameState from dlgo.goboard


class State_2(Model):
    # players = ManyToManyField(Player) - provided by backref from Player
    board = ForeignKeyField(Board, backref='go_game')

    class Meta:
        database = db_proxy

    def resign(self):
        move = Move(is_resign=True)
        self.board.state.apply_move(move)


class State(Model):
    board = ForeignKeyField(Board, backref='go_game')
    next_color = None
    previous_state = None
    previous_states = None
    rule_set = None
    score = None
    last_move = None

    class Meta:
        database = db_proxy

    def apply_move(self, move):
        if move.is_play:
            next_board = copy.deepcopy(self.board)
            score = next_board.place_stone(self.next_color, move.point) + self.score
        else:
            next_board = self.board
            score = self.score

        previous = self.previous_state
        previous_states = frozenset(
            previous.previous_states |
            {(previous.next_color, previous.board.hash())})
        return State(board=next_board, rule_set=self.rule_set, next_color=self.next_color.other,
                     last_move=move, previous_state=self, previous_states=previous_states, score=score)

    @classmethod
    def new_game(cls, board_size, rule_set):
        assert isinstance(board_size, int)
        board_size = (board_size, board_size)
        board = Board(*board_size)
        return cls.create(board=board, rule_set=rule_set, next_color=Color.black, last_move=None, previous_state=None,
                          previous_states=frozenset(), score=rule_set.komi)

    def is_over(self):
        if self.last_move is None:
            return False
        if self.last_move.is_resign:
            return True
        second_last_move = self.previous_state.last_move
        if second_last_move is None:
            return False
        return self.last_move.is_pass and second_last_move.is_pass

    @property
    def situation(self):
        return self.next_color, self.board.hash()

    def is_valid_move(self, move):
        return self.rule_set.is_valid_move(game_state=self, color=self.next_color, move=move)