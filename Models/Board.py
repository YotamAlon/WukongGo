from peewee import Model, IntegerField, TextField


class Board(Model):
    size = IntegerField()
    state = TextField()
    # history = ManyToManyField(Move) - provided by backref from Move
