from peewee import Model, ForeignKeyField, CharField
from Models.User import User
from Models.GoGame import GoGame


class Player(Model):
    user = ForeignKeyField(User)
    go_game = ForeignKeyField(GoGame, backref='players')
    color = CharField()
