from peewee import Model, ForeignKeyField
from Models.Board import Board
from Models import db


class GoGame(Model):
    # players = ManyToManyField(Player) - provided by backref from Player
    board = ForeignKeyField(Board, backref='go_game')

    class Meta:
        database = db