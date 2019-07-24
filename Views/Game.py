from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.properties import NumericProperty, StringProperty, ObjectProperty, ListProperty
from kivy.uix.gridlayout import GridLayout
from dlgo.gotypes import Point
from dlgo.goboard import Move, GameState
from dlgo.rules import get_ai_rule_set, get_japanese_rule_set
from kivy.lang import Builder
from Views.Fragments import NotifyPopup
Builder.load_file("kv/Game.kv")


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
        point = Point(*self.index)
        if self.parent.is_move_legal(point):
            self.parent.make_move(point=point)
            print("legal move:", point, "current score:", self.parent.game_state.score)
        else:
            self.parent.show_illegal_move_popup(point)
            print("illegal move: ", point, "current score:", self.parent.game_state.score)


class GameBoard(GridLayout):
    score = StringProperty('0 - 0')

    def __init__(self, **kwargs):
        super(GameBoard, self).__init__(**kwargs)

        self.board_size = 9
        self.game_state = GameState.new_game(self.board_size, get_japanese_rule_set())
        self.update_score()
        self.grid = {}
        for i in range(1, self.board_size + 1):
            for j in range(1, self.board_size + 1):
                point = Point(i, j)
                self.grid[point] = Piece(index=point, board_size=self.board_size)
                self.add_widget(self.grid[point])

    def update_board(self):
        for move in self.game_state.board.get_grid():
            self.grid[move[0]].place_piece(move[1])

    def update_score(self):
        self.score = f'{self.game_state.score.black_score} - {self.game_state.score.white_score}'

    def is_move_legal(self, point):
        move = Move.play(point)
        return self.game_state.is_valid_move(move)

    def show_illegal_move_popup(self, point):
        NotifyPopup(title='This is not a legal move!',
                    text=f'the move {point[0]}, {point[1]} is not a legal move').open()

    def make_move(self, point=None, is_pass=False, is_resign=False):
        move = Move(point, is_pass=is_pass, is_resign=is_resign)
        self.game_state = self.game_state.apply_move(move)
        self.update_board()
        self.update_score()

    def resign(self):
        move = Move(is_resign=True)
        self.game_state = self.game_state.apply_move(move)
        print('you have resigned')


class GameScreen(Screen):
    board = ObjectProperty(None)

    def handle_click(self, signal):
        self.manager.handle_click(signal)
