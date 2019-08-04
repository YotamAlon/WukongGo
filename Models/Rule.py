import copy
from Models.Scoring import Score


class Rule:
    def __init__(self):
        pass

    @staticmethod
    def is_valid_move(game_state, color, move):
        raise NotImplementedError


class BasicRule(Rule):
    # should always be the first rule in any RuleSet
    @staticmethod
    def is_valid_move(game_state, color, move):
        if not move.is_play:
            return True
        if color is None:
            return False
        if game_state.board.get_color(move.point) is not None:
            return False
        return True


class KoRule(Rule):
    @staticmethod
    def is_valid_move(game_state, color, move):
        if game_state.previous_state is None:
            return True
        next_board = copy.deepcopy(game_state.board)
        next_board.place_stone(color, move.point)
        next_situation = (color.other, next_board.hash)
        return next_situation != game_state.previous_state.situation


class SuperKoRule(Rule):
    @staticmethod
    def is_valid_move(game_state, color, move):
        next_board = copy.deepcopy(game_state.board)
        next_board.place_stone(color, move.point)
        next_situation = (color.other, next_board.hash)
        return next_situation not in game_state.previous_states


class SelfCaptureRule(Rule):
    @staticmethod
    def is_valid_move(game_state, color, move):
        next_board = copy.deepcopy(game_state.board)
        next_board.place_stone(color, move.point)
        new_group = next_board.get_group(move.point)
        return new_group.num_liberties != 0


class RuleSet:
    def __init__(self, *rules, komi, name):
        self.rules = [BasicRule] + [*rules]
        self.komi = komi
        self.name = name

    def is_valid_move(self, game_state, color, move):
        for rule in self.rules:
            if not rule.is_valid_move(game_state, color, move):
                return False
        return True


def get_ai_rule_set():
    return RuleSet(SelfCaptureRule, SuperKoRule, komi=Score(w_score=7.5), name="ai")


def get_japanese_rule_set():
    """
    https://senseis.xmp.net/?JapaneseRules
    """
    return RuleSet(SelfCaptureRule, KoRule, komi=Score(w_score=6.5), name="japanese")


def get_chinese_rule_set():
    """
    https://senseis.xmp.net/?ChineseRules
    """
    return RuleSet(SelfCaptureRule, SuperKoRule, komi=Score(w_score=7.5), name="chinese")


def get_ign_rule_set():
    """
    https://senseis.xmp.net/?IngRules
    """
    return RuleSet(SuperKoRule, komi=Score(w_score=7.5), name="ign")


def get_rule_set_by_name(name):
    if name == "japanese":
        return get_japanese_rule_set()
    if name == "chinese":
        return get_chinese_rule_set()
    if name == "ign":
        return get_ign_rule_set()
    if name == "ai":
        return get_ai_rule_set()
