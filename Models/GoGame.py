from peewee import Model, ForeignKeyField, ManyToManyField
from Models.Board import Board
from Models.Rule import Rule


class GoGame(Model):
    # players = ManyToManyField(Player) - provided by backref from Player
    board = ForeignKeyField(Board, backref='go_game')
    rules = ManyToManyField(Rule)
