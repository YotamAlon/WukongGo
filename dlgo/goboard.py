import copy
from dlgo.gotypes import Color
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
                self._remove_group(other_color_group)

        for other_color_group in adjacent_opposite_color:
            if other_color_group.num_liberties == 0:
                self._remove_group(other_color_group)

    def _replace_group(self, new_group):
        for point in new_group.stones:
            self._grid[point] = new_group

    def is_on_grid(self, point):
        return 1 <= point.row <= self.num_rows and \
            1 <= point.col <= self.num_cols

    def get(self, point):
        group = self._grid.get(point)
        return None if group is None else group.color

    def get_go_group(self, point):
        return self._grid.get(point)

    def _remove_group(self, group):
        for point in group.stones:
            for neighbor in point.neighbors():
                neighbor_group = self._grid.get(neighbor)
                if neighbor_group is None:
                    continue
                if neighbor_group is not group:
                    neighbor_group.add_liberty(point)
            self._grid[point] = None

            self._hash ^= zobrist.HASH_CODE[point, group.color]

    def zobrist_hash(self):
        return self._hash


class GameState:
    def __init__(self, board, next_color, previous, move):
        self.board = board
        self.next_color = next_color
        self.previous_state = previous
        if self.previous_state is None:
            self.previous_states = frozenset()
        else:
            self.previous_states = frozenset(
                previous.previous_states |
                {(previous.next_color, previous.board.zobrist_hash())})

        self.last_move = move

    def apply_move(self, move):
        if move.is_play:
            next_board = copy.deepcopy(self.board)
            next_board.place_stone(self.next_color, move.point)
        else:
            next_board = self.board
        return GameState(next_board, self.next_color.other, self, move)

    @classmethod
    def new_game(cls, board_size):
        if isinstance(board_size, int):
            board_size = (board_size, board_size)
            board = Board(*board_size)
            return GameState(board, Color.black, None, None)

    def is_over(self):
        if self.last_move is None:
            return False
        if self.last_move.is_resign:
            return True
        second_last_move = self.previous_state.last_move
        if second_last_move is None:
            return False
        return self.last_move.is_pass and second_last_move.is_pass

    def is_move_self_capture(self, color, move):
        """
        note - this is illegal in most game rule sets, but not in chinese.
        """
        if not move.is_play:
            return False
        next_board = copy.deepcopy(self.board)
        next_board.place_stone(color, move.point)
        new_group = next_board.get_go_group(move.point)
        return new_group.num_liberties == 0

    @property
    def situation(self):
        return self.next_color, self.board

    def does_move_violate_ko(self, color, move):
        """
        note - superko is implemented, some rule sets might declare a tie on superko, instead of this.
        """
        if not move.is_play:
            return False
        next_board = copy.deepcopy(self.board)
        next_board.place_stone(color, move.point)
        next_situation = (color.other, next_board.zobrist_hash())
        return next_situation in self.previous_states

    def is_valid_move(self, move):
        if self.is_over():
            return False
        if move.is_resign or move.is_pass:
            return True
        return (
            self.board.get(move.point) is None and
            not self.is_move_self_capture(self.next_color, move) and
            not self.does_move_violate_ko(self.next_color, move))
