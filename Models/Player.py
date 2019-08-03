from peewee import Model, ForeignKeyField, CharField
from Models.User import User
from Models.State import State
from Models import db_proxy


class Player(Model):
    user = ForeignKeyField(User)
    go_game = ForeignKeyField(State, backref='players')
    color = CharField()

    class Meta:
        database = db_proxy
