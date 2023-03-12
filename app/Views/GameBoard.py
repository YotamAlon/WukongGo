from __future__ import annotations

from kivy.graphics import InstructionGroup, Color as kColor, Rectangle, Line
from kivy.properties import ListProperty, StringProperty, NumericProperty, BooleanProperty
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout

from Models.BasicTypes import Point, Color
from Models.Board import Board


class GameBoard(GridLayout):
    grid = {}
    board_size = 0

    def __init__(self, board_size):
        self.board_size = board_size
        super(GameBoard, self).__init__()
        self.clear_widgets()
        self.grid = {}
        for i in range(1, board_size + 1):
            for j in range(1, board_size + 1):
                point = Point(i, j)
                self.grid[point] = Piece(index=point, board_size=board_size)
                self.add_widget(self.grid[point])

    def on_kv_post(self, base_widget):
        board_lines = InstructionGroup()
        board_lines.add(kColor(0, 0, 0, 1))
        for i in range(self.board_size):
            horizontal_line = HorizontalLine(i)
            self.bind(pos=horizontal_line.update_points, size=horizontal_line.update_points)
            board_lines.add(horizontal_line)

            vertical_line = VerticalLine(i)
            self.bind(pos=vertical_line.update_points, size=vertical_line.update_points)
            board_lines.add(vertical_line)
        self.canvas.add(board_lines)

    def update(self, board: Board):
        for point in board.grid:
            self.grid[point[0]].place_piece(point[1])

    def update_point_markers(self, black_points=None, white_points=None):
        for point, piece in self.grid.items():
            if black_points is not None and point in black_points:
                piece.update_marker(Color.black)
            elif white_points is not None and point in white_points:
                piece.update_marker(Color.white)
            else:
                piece.update_marker(None)

    def update_dead_points(self, dead_points=None):
        for point, piece in self.grid.items():
            piece.is_dead = (dead_points is not None and point in dead_points)


class Piece(Button):
    index = ListProperty(None)
    color = StringProperty('blank')
    board_size = NumericProperty(None)
    is_dead = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.marker = None

    def place_piece(self, color):
        if color is None:
            self.color = 'blank'
        else:
            self.color = str(color)

    def update_marker(self, color):
        if color is None:
            if self.marker is not None:
                self.canvas.remove(self.marker)
        else:
            self.marker = InstructionGroup()
            self.marker.add(kColor(*((0, 0, 0) if color == Color.black else (1, 1, 1))))
            self.marker.add(Rectangle(
                pos=(self.pos[0] + (self.size[0] / 4) * 1.5, self.pos[1] + (self.size[1] / 4) * 1.5),
                size=(self.size[0] / 4, self.size[1] / 4)
            ))
            self.canvas.add(self.marker)


class HorizontalLine(Line):
    def __init__(self, index: int):
        super().__init__()
        self.index = index

    def update_points(self, game_board: GameBoard, _):
        line_margin = game_board.size[0] / game_board.board_size
        edge_margin = line_margin / 2
        self.points = [
            game_board.pos[0] + edge_margin,
            game_board.pos[1] + edge_margin + (line_margin * self.index),
            game_board.pos[0] + game_board.size[0] - edge_margin,
            game_board.pos[1] + edge_margin + (line_margin * self.index),
        ]


class VerticalLine(Line):
    def __init__(self, index: int):
        super().__init__()
        self.index = index

    def update_points(self, game_board: GameBoard, _):
        line_margin = game_board.size[0] / game_board.board_size
        edge_margin = line_margin / 2
        self.points = [
            game_board.pos[0] + edge_margin + (line_margin * self.index),
            game_board.pos[1] + edge_margin,
            game_board.pos[0] + edge_margin + (line_margin * self.index),
            game_board.pos[1] + game_board.size[1] - edge_margin,
        ]
