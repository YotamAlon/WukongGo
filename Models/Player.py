from peewee import ForeignKeyField, CharField
from Models.User import User
from Models.GoGame import GoGame


class Player(User):
    go_game = ForeignKeyField(GoGame, backref='players')
    color = CharField()
