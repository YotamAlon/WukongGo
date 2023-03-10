from __future__ import annotations

from typing import Any, Iterable, Optional

from Models import zobrist
from Models.BasicTypes import Color, Point


class GoGroup:
    def __init__(self, color: Color, stones: Iterable[Point], liberties: Iterable[Point]):
        self.color = color
        self.stones = frozenset(stones)
        self.liberties = frozenset(liberties)
        self.is_dead = False  # endgame purposes

    def without_liberty(self, point: Point) -> GoGroup:
        new_liberties = self.liberties - {point}
        return GoGroup(self.color, self.stones, new_liberties)

    def with_liberty(self, point: Point) -> GoGroup:
        new_liberties = self.liberties | {point}
        return GoGroup(self.color, self.stones, new_liberties)

    def merged_with(self, go_group: GoGroup) -> GoGroup:
        assert go_group.color == self.color
        combined_stones = self.stones | go_group.stones
        return GoGroup(
            self.color,
            combined_stones,
            (self.liberties | go_group.liberties) - combined_stones)

    def change_dead_status(self) -> None:
        self.is_dead = not self.is_dead  # again, mark_dead -> change dead marking.

    @property
    def points(self) -> frozenset[Point]:
        return self.stones

    @property
    def num_liberties(self) -> int:
        return len(self.liberties)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, GoGroup) and \
            self.color == other.color and \
            self.stones == other.stones and \
            self.liberties == other.liberties

    def __len__(self) -> int:
        return len(self.stones)


class Board:
    def __init__(self, num_rows: int, num_cols: int):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self._grid = {}
        self._hash = zobrist.EMPTY_BOARD

    def place_stone(self, color: Color, point: Point) -> list[GoGroup]:
        if not self.is_on_grid(point):
            raise ValueError('The provided point is not on the board!')
        if self._grid.get(point) is not None:
            raise ValueError('That spot on the board is already taken!')

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

        captured_groups = []
        for other_color_group in adjacent_opposite_color:
            replacement = other_color_group.without_liberty(point)
            if replacement.num_liberties:
                self._replace_group(other_color_group.without_liberty(point))
            else:
                captured_groups.append(other_color_group)
                self._remove_group(other_color_group)

        return captured_groups

    def _replace_group(self, new_group: GoGroup) -> None:
        for point in new_group.stones:
            self._grid[point] = new_group

    def _remove_group(self, group: GoGroup) -> None:
        for point in group.stones:
            for neighbor in point.neighbors():
                neighbor_group = self._grid.get(neighbor)
                if neighbor_group is None:
                    continue
                if neighbor_group is not group:
                    self._replace_group(neighbor_group.with_liberty(point))
            self._grid[point] = None

            self._hash ^= zobrist.HASH_CODE[point, group.color]

    def is_on_grid(self, point: Point) -> bool:
        return 1 <= point.row <= self.num_rows and \
            1 <= point.col <= self.num_cols

    def get_color(self, point: Point) -> Optional[Color]:
        group = self._grid.get(point)
        return None if group is None else group.color

    def get_group(self, point: Point) -> GoGroup:
        return self._grid.get(point)

    @property
    def grid(self) -> list[tuple[Point, Color]]:
        return [(point, self.get_color(point)) for point in self._grid]

    @property
    def size(self) -> int:
        assert self.num_cols == self.num_rows
        return self.num_cols

    @property
    def endgame_dead_groups(self) -> list[GoGroup]:
        return [group for group in self._grid.values() if group.is_dead]

    @property
    def hash(self) -> int:
        return self._hash
