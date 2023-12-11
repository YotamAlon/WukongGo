import typing
import uuid

from peewee import Model, ForeignKeyField, IntegerField, CharField, FloatField, TextField

from Models import db_proxy
from Models.BasicTypes import Move, Point, Color
from Models.Rule import get_rule_set_by_name, RuleSet, RuleSetType
from Models.SGF import SGF
from Models.Scoring import GameResult, Score
from Models.State import State
from Models.Timer import Timer
from Models.User import User


class Game(Model):
    uuid = CharField()
    black = ForeignKeyField(User)
    white = ForeignKeyField(User)
    size = IntegerField()
    rule_set_name = CharField()
    komi = FloatField()
    _sgf = TextField()

    class Meta:
        database = db_proxy

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not hasattr(self, 'state'):

    def save(self, **kwargs):
        if self.uuid is None:
            self.uuid = str(uuid.uuid4())
        super(Game, self).save(**kwargs)
        GameUser(game=self, user=self.black).save()
        GameUser(game=self, user=self.white).save()

    @property
    def players(self) -> dict[Color, User]:
        return {Color.black: self.black, Color.white: self.white}

    @players.setter
    def players(self, value: dict[Color, User]) -> None:
        self.black = value[Color.black]
        self.white = value[Color.white]

    @property
    def rule_set(self) -> RuleSet:
        return get_rule_set_by_name(RuleSetType(self.rule_set_name))

    @rule_set.setter
    def rule_set(self, value: RuleSet) -> None:
        self.rule_set_name = value.name
        self.komi = value.komi.w_score

    @property
    def users(self) -> list[User]:
        return [self.black, self.white]

    # This should probably not be used, but it's here as an example
    # @users.setter
    # def users(self, value: List[User]) -> None:
    #     GameUser.insert_many([{'game': self, 'user': user} for user in value]).on_conflict_ignore()

    @classmethod
    def new_game(
        cls,
        size: int,
        rule_set: RuleSet,
        players: dict[Color, User],
        timer: Timer,
        uuid: str | None = None,
    ) -> typing.Self:
        state = State.new_game(size, rule_set.komi)
        return Game(
            black=players[Color.black],
            white=players[Color.white],
            state=state,
            timer=timer,
            rule_set=rule_set,
            size=size,
            uuid=uuid,
            komi=rule_set.komi,
        )

    def is_legal(self, point: Point) -> bool:
        move = Move.play(point)
        return self.rule_set.is_valid_move(game_state=self.state, color=self.state.next_color, move=move)

    def make_move(self, point: Point) -> tuple[Move, GameResult | None]:
        return self._make_move(Move.play(point))

    def _make_move(self, move: Move) -> tuple[Move, Optional[GameResult]]:

        GameMove(move=move, game=self).save()
        self.state = self.state.apply_move(move)
        if self.state.is_over():
            return move, self.state.get_game_result()
        return move, None

    def pass_turn(self) -> tuple[Move, GameResult | None]:
        return self._make_move(Move.pass_turn())

    def resign(self) -> tuple[Move, GameResult | None]:
        return self._make_move(Move.resign())

    def to_sgf(self) -> SGF:
        return SGF(self)

    @property
    def sgf(self) -> SGF:
        return SGF.from_string(self._sgf)

    @sgf.setter
    def sgf(self, value: SGF) -> None:
        self._sgf = str(value)

    @property
    def sgf_str(self) -> str:
        return str(self.to_sgf())

    @classmethod
    def _from_sgf(cls, sgf: SGF) -> typing.Self:
        uuid = sgf.header.get("UD", None)
        size = sgf.header["SZ"]
        rules = get_rule_set_by_name(RuleSetType(sgf.header["RU"]))
        players = {
            Color.black: User.get_or_create(display_name=sgf.header["BP"], defaults={"token": "1"})[0],
            Color.white: User.get_or_create(display_name=sgf.header["WP"], defaults={"token": "2"})[0],
        }
        game = cls.new_game(int(size), rules, players, Timer(), uuid=uuid)

        for move in sgf.moves:
            game.make_move(Move.from_sgf(move[game.state.next_color.sgf_str]).point)
        return game

    @classmethod
    def from_sgf(cls, sgf_string: str) -> typing.Self:
        sgf = SGF.from_string(sgf_string)
        return cls._from_sgf(sgf)

    @property
    def score(self) -> Score:
        return self.state.score

    @property
    def grid(self) -> list[tuple[Point, Color]]:
        return self.state.board.grid

    def get_black_white_points(self) -> tuple[set[Point], set[Point]]:
        self.state.change_dead_stone_marking(None)
        return (
            self.state.territory.black_territory,
            self.state.territory.white_territory,
        )

    def mark_dead_stone(self, point: Point) -> list[Point]:
        # actually changes a group of stones from dead to alive and vice versa.
        return self.state.change_dead_stone_marking(point)
