import abc
import copy
import enum

from Models.BasicTypes import Color, Move
from Models.Scoring import Score
from Models.State import State


class Rule(abc.ABC):
    def __init__(self):
        pass

    @staticmethod
    @abc.abstractmethod
    def is_valid_move(game_state: State, color: Color, move: Move) -> bool:
        raise NotImplementedError


class BasicRule(Rule):
    # should always be the first rule in any RuleSet
    @staticmethod
    def is_valid_move(game_state: State, color: Color, move: Move) -> bool:
        if not move.is_play:
            return True
        if color is None:
            return False
        if game_state.board.get_color(move.point) is not None:
            return False
        return True


class KoRule(Rule):
    @staticmethod
    def is_valid_move(game_state: State, color: Color, move: Move) -> bool:
        if game_state.previous_state is None:
            return True
        next_board = copy.deepcopy(game_state.board)
        next_board.place_stone(color, move.point)
        next_situation = (color.other, next_board.hash)
        return next_situation != game_state.previous_state.situation


class SuperKoRule(Rule):
    @staticmethod
    def is_valid_move(game_state: State, color: Color, move: Move) -> bool:
        next_board = copy.deepcopy(game_state.board)
        next_board.place_stone(color, move.point)
        next_situation = (color.other, next_board.hash)
        return next_situation not in game_state.previous_states


class SelfCaptureRule(Rule):
    @staticmethod
    def is_valid_move(game_state: State, color: Color, move: Move) -> bool:
        next_board = copy.deepcopy(game_state.board)
        next_board.place_stone(color, move.point)
        new_group = next_board.get_group(move.point)
        return new_group.num_liberties != 0


class RuleSet:
    def __init__(self, *rules, komi, name):
        self.rules = [BasicRule] + [*rules]
        self.komi = komi
        self.name = name

    def is_valid_move(self, game_state: State, color: Color, move: Move) -> bool:
        for rule in self.rules:
            if not rule.is_valid_move(game_state, color, move):
                return False
        return True


def get_ai_rule_set() -> RuleSet:
    return RuleSet(SelfCaptureRule, SuperKoRule, komi=Score(w_score=7.5), name="ai")


def get_japanese_rule_set() -> RuleSet:
    """
    https://senseis.xmp.net/?JapaneseRules
    """
    return RuleSet(SelfCaptureRule, KoRule, komi=Score(w_score=6.5), name="japanese")


def get_chinese_rule_set() -> RuleSet:
    """
    https://senseis.xmp.net/?ChineseRules
    """
    return RuleSet(SelfCaptureRule, SuperKoRule, komi=Score(w_score=7.5), name="chinese")


def get_ign_rule_set() -> RuleSet:
    """
    https://senseis.xmp.net/?IngRules
    """
    return RuleSet(SuperKoRule, komi=Score(w_score=7.5), name="ign")


class RuleSetType(enum.Enum):
    japanese = 'japanese'
    chinese = 'chinese'
    ign = 'ign'
    ai = 'ai'


def get_rule_set_by_name(rule_set_type: RuleSetType) -> RuleSet:
    if rule_set_type == RuleSetType.japanese:
        return get_japanese_rule_set()
    if rule_set_type == RuleSetType.chinese:
        return get_chinese_rule_set()
    if rule_set_type == RuleSetType.ign:
        return get_ign_rule_set()
    if rule_set_type == RuleSetType.ai:
        return get_ai_rule_set()
