from kivy.uix.popup import Popup
from kivy.properties import StringProperty, ObjectProperty
from kivy.lang import Builder
from kivy.graphics import Color, Line
Builder.load_file("kv/Fragments.kv")


class ConfirmPopup(Popup):
    text = StringProperty()
    callback = ObjectProperty(print)

    def __init__(self, **kwargs):
        super(ConfirmPopup, self).__init__(**kwargs)

    def answer(self, confirmed):
        if confirmed:
            self.callback()
        self.dismiss()


class NotifyPopup(Popup):
    text = StringProperty()

    def __init__(self, **kwargs):
        super(NotifyPopup, self).__init__(**kwargs)

    def ok(self):
        self.dismiss()


def do_border(obj):
    with obj.canvas.before:
        Color(rgba=(.5, .5, .5, 1))
        Line(width=2, rectangle=(obj.x, obj.y, obj.width, obj.height))
