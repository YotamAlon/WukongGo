from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
Builder.load_file("kv/Menu.kv")


class MenuScreen(Screen):
    def handle_click(self, signal):
        self.manager.handle_click(signal)
