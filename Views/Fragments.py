from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty
from kivy.lang import Builder
Builder.load_file("kv/Fragments.kv")


class ConfirmPopup(GridLayout):
    text = StringProperty()
    answer_func = None

    def __init__(self, **kwargs):
        self.register_event_type('on_answer')
        super(ConfirmPopup, self).__init__(**kwargs)

    def on_answer(self, *args):
        if self.answer_func is not None:
            self.answer_func(*args)
