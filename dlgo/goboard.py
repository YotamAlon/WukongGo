import copy
from dlgo.gotypes import Color, Score
from dlgo import zobrist

"""
note - goboard_fast.py in the authors git, should be even faster. but not very readable.
until necessary we will use this.
"""


class Move:
    def __init__(self, point=None, is_pass=False, is_resign=False):
        assert (point is not None) ^ is_pass ^ is_resign
        self.point = point
        self.is_play = (self.point is not None)
        self.is_pass = is_pass
        self.is_resign = is_resign

    @classmethod
    def play(cls, point):
        return Move(point=point)

    @classmethod
    def pass_turn(cls):
        return Move(is_pass=True)

    @classmethod
    def resign(cls):
        return Move(is_resign=True)


class GoGroup:
    def __init__(self, color, stones, liberties):
        self.color = color
        self.stones = frozenset(stones)
        self.liberties = frozenset(liberties)

    def without_liberty(self, point):
        new_liberties = self.liberties - {point}
        return GoGroup(self.color, self.stones, new_liberties)

    def with_liberty(self, point):
        new_liberties = self.liberties | {point}
        return GoGroup(self.color, self.stones, new_liberties)

    def merged_with(self, go_group):
        assert go_group.color == self.color
        combined_stones = self.stones | go_group.stones
        return GoGroup(
            self.color,
            combined_stones,
            (self.liberties | go_group.liberties) - combined_stones)

    @property
    def num_liberties(self):
        return len(self.liberties)

    def __eq__(self, other):
        return isinstance(other, GoGroup) and \
            self.color == other.color and \
            self.stones == other.stones and \
            self.liberties == other.liberties


class Board:
    def __init__(self, num_rows, num_cols):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self._grid = {}
        self._hash = zobrist.EMPTY_BOARD

    def place_stone(self, color, point):
        assert self.is_on_grid(point)
        assert self._grid.get(point) is None
        adjacent_same_color = []
        adjacent_opposite_color = []
        liberties = []
        score = Score(0, 0)

        for neighbor in point.neighbors():
            if not self.is_on_grid(neighbor):
                continue
            neighbor_group = self._grid.get(neighbor)
            if neighbor_group is None:
                liberties.append(neighbor)
            elif neighbor_group.color == color:
                if neighbor_group not in adjacent_same_color:
                    adjacent_same_color.append(neighbor_group)
            else:
                if neighbor_group not in adjacent_opposite_color:
                    adjacent_opposite_color.append(neighbor_group)

        new_group = GoGroup(color, [point], liberties)

        for same_color_group in adjacent_same_color:
            new_group = new_group.merged_with(same_color_group)
        for new_group_point in new_group.stones:
            self._grid[new_group_point] = new_group

        self._hash ^= zobrist.HASH_CODE[point, color]

        for other_color_group in adjacent_opposite_color:
            replacement = other_color_group.without_liberty(point)
            if replacement.num_liberties:
                self._replace_group(other_color_group.without_liberty(point))
            else:
                score += self._remove_group(other_color_group)
        return score

    def _replace_group(self, new_group):
        for point in new_group.stones:
            self._grid[point] = new_group

    def _remove_group(self, group):
        score = Score(score_dict={group.color.other: len(group.stones), group.color: 0})
        for point in group.stones:
            for neighbor in point.neighbors():
                neighbor_group = self._grid.get(neighbor)
                if neighbor_group is None:
                    continue
                if neighbor_group is not group:
                    self._replace_group(neighbor_group.with_liberty(point))
            self._grid[point] = None

            self._hash ^= zobrist.HASH_CODE[point, group.color]
        return score

    def is_on_grid(self, point):
        return 1 <= point.row <= self.num_rows and \
            1 <= point.col <= self.num_cols

    def get(self, point):
        group = self._grid.get(point)
        return None if group is None else group.color

    def get_grid(self):
        return [(point, self.get(point)) for point in self._grid]

    def get_go_group(self, point):
        return self._grid.get(point)

    def zobrist_hash(self):
        return self._hash


class GameState:
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
                {(previous.next_color, previous.board.hash())})

        self.last_move = move

    def apply_move(self, move):
        if move.is_play:
            next_board = copy.deepcopy(self.board)
            score = next_board.place_stone(self.next_color, move.point) + self.score
        else:
            next_board = self.board
            score = self.score
        return GameState(next_board, self.rule_set, self.next_color.other, self, move, score)

    @classmethod
    def new_game(cls, board_size, rule_set):
        if isinstance(board_size, int):
            board_size = (board_size, board_size)
            board = Board(*board_size)
            return GameState(board, rule_set, Color.black, None, None, rule_set.komi)

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
