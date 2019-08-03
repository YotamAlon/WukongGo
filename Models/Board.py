from peewee import Model, IntegerField, ForeignKeyField
from Models import db_proxy
from Models.BasicTypes import Move, Score
# from dlgo.rules import get_japanese_rule_set
# from dlgo.goboard import GameState
from dlgo import zobrist


class GoGroup(Model):
    def __init__(self, color, stones, liberties):
        self.color = ForeignKeyField(color)
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


class Board(Model):
    num_rows = IntegerField()
    num_cols = IntegerField()
    size = IntegerField()
    _grid = {}
    _hash = IntegerField(zobrist.EMPTY_BOARD)

    class Meta:
        database = db_proxy

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

    def get_color(self, point):
        group = self._grid.get(point)
        return None if group is None else group.color

    @property
    def grid(self):
        return [(point, self.get_color(point)) for point in self._grid]

    def get_group(self, point):
        return self._grid.get(point)

    @property
    def hash(self):
        return self._hash

"""
class Board2(Model):
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
        return self.state.board.grid()
"""