from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.properties import NumericProperty, StringProperty, ObjectProperty, ListProperty
from kivy.uix.gridlayout import GridLayout
from dlgo.gotypes import Point
from dlgo.goboard import Move, GameState
from dlgo.rules import get_ai_rule_set


class Piece(Button):
    index = ListProperty(None)
    img = StringProperty('assets/blank.png')
    board_size = NumericProperty(None)

    def place_piece(self, color):
        if color is None:
            self.img = 'assets/blank.png'
        else:
            self.img = 'assets/' + str(color) + '.png'

    def on_press(self):
        point = Point(self.index[0], self.index[1])
        if self.parent.is_move_legal(point):
            self.parent.make_move(point)
            print("legal move: ", point)
        else:
            print("illegal move: ", point)


class GameBoard(GridLayout):
    def __init__(self, **kwargs):
        super(GameBoard, self).__init__(**kwargs)

        self.board_size = 9
        self.game_state = GameState.new_game(self.board_size, get_ai_rule_set())
        self.grid = {}
        for i in range(1, self.board_size + 1):
            for j in range(1, self.board_size + 1):
                point = Point(i, j)
                self.grid[point] = Piece(index=point, board_size=self.board_size)
                self.add_widget(self.grid[point])

    def is_move_legal(self, point):
        move = Move.play(point)
        return self.game_state.is_valid_move(move)

    def make_move(self, point):
        move = Move.play(point)
        self.game_state = self.game_state.apply_move(move)
        for move in self.game_state.board.get_grid():
            self.grid[move[0]].place_piece(move[1])
        return None


class GameScreen(Screen):
    board = ObjectProperty(None)

    def handle_click(self, signal):
        self.manager.handle_click(signal)
