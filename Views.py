from kivy.uix.screenmanager import Screen


class MenuScreen(Screen):
    def handle_click(self, signal):
        self.manager.handle_click(signal)


class GameScreen(Screen):
    def handle_click(self, signal):
        self.manager.handle_click(signal)
