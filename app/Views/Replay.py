from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import Screen

from Models.Game import Game
from Models.State import State
from app.Views.GameBoard import GameBoard
from app.dispatcher import Dispatcher


class ReplayScreen(Screen):
    game_state: State = ObjectProperty(None)
    board_container = ObjectProperty(None)
    board: GameBoard = ObjectProperty(None)
    score = StringProperty('0 - 0')

    def initialize(self, game: Game):
        self.game_state = game.state
        self.board = GameBoard(game.size)
        self.board_container.add_widget(self.board)
        Dispatcher.subscribe_to_event('replay_previous', self.go_to_previous_game_state)
        Dispatcher.subscribe_to_event('replay_next', self.go_to_next_game_state)

    def update_score(self, score):
        self.score = f'{score.b_score} - {score.w_score}'

    def on_game_state(self):
        self.board.update(self.game_state.board)

    def go_to_previous_game_state(self):
        if self.game_state.previous_state:
            self.game_state = self.game_state.previous_state

    def go_to_next_game_state(self):
        if self.game_state.next_state:
            self.game_state = self.game_state.next_state
