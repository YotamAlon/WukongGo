from __future__ import annotations

import copy
import typing
from typing import Optional

from Models.BasicTypes import Color, Move, Point
from Models.Board import Board
from Models.Scoring import Score, evaluate_territory, compute_game_result, GameResult
from Models.zobrist import Hash


class State:
    def __init__(
        self,
        board: Board,
        next_color: Color,
        score: Score,
        previous: Optional[State] = None,
        move: Optional[Move] = None,
        next: Optional[State] = None,
    ):
        self.board = board
        self.next_color = next_color
        self.previous_state = previous
        self._score = score
        self.territory = None
        if self.previous_state is None:
            self.previous_states = frozenset()
        else:
            self.previous_states = frozenset(previous.previous_states | {(previous.next_color, previous.board.hash)})
        self.next_state = next

        self.last_move = move

        self.endgame_mode = False
        self.dead_groups = None

    @classmethod
    def from_moves(cls, board_size: int, komi: Score, moves: list[Move]) -> typing.Self:
        state = cls.new_game(board_size=board_size, komi=komi)
        for move in moves:
            state = state.apply_move(move)

        return state

    def apply_move(self, move: Move) -> State:
        if move.is_play:
            next_board = copy.deepcopy(self.board)
            captured_groups = next_board.place_stone(self.next_color, move.point)
            score = self._score
            for group in captured_groups:
                score = score.with_captured_group(group)
        else:
            next_board = self.board
            score = self._score
        return State(next_board, self.next_color.other, score, self, move)

    def change_dead_stone_marking(self, point: Point | None) -> list[Point]:
        # actually changes a group of stones from dead to alive and vice versa.
        if point is not None:
            group = self.board.get_group(point)
            if group is not None:
                group.change_dead_status()
        self.territory = evaluate_territory(self.board)
        return [point for group in self.board.endgame_dead_groups for point in group.points]

    @classmethod
    def new_game(cls, board_size: int, komi: Score) -> State:
        board_size = (board_size, board_size)
        board = Board(*board_size)
        return State(board, Color.black, komi)

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
        return compute_game_result(self.board)

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
