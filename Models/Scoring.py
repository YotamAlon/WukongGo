from __future__ import annotations

from Models.BasicTypes import Color, Point
from Models.Board import Board
from Models.State import State


class Score:
    def __init__(self, w_score=0, b_score=0):
        self.w_score = w_score
        self.b_score = b_score

    @staticmethod
    def from_dict(score_dict: dict[Color, int]) -> Score:
        w_score = score_dict[Color.white]
        b_score = score_dict[Color.black]
        return Score(w_score, b_score)

    def __str__(self) -> str:
        return f'black: {self.b_score}, white: {self.w_score}'

    def __repr__(self) -> str:
        return self.__str__()

    def __add__(self, other) -> Score:
        if not isinstance(other, Score):
            raise TypeError(f"Can't add object of type {type(other)} to score")
        return Score(self.w_score + other.w_score, self.b_score + other.b_score)


class GameResult(Score):
    @property
    def winner(self) -> Color:
        if self.b_score > self.w_score:
            return Color.black
        return Color.white

    @property
    def winning_margin(self) -> int:
        return abs(self.b_score - self.w_score)

    def __str__(self) -> str:
        if self.b_score > self.w_score:
            return 'B+%.1f' % (self.b_score - self.w_score)
        return 'W+%.1f' % (self.w_score - self.b_score)


class Territory:
    def __init__(self, territory_map: dict[Point, Color | str]):  # <1>
        self.num_black_territory = 0
        self.num_white_territory = 0
        self.num_black_stones = 0
        self.num_white_stones = 0
        self.num_dame = 0
        self.dame_points = []
        self.white_territory = set()
        self.black_territory = set()
        for point, status in territory_map.items():  # <2>
            if status == Color.black:
                self.num_black_stones += 1
            elif status == Color.white:
                self.num_white_stones += 1
            elif status == 'territory_black':
                self.num_black_territory += 1
                self.black_territory.add(point)
            elif status == 'territory_white':
                self.num_white_territory += 1
                self.white_territory.add(point)
            elif status == 'dame':
                self.num_dame += 1
                self.dame_points.append(point)


def _get_color(board: Board, point: Point):
    color = board.get_color(point)
    if color is None:
        return None
    group = board.get_group(point)
    if group.is_dead:
        return None
    return color


def evaluate_territory(board: Board) -> Territory:
    status = {}
    for r in range(1, board.num_rows + 1):
        for c in range(1, board.num_cols + 1):
            p = Point(row=r, col=c)
            if p in status:
                continue
            color = _get_color(board, p)
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


def _collect_region(start_point: Point, board: Board, visited: set[Point] = None) -> tuple[list[Point], set[Color]]:
    if visited is None:
        visited = set()
    if start_point in visited:
        return [], set()

    all_points = [start_point]
    all_borders = set()
    visited.add(start_point)
    start_color = _get_color(board, start_point)
    for neighbor in start_point.neighbors():
        if not board.is_on_grid(neighbor):
            continue
        neighbor_color = _get_color(board, neighbor)
        if neighbor_color == start_color:
            points, borders = _collect_region(neighbor, board, visited)
            all_points += points
            all_borders |= borders
        else:
            all_borders.add(neighbor_color)
    return all_points, all_borders


def get_territory(game_state: State) -> Territory:
    return evaluate_territory(game_state.board)


def compute_game_result(game_state: State) -> GameResult:
    territory = evaluate_territory(game_state.board)
    return GameResult(
        b_score=territory.num_black_territory + territory.num_black_stones,
        w_score=territory.num_white_territory + territory.num_white_stones)
