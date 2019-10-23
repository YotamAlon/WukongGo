from kivy.uix.screenmanager import Screen
from kivy.lang import Builder


class SettingsScreen(Screen):

    def __init__(self, **kwargs):
        Builder.load_file("kv/Settings.kv")
        super(SettingsScreen, self).__init__(name=kwargs['name'])
