from Models.Scoring import Score
from Models import zobrist


class GoGroup:
    def __init__(self, color, stones, liberties):
        self.color = color
        self.stones = frozenset(stones)
        self.liberties = frozenset(liberties)
        self.is_dead = False  # endgame purposes

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

    def mark_dead(self):
        self.is_dead = not self.is_dead  # again, mark_dead -> change dead marking.

    @property
    def points(self):
        return self.stones

    @property
    def num_liberties(self):
        return len(self.liberties)

    def __eq__(self, other):
        return isinstance(other, GoGroup) and \
            self.color == other.color and \
            self.stones == other.stones and \
            self.liberties == other.liberties

    def __len__(self):
        return len(self.stones)


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
        score = Score.from_dict(score_dict={group.color.other: len(group.stones), group.color: 0})
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

    def get_group(self, point):
        return self._grid.get(point)

    @property
    def grid(self):
        return [(point, self.get_color(point)) for point in self._grid]

    @property
    def size(self):
        assert self.num_cols == self.num_rows
        return self.num_cols

    @property
    def endgame_dead_groups(self):
        return [group for group in self._grid.values() if group.is_dead]

    @property
    def hash(self):
        return self._hash
