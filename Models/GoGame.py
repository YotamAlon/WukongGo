from peewee import Model, ForeignKeyField
from Models.Board import Board
from Models import db_proxy
from dlgo.goboard import Move


class GoGame(Model):
    # players = ManyToManyField(Player) - provided by backref from Player
    board = ForeignKeyField(Board, backref='go_game')

    class Meta:
        database = db_proxy

    def resign(self):
        move = Move(is_resign=True)
        self.board.state.apply_move(move)
