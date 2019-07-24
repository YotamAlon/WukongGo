from kivy.uix.popup import Popup
from kivy.properties import StringProperty, ObjectProperty
from kivy.lang import Builder
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
