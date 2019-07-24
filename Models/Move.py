from peewee import Model, ForeignKeyField, CharField
from Models.Board import Board
from Models.Player import Player
from Models import db


class Move(Model):
    board = ForeignKeyField(Board, backref='history')
    player = ForeignKeyField(Player, backref='moves')
    point = CharField()

    class Meta:
        database = db