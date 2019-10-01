from Models.Board import Board
import copy
from Models.BasicTypes import Color
from Models.Scoring import compute_game_result


class State:
    def __init__(self, board, rule_set, next_color, previous, move, score):
        self.board = board
        self.next_color = next_color
        self.previous_state = previous
        self.rule_set = rule_set
        self.score = score
        if self.previous_state is None:
            self.previous_states = frozenset()
        else:
            self.previous_states = frozenset(
                previous.previous_states |
                {(previous.next_color, previous.board.hash)})

        self.last_move = move

        self.endgame_mode = False
        self.dead_groups = None

    def apply_move(self, move):
        if move.is_play:
            next_board = copy.deepcopy(self.board)
            score = next_board.place_stone(self.next_color, move.point) + self.score
        else:
            next_board = self.board
            score = self.score
        return State(next_board, self.rule_set, self.next_color.other, self, move, score)

    @classmethod
    def new_game(cls, board_size, rule_set):
        assert isinstance(board_size, int)
        board_size = (board_size, board_size)
        board = Board(*board_size)
        return State(board, rule_set, Color.black, None, None, rule_set.komi)

    def is_over(self):
        if self.last_move is None:
            self.endgame_mode = False
        elif self.last_move.is_resign:
            self.endgame_mode = True
        elif self.previous_state.last_move is None:
            self.endgame_mode = False
        else:
            self.endgame_mode = self.last_move.is_pass and self.previous_state.last_move.is_pass
        return self.endgame_mode

    def get_game_result(self):
        assert self.endgame_mode
        return compute_game_result(self)

    @property
    def situation(self):
        return self.next_color, self.board.hash

    def is_valid_move(self, move):
        return self.rule_set.is_valid_move(game_state=self, color=self.next_color, move=move)