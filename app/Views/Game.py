from __future__ import annotations
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.properties import NumericProperty, StringProperty, ObjectProperty, ListProperty, BooleanProperty, AliasProperty
from kivy.uix.gridlayout import GridLayout
from Models.BasicTypes import Point, Color
from kivy.lang import Builder
from app.Views.Fragments import NotifyPopup
from kivy.graphics import Color as kColor, Rectangle, InstructionGroup


def get_horizontal_line_points(piece: Piece) -> tuple[int, int, int, int]:
    startx = piece.pos[0] + (piece.size[0] / 2 if piece.index[1] == 1 else 0)
    starty = piece.pos[1] + (piece.size[1] / 2)
    finalx = piece.pos[0] + piece.size[0] / (2 if piece.index[1] == piece.board_size else 1)
    finaly = piece.pos[1] + (piece.size[1] / 2)
    return startx, starty, finalx, finaly


def get_vertical_line_points(piece: Piece) -> tuple[int, int, int, int]:
    startx = piece.pos[0] + (piece.size[0] / 2)
    starty = piece.pos[1] + (piece.size[1] / 2 if piece.index[0] == piece.board_size else 0)
    finalx = piece.pos[0] + (piece.size[0] / 2)
    finaly = piece.pos[1] + piece.size[1] / (2 if piece.index[0] == 1 else 1)
    return startx, starty, finalx, finaly


class Piece(Button):
    index = ListProperty(None)
    color = StringProperty('blank')
    board_size = NumericProperty(None)
    is_dead = BooleanProperty(False)
    horizontal_line_points = AliasProperty(get_horizontal_line_points, None, cache=True, bind=['pos', 'size'])
    vertical_line_points = AliasProperty(get_vertical_line_points, None, cache=True, bind=['pos', 'size'])
    marker = None

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

    def update(self, board):
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


class GameScreen(Screen):
    mode = StringProperty('play')
    board_container = ObjectProperty(None)
    board = ObjectProperty(None)
    score = StringProperty('0 - 0')
    player_names = ['Player 1', 'Player 2']

    def __init__(self, **kwargs):
        Builder.load_file("kv/Game.kv")
        super(GameScreen, self).__init__(name=kwargs['name'])

    def initialize(self, game):
        self.board = GameBoard(game.size)
        self.board_container.add_widget(self.board)

    def update_score(self, score):
        self.score = f'{score.b_score} - {score.w_score}'

    def update_board(self, board):
        self.board.update(board)

    def initiate_endgame(self, black_points=None, white_points=None):
        self.mode = 'count'
        self.board.update_point_markers(black_points, white_points)

    def update_endgame(self, dead_points=None, black_points=None, white_points=None):
        self.board.update_dead_points(dead_points)
        self.board.update_point_markers(black_points, white_points)

    @staticmethod
    def show_illegal_move_popup(point):
        NotifyPopup(title='This is not a legal move!',
                    text=f'the move {point[0]}, {point[1]} is not a legal move').open()

    def show_game_finished_popup(self, result):
        winner = 'Black' if result.winner == Color.black else 'White'
        NotifyPopup(title='Game is finished!', text=f'The winner is {winner}.\nThe final score is '
                                                    f'Black - {result.b_score} and White - {result.w_score}',
                    on_dismiss=lambda _: self.manager.navigate('menu')).open()
