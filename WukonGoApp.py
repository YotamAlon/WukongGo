from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from Views import MenuScreen, GameScreen
from kivy.lang import Builder
Builder.load_file("WukonGo.kv")


class ScreenRouter(ScreenManager):
    def handle_click(self, signal):
        if signal == 'new_game_please':
            self.transition.direction = 'left'
            self.current = 'game'

        elif signal == 'back_to_menu':
            self.transition.direction = 'right'
            self.current = 'menu'


class WukonGoApp(App):
    def __init__(self):
        super(WukonGoApp, self).__init__()
        self.screen_manager = ScreenRouter()
        self.screen_manager.add_widget(MenuScreen(name='menu'))
        self.screen_manager.add_widget(GameScreen(name='game'))

    def build(self):
        return self.screen_manager


if __name__ == "__main__":
    WukonGoApp().run()
