from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from Views.Game import GameScreen
from Views.Menu import MenuScreen
from Models import db_proxy
from Models.BasicTypes import Move
from Models.Game import Game
from Models.User import User
from Models.Timer import Timer
from Models.Player import Player
from peewee import SqliteDatabase
from Models.BasicTypes import Point
from Models.Board import Board
from Models.State import State
from dlgo.rules import get_japanese_rule_set

# this import will be removed
from dlgo.scoring import compute_game_result


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
        db.create_tables([Move, Game, User, Timer, Player])
        # Secondary tables
#        db.create_tables([Game.users.get_through_model()])
        db.close()

    def start_new_game(self):
        users = [User.get_or_create(token='player1')[0], User.get_or_create(token='player2')[0]]
        timer = Timer.create()
        board = Board.create(num_rows=9, num_cols=9, size=9)
        go_game = State.create(board=board)
        players = [Player.create(user=users[0], go_game=go_game, color='black'),
                   Player.create(user=users[1], go_game=go_game, color='white')]
        self.game = Game.new_game(size=9, rule_set=get_japanese_rule_set(), users=users, timer=timer)
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
        print("legal move: pass, current score:", self.game.go_game.board.score)
        if self.game.go_game.board.state.is_over():
            game_res = compute_game_result(self.game.go_game.board.state)
            print(game_res)

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
