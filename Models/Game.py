from Models.State import State
from Models.BasicTypes import Move, Point, Color
from Models.SGF import SGF
from Models.Rule import get_rule_set_by_name, RuleSet
from Models.Player import Player
from Models.User import User
from Models.Timer import Timer
from peewee import Model, ForeignKeyField, IntegerField, CharField, FloatField
from typing import Dict, List
from Models import db_proxy


class Game(Model):
    black = ForeignKeyField(User)
    white = ForeignKeyField(User)
    size = IntegerField()
    rule_set_name = CharField()
    komi = FloatField()

    class Meta:
        db = db_proxy

    def __init__(self, players: Dict[Color, User], timer, state: State, rule_set: RuleSet):
        super(Game, self).__init__()
        self.players = players
        self.timer = timer
        self.state = state
        self.rule_set = rule_set.name
        self.komi = rule_set.komi.w_score

    @property
    def players(self) -> Dict[Color, User]:
        return {Color.black: self.black, Color.white: self.white}

    @players.setter
    def players(self, value: Dict[Color, User]) -> None:
        self.black = value[Color.black]
        self.white = value[Color.white]

    @property
    def rule_set(self) -> RuleSet:
        return get_rule_set_by_name(self.rule_set_name)

    @rule_set.setter
    def rule_set(self, value: RuleSet) -> None:
        self.rule_set_name = value.name

    @property
    def users(self) -> List[User]:
        return list(GameUser.select(GameUser.user).where(GameUser.game == self))

    # This should probably not be used, but it's here as an example
    # @users.setter
    # def users(self, value: List[User]) -> None:
    #     GameUser.insert_many([{'game': self, 'user': user} for user in value]).on_conflict_ignore()

    @classmethod
    def new_game(cls, size, rule_set, players, timer):
        state = State.new_game(size, rule_set)
        return Game(players, timer, state, rule_set)

    def is_legal(self, point):
        assert isinstance(point, Point)
        move = Move.play(point)
        return self.state.is_valid_move(move)

    def make_move(self, point):
        return self._make_move(Move.play(point))

    def _make_move(self, move):
        self.state = self.state.apply_move(move)
        if self.state.is_over():
            return self.state.get_game_result()

    def pass_turn(self):
        return self._make_move(Move.pass_turn())

    def resign(self):
        return self._make_move(Move.resign())

    def to_sgf(self):
        return SGF(self)

    @staticmethod
    def _from_sgf(sgf):
        assert isinstance(sgf, SGF)
        size = sgf.header['SZ']
        rules = get_rule_set_by_name(sgf.header['RU'])
        players = {Color.black: Player(User(sgf.header['BP'], 1), Color.black),
                   Color.white: Player(User(sgf.header['WP'], 2), Color.white)}
        game = Game.new_game(size, rules, players, Timer())

        for move in sgf.moves:
            game.make_move(Move.from_sgf(move[game.state.next_color.sgf_str]))
        return game

    @staticmethod
    def from_sgf(sgf_string):
        sgf = SGF.from_string(sgf_string)
        return Game._from_sgf(sgf)

    @property
    def score(self):
        return self.state.score

    @property
    def grid(self):
        return self.state.board.grid

    def get_black_white_points(self):
        # return {Point(1, 1)}, {Point(2, 2)}
        self.state.change_dead_stone_marking(None)
        return self.state.territory.black_territory, self.state.territory.white_territory

    def mark_dead_stone(self, point):
        # actually changes a group of stones from dead to alive and vice versa.
        return self.state.change_dead_stone_marking(point)


class GameUser(Model):
    game = ForeignKeyField(Game)
    user = ForeignKeyField(User)

    class Meta:
        db = db_proxy
        indexes = ((('game', 'user'), True), )


class GameMove(Model):
    game = ForeignKeyField(Game)
    move = ForeignKeyField(Move)

    class Meta:
        db = db_proxy
        indexes = ((('game', 'move'), True), )
