from peewee import Model, ForeignKeyField, ManyToManyField
from Models.User import User
from Models.Timer import Timer
from Models.GoGame import GoGame
from Models import db_proxy


class Game(Model):
    users = ManyToManyField(User, backref='games')
    timer = ForeignKeyField(Timer, backref='game')
    go_game = ForeignKeyField(GoGame, backref='game')

    class Meta:
        database = db_proxy


GameUser = Game.users.get_through_model()
