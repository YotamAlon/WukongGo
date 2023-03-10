from kivy.graphics import Color, Line
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.popup import Popup

Builder.load_file("kv/Fragments.kv")


class ConfirmPopup(Popup):
    text = StringProperty()
    callback = ObjectProperty(print)


class NotifyPopup(Popup):
    text = StringProperty()


class BoardSizeChoicePopup(Popup):
    callback = ObjectProperty(print)


def do_border(obj):
    with obj.canvas.before:
        Color(rgba=(.5, .5, .5, 1))
        Line(width=2, rectangle=(obj.x, obj.y, obj.width, obj.height))
