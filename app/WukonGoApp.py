import asyncio
from functools import wraps

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager
from peewee import SqliteDatabase

from Models import db_proxy
from Models.BasicTypes import Color
from Models.BasicTypes import Point
from Models.Game import Game
from Models.Rule import get_japanese_rule_set
from Models.Scoring import GameResult
from Models.Timer import Timer
from Models.User import User
from app.Views.Game import GameScreen, GameMode
from app.Views.Menu import MenuScreen
from app.Views.Settings import SettingsScreen


def run_async(func):
    @wraps(func)
    def inner(*args, **kwargs):
        return asyncio.create_task(func(*args, **kwargs))

    return inner


# class API(socketio.AsyncClient):
#     @run_async
#     async def connect(self):
#         await super(API, self).connect('http://wukongo.ddns.net:5000')
#
#     @run_async
#     async def send_move(self, game: Game, move: Move):
#         await super(API, self).emit('move_made', {'move_sgf': move.sgf_str, 'game_uuid': game.uuid})
#
#     @run_async
#     async def start_game(self, game: Game):
#         await super(API, self).emit('game_started', {'game_sgf': game.sgf_str})
#
#     @run_async
#     async def disconnect(self):
#         await super(API, self).disconnect()


class Controller(ScreenManager):
    game = None
    # api = API()
    black_name = StringProperty('Black')
    white_name = StringProperty('White')

    async def initialize(self):
        self.initialize_db()

        # self.api.connect()

        self.add_widget(MenuScreen(name='menu'))
        self.add_widget(GameScreen(name='game'))
        self.add_widget(SettingsScreen(name='settings'))

        self.switch_to(self.get_screen('menu'))

    @staticmethod
    def initialize_db():
        db = SqliteDatabase('wukongo.db')
        db_proxy.initialize(db)

    def start_new_game(self):
        users = [User.get_or_create(display_name=self.black_name, defaults={'token': '1'})[0],
                 User.get_or_create(display_name=self.white_name, defaults={'token': '2'})[0]]
        timer = Timer()
        players = {Color.black: users[0], Color.white: users[1]}
        self.game = Game.new_game(size=9, rule_set=get_japanese_rule_set(), players=players, timer=timer)
        self.game.save()
        # self.api.start_game(self.game)
        return self.game

    def process_move(self, index):
        point = Point(*index)
        game_screen = self.get_screen('game')
        if game_screen.mode == GameMode.play:
            if self.game.is_legal(point):
                move, result = self.game.make_move(point=point)
                # self.api.send_move(self.game, move)
                if isinstance(result, GameResult):
                    game_screen.show_game_finished_popup(result)
                else:
                    game_screen.update_board(self.game.state.board)
                    game_screen.update_score(self.game.score)
                    print("legal move:", point, "current score:", self.game.score)

            else:
                game_screen.show_illegal_move_popup(point)
                print("illegal move: ", point, "current score:", self.game.score)
        else:
            dead = self.game.mark_dead_stone(point)
            if dead is not None:
                black_points, white_points = self.game.get_black_white_points()
                game_screen.update_endgame(dead, black_points, white_points)
            game_screen.update_score(self.game.score)

    def pass_turn(self):
        # print(f'\n{self.game.to_sgf()}\n') This is currently not working
        move, result = self.game.pass_turn()
        print("legal move: pass, current score:", result)
        if result:
            self.get_screen('game').initiate_endgame(*self.game.get_black_white_points())
            # self.get_screen('game').show_game_finished_popup(result)

    def resign(self):
        result = self.game.resign()
        self.get_screen('game').show_game_finished_popup(result)
        print('you have resigned')

    # @staticmethod
    # @api.event
    # def receive_move(move_sgf):
    #     print(Move.from_sgf(move_sgf))

    def navigate(self, signal):
        self.transition.duration = 0.4
        if signal == 'game':
            game = self.start_new_game()
            self.get_screen('game').initialize(game)
            self.transition.direction = 'down'
            self.current = 'game'

        elif signal == 'menu':
            if self.current == 'game':
                self.transition.direction = 'up'
            elif self.current == 'settings':
                self.transition.direction = 'down'
            self.current = 'menu'

        elif signal == 'settings':
            self.transition.direction = 'up'
            self.current = 'settings'

    def change_player_name(self, player_id, name):
        if player_id == 0:
            self.get_screen('game').player_1_label.text = name
        else:
            self.get_screen('game').player_2_label.text = name


class WukonGoApp(App):
    controller = Controller()

    def build(self):
        Window.size = (400, 600)
        return self.controller

    async def run(self):
        await self.controller.initialize()
        await self.async_run()


if __name__ == "__main__":
    Clock.init_async_lib('asyncio')
    app = WukonGoApp()
    asyncio.run(app.run())
