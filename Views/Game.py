from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.properties import NumericProperty, StringProperty, ObjectProperty, ListProperty
from kivy.uix.gridlayout import GridLayout
from dlgo.gotypes import Point
from kivy.lang import Builder
from Views.Fragments import NotifyPopup


class Piece(Button):
    index = ListProperty(None)
    img = StringProperty('assets/blank.png')
    board_size = NumericProperty(None)

    def place_piece(self, color):
        if color is None:
            self.img = 'assets/blank.png'
        else:
            self.img = 'assets/' + str(color) + '.png'


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


class GameScreen(Screen):
    board_container = ObjectProperty(None)
    board = ObjectProperty(None)
    score = StringProperty('0 - 0')

    def __init__(self, **kwargs):
        Builder.load_file("kv/Game.kv")
        super(GameScreen, self).__init__(name=kwargs['name'])

    def initialize(self, game):
        self.board = GameBoard(game.go_game.board.size)
        self.board_container.add_widget(self.board)

    def update_score(self, score):
        self.score = f'{score.black_score} - {score.white_score}'

    def update_board(self, board):
        self.board.update(board)

    @staticmethod
    def show_illegal_move_popup(point):
        NotifyPopup(title='This is not a legal move!',
                    text=f'the move {point[0]}, {point[1]} is not a legal move').open()

    def handle_click(self, signal):
        self.manager.handle_click(signal)
