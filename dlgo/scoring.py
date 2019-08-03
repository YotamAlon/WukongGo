from __future__ import absolute_import
from collections import namedtuple

from dlgo.gotypes import Color, Point

# this class counts the number of territories. for japanese scoring, add captures. for chinese scoring add stones.


class Territory:
    def __init__(self, territory_map):  # <1>
        self.num_black_territory = 0
        self.num_white_territory = 0
        self.num_black_stones = 0
        self.num_white_stones = 0
        self.num_dame = 0
        self.dame_points = []
        for point, status in territory_map.items():  # <2>
            if status == Color.black:
                self.num_black_stones += 1
            elif status == Color.white:
                self.num_white_stones += 1
            elif status == 'territory_black':
                self.num_black_territory += 1
            elif status == 'territory_white':
                self.num_white_territory += 1
            elif status == 'dame':
                self.num_dame += 1
                self.dame_points.append(point)


class GameResult(namedtuple('GameResult', 'b w komi')):
    @property
    def winner(self):
        if self.b > self.w + self.komi:
            return Color.black
        return Color.white

    @property
    def winning_margin(self):
        w = self.w + self.komi
        return abs(self.b - w)

    def __str__(self):
        w = self.w + self.komi
        if self.b > w:
            return 'B+%.1f' % (self.b - w,)
        return 'W+%.1f' % (w - self.b,)


def evaluate_territory(board):
    status = {}
    for r in range(1, board.num_rows + 1):
        for c in range(1, board.num_cols + 1):
            p = Point(row=r, col=c)
            if p in status:
                continue
            color = board.get_color(p)
            if color is not None:
                status[p] = color
            else:
                terr, neighbors = _collect_region(p, board)
                if len(neighbors) == 1:
                    neighbor_color = neighbors.pop()
                    color_str = str(neighbor_color)
                    fill_with = 'territory_' + color_str
                else:
                    fill_with = 'dame'
                for point in terr:
                    status[point] = fill_with
    return Territory(status)


def _collect_region(start_point, board, visited=None):
    if visited is None:
        visited = set()
    if start_point in visited:
        return [], set()

    all_points = [start_point]
    all_borders = set()
    visited.add(start_point)
    start_color = board.get_color(start_point)
    for neighbor in start_point.neighbors():
        if not board.is_on_grid(neighbor):
            continue
        neighbor_color = board.get_color(neighbor)
        if neighbor_color == start_color:
            points, borders = _collect_region(neighbor, board, visited)
            all_points += points
            all_borders |= borders
        else:
            all_borders.add(neighbor_color)
    return all_points, all_borders


def compute_game_result(game_state):
    territory = evaluate_territory(game_state.board)
    return GameResult(
        territory.num_black_territory + territory.num_black_stones,
        territory.num_white_territory + territory.num_white_stones,
        komi=game_state.rule_set.komi.white_score)
