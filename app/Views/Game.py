from __future__ import annotations

import enum

from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, OptionProperty
from kivy.uix.screenmanager import Screen

from Models.BasicTypes import Color
from app.Views.Fragments import NotifyPopup
from app.Views.GameBoard import GameBoard


class GameMode(enum.Enum):
    play = 'play'
    count = 'count'


class GameScreen(Screen):
    mode = OptionProperty(defaultvalue=GameMode.play, options=list(GameMode))
    board_container = ObjectProperty(None)
    board = ObjectProperty(None)
    score = StringProperty('0 - 0')
    player_names = ['Player 1', 'Player 2']

    def __init__(self, **kwargs):
        Builder.load_file("kv/Game.kv")
        super(GameScreen, self).__init__(name=kwargs['name'])

    def initialize(self, game):
        self.mode = GameMode.play
        self.board = GameBoard(game.size)
        self.board_container.add_widget(self.board)

    def update_score(self, score):
        self.score = f'{score.b_score} - {score.w_score}'

    def update_board(self, board):
        self.board.update(board)

    def initiate_endgame(self, black_points=None, white_points=None):
        self.mode = GameMode.count
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
