from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from Views.Game import GameScreen
from Views.Menu import MenuScreen
from Models import db_proxy
from Models.Move import Move
from Models.Game import Game
from Models.User import User
from Models.Timer import Timer
from Models.Board import Board
from Models.GoGame import GoGame
from Models.Player import Player
from peewee import SqliteDatabase
from dlgo.gotypes import Point


class Controller(ScreenManager):
    def __init__(self):
        super(Controller, self).__init__()

    def initialize(self):
        self.add_widget(MenuScreen(name='menu'))
        self.add_widget(GameScreen(name='game'))

        self.initialize_db()

        self.switch_to(self.get_screen('menu'))

    @staticmethod
    def initialize_db():
        db = SqliteDatabase('WukonGo.db')
        db_proxy.initialize(db)
        db.connect()
        # Main tables
        db.create_tables([Move, Game, User, Timer, Board, GoGame, Player])
        # Secondary tables
        db.create_tables([Game.users.get_through_model()])
        db.close()

    def start_new_game(self):
        users = [User.get_or_create(token='player1')[0], User.get_or_create(token='player2')[0]]
        timer = Timer.create()
        board = Board.create(size=9)
        go_game = GoGame.create(board=board)
        players = [Player.create(user=users[0], go_game=go_game, color='black'),
                   Player.create(user=users[1], go_game=go_game, color='white')]
        self.game = Game.create(timer=timer, go_game=go_game)
        self.game.users = users
        self.players = players
        return self.game

    def process_move(self, index):
        point = Point(*index)
        if self.game.go_game.board.is_move_legal(point):
            self.game.go_game.board.make_move(point=point)
            self.get_screen('game').update_board(self.game.go_game.board)
            self.get_screen('game').update_score(self.game.go_game.board.score)
            print("legal move:", point, "current score:", self.game.go_game.board.score)

        else:
            self.get_screen('game').show_illegal_move_popup(point)
            print("illegal move: ", point, "current score:", self.game.go_game.board.score)

    def pass_turn(self):
        self.game.go_game.board.make_move(None, is_pass=True)

    def resign(self):
        self.game.go_game.resign()
        print('you have resigned')

    def handle_click(self, signal):
        if signal == 'new_game_please':
            game = self.start_new_game()
            self.get_screen('game').initialize(game)
            self.switch_to(self.get_screen('game'))

        elif signal == 'back_to_menu':
            self.switch_to(self.get_screen('menu'), direction='right')


class WukonGoApp(App):
    controller = Controller()

    def __init__(self):
        super(WukonGoApp, self).__init__()
        self.controller.initialize()

    def build(self):
        return self.controller


if __name__ == "__main__":
    app = WukonGoApp()
    app.run()
