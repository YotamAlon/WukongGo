from peewee import Model, IntegerField, TextField
from Models import db


class Board(Model):
    size = IntegerField()
    state = TextField()
    # history = ManyToManyField(Move) - provided by backref from Move

    class Meta:
        database = db
