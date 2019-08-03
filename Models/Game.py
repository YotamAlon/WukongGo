from Models.State import State
from Models.BasicTypes import Move, Point


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

    @property
    def score(self):
        return self.state.score

    @property
    def grid(self):
        return self.state.board.grid

    @property
    def size(self):
        return self.state.board.size
