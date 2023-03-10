from __future__ import annotations

import copy
from typing import Optional

from Models.BasicTypes import Color, Move, Point
from Models.Board import Board
from Models.Rule import RuleSet
from Models.Scoring import Score
from Models.Scoring import compute_game_result, get_territory, GameResult
from Models.zobrist import Hash


class State:
    def __init__(self, board: Board, rule_set: RuleSet, next_color: Color, score: Score,
                 previous: Optional[State] = None, move: Optional[Move] = None):
        self.board = board
        self.next_color = next_color
        self.previous_state = previous
        self.rule_set = rule_set
        self._score = score
        self.territory = None
        if self.previous_state is None:
            self.previous_states = frozenset()
        else:
            self.previous_states = frozenset(
                previous.previous_states |
                {(previous.next_color, previous.board.hash)})

        self.last_move = move

        self.endgame_mode = False
        self.dead_groups = None

    def apply_move(self, move: Move) -> State:
        if move.is_play:
            next_board = copy.deepcopy(self.board)
            score = next_board.place_stone(self.next_color, move.point) + self._score
        else:
            next_board = self.board
            score = self._score
        return State(next_board, self.rule_set, self.next_color.other, score, self, move)

    def change_dead_stone_marking(self, point: Point) -> list[Point]:
        # actually changes a group of stones from dead to alive and vice versa.
        if point is not None:
            group = self.board.get_group(point)
            if group is not None:
                group.change_dead_status()
        self.territory = get_territory(self)
        return [point for group in self.board.endgame_dead_groups for point in group.points]

    @classmethod
    def new_game(cls, board_size: int, rule_set: RuleSet) -> State:
        board_size = (board_size, board_size)
        board = Board(*board_size)
        return State(board, rule_set, Color.black, rule_set.komi)

    def is_over(self) -> bool:
        if self.last_move is None:
            self.endgame_mode = False
        elif self.last_move.is_resign:
            self.endgame_mode = True
        elif self.previous_state.last_move is None:
            self.endgame_mode = False
        else:
            self.endgame_mode = self.last_move.is_pass and self.previous_state.last_move.is_pass
        return self.endgame_mode

    def get_game_result(self) -> GameResult:
        assert self.endgame_mode
        return compute_game_result(self)

    @property
    def situation(self) -> tuple[Color, Hash]:
        return self.next_color, self.board.hash

    @property
    def score(self) -> Score:
        black, white = self._score.b_score, self._score.w_score
        if self.territory is not None:
            black += self.territory.num_black_territory
            white += self.territory.num_white_territory
            groups = self.board.endgame_dead_groups
            white += sum(len(group) for group in groups if group.color == Color.black)
            black += sum(len(group) for group in groups if group.color == Color.white)
        return Score(w_score=white, b_score=black)

    def is_valid_move(self, move) -> bool:
        return self.rule_set.is_valid_move(game_state=self, color=self.next_color, move=move)
