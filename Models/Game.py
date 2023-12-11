import dataclasses
import typing
import uuid

from Models.BasicTypes import Move, Point, Color
from Models.Rule import get_rule_set_by_name, RuleSet, RuleSetType
from Models.SGF import SGF
from Models.Scoring import GameResult, Score
from Models.State import State
from Models.Timer import Timer
from Models.User import User


@dataclasses.dataclass
class Game:
    black: User
    white: User
    size: int
    rule_set: RuleSet
    state: State
    timer: Timer
    komi: float
    id: uuid.UUID = dataclasses.field(default_factory=uuid.uuid4)

    @property
    def players(self) -> dict[Color, User]:
        return {Color.black: self.black, Color.white: self.white}

    @players.setter
    def players(self, value: dict[Color, User]) -> None:
        self.black = value[Color.black]
        self.white = value[Color.white]

    @property
    def users(self) -> list[User]:
        return [self.black, self.white]

    @classmethod
    def new_game(
        cls,
        size: int,
        rule_set: RuleSet,
        players: dict[Color, User],
        timer: Timer,
        id_: uuid.UUID | None = None,
    ) -> typing.Self:
        state = State.new_game(size, rule_set.komi)
        game = Game(
            black=players[Color.black],
            white=players[Color.white],
            state=state,
            timer=timer,
            rule_set=rule_set,
            size=size,
            komi=rule_set.komi,
        )
        if id_:
            game.id = id_
        return game

    def is_legal(self, point: Point) -> bool:
        move = Move.play(point)
        return self.rule_set.is_valid_move(game_state=self.state, color=self.state.next_color, move=move)

    def make_move(self, point: Point) -> tuple[Move, GameResult | None]:
        return self._make_move(Move.play(point))

    def _make_move(self, move: Move) -> tuple[Move, GameResult | None]:
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
        uuid_str = sgf.header.get("UD", None)
        size = sgf.header["SZ"]
        rules = get_rule_set_by_name(RuleSetType(sgf.header["RU"]))
        players = {
            Color.black: User(display_name=sgf.header["BP"]),
            Color.white: User(display_name=sgf.header["WP"]),
        }
        game = cls.new_game(size=int(size), rule_set=rules, players=players, timer=Timer(), id_=uuid.UUID(uuid_str))

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
