from peewee import Model, ForeignKeyField, CharField
from Models.Board import Board


class Move(Model):
    board = ForeignKeyField(Board, backref='history')
    point = CharField()
