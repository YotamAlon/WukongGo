from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.uix.gridlayout import GridLayout


class Piece(Button):
    index = NumericProperty(None)
    img = StringProperty(None)

    def place_piece(self, color):
        self.img = 'assets/' + color + '.png'

    def on_press(self):
        if self.parent.is_move_legal(self.index):
            color = self.parent.make_move(self.index)
            self.place_piece(color)


class MenuScreen(Screen):
    def handle_click(self, signal):
        self.manager.handle_click(signal)


class GameBoard(GridLayout):
    board_size = NumericProperty(19)
    current_player = StringProperty('black')

    def __init__(self, **kwargs):
        super(GameBoard, self).__init__(**kwargs)
        for i in range(self.board_size ** 2):
            self.add_widget(Piece(index=i))

    def is_move_legal(self, index):
        return True

    def make_move(self, move):
        if self.current_player == 'black':
            self.current_player = 'white'
            return 'white'
        else:
            self.current_player = 'black'
            return 'black'


class GameScreen(Screen):
    board = ObjectProperty(None)

    def handle_click(self, signal):
        self.manager.handle_click(signal)
