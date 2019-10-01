from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
from Views.Game import GameScreen
from Views.Menu import MenuScreen
from Models.BasicTypes import Color
from Views.Settings import SettingsScreen
from Models.Game import Game
from Models.User import User
from Models.Timer import Timer
from Models.Player import Player
from Models.BasicTypes import Point
from Models.Rule import get_japanese_rule_set
from Models.Scoring import GameResult


class Controller(ScreenManager):
    def __init__(self):
        super(Controller, self).__init__()
        self.game = None

    def initialize(self):
        self.add_widget(MenuScreen(name='menu'))
        self.add_widget(GameScreen(name='game'))
        self.add_widget(SettingsScreen(name='settings'))

        self.initialize_db()

        self.switch_to(self.get_screen('menu'))

    @staticmethod
    def initialize_db():
        pass

    def start_new_game(self):
        users = [User(1, 1), User(2, 2)]
        timer = Timer()
        players = {Color.black: Player(users[0], Color.black), Color.white: Player(users[1], Color.white)}
        self.game = Game.new_game(size=9, rule_set=get_japanese_rule_set(), players=players, timer=timer)
        return self.game  # a bit weird, why are we assigning it to self and returning it? one should be enough.

    def process_move(self, index):
        point = Point(*index)
        game_screen = self.get_screen('game')
        if game_screen.mode == 'play':
            if self.game.is_legal(point):
                result = self.game.make_move(point=point)
                if isinstance(result, GameResult):
                    game_screen.show_game_finished_popup(result)
                else:
                    game_screen.update_board(self.game.state.board)
                    game_screen.update_score(self.game.state.score)
                    print("legal move:", point, "current score:", self.game.state.score)

            else:
                game_screen.show_illegal_move_popup(point)
                print("illegal move: ", point, "current score:", self.game.state.score)
        else:
            dead = self.game.mark_dead_stone(point)
            if dead is not None:
                black_points, white_points = self.game.get_black_white_points()
                game_screen.update_endgame(dead, black_points, white_points)

    def pass_turn(self):
        # print(f'\n{self.game.to_sgf()}\n') This is currently not working
        result = self.game.pass_turn()
        print("legal move: pass, current score:", result)
        if isinstance(result, GameResult):
            self.get_screen('game').initiate_endgame(*self.game.get_black_white_points())
            # self.get_screen('game').show_game_finished_popup(result)

    def resign(self):
        result = self.game.resign()
        self.get_screen('game').show_game_finished_popup(result)
        print('you have resigned')

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

    def __init__(self):
        super(WukonGoApp, self).__init__()
        self.controller.initialize()

    def build(self):
        Window.size = (400, 600)
        return self.controller


if __name__ == "__main__":
    app = WukonGoApp()
    app.run()
