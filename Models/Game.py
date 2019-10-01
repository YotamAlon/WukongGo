from Models.State import State
from Models.BasicTypes import Move, Point, Color
from Models.SGF import SGF
from Models.Rule import get_rule_set_by_name
from Models.Player import Player
from Models.User import User
from Models.Timer import Timer


class Game:
    def __init__(self, players, timer, state):
        self.players = players
        self.timer = timer
        self.state = state

    @classmethod
    def new_game(cls, size, rule_set, players, timer):
        state = State.new_game(size, rule_set)
        return Game(players, timer, state)

    def is_legal(self, point):
        assert isinstance(point, Point)
        move = Move.play(point)
        return self.state.is_valid_move(move)

    def make_move(self, point):
        return self._make_move(Move.play(point))

    def _make_move(self, move):
        self.state = self.state.apply_move(move)
        if self.state.is_over():
            return self.state.get_game_result()

    def pass_turn(self):
        return self._make_move(Move.pass_turn())

    def resign(self):
        return self._make_move(Move.resign())

    def to_sgf(self):
        return SGF(self)

    @staticmethod
    def _from_sgf(sgf):
        assert isinstance(sgf, SGF)
        size = sgf.header['SZ']
        rules = get_rule_set_by_name(sgf.header['RU'])
        players = {Color.black: Player(User(sgf.header['BP'], 1), Color.black),
                   Color.white: Player(User(sgf.header['WP'], 2), Color.white)}
        game = Game.new_game(size, rules, players, Timer())

        for move in sgf.moves:
            game.make_move(Move.from_sgf(move[game.state.next_color.sgf_str]))
        return game

    @staticmethod
    def from_sgf(sgf_string):
        sgf = SGF.from_string(sgf_string)
        return Game._from_sgf(sgf)

    @property
    def score(self):
        return self.state.score

    @property
    def grid(self):
        return self.state.board.grid

    @property
    def size(self):
        return self.state.board.size

    def get_black_white_points(self):
        return [Point(1, 1)], [Point(2, 2)]

    def mark_dead_stone(self, point):
        pass
