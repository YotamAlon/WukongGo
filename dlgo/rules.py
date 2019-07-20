import copy


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
        if game_state.board.get(move.point) is not None:
            return False
        return True


class SuperKoRule(Rule):
    @staticmethod
    def is_valid_move(game_state, color, move):
        next_board = copy.deepcopy(game_state.board)
        next_board.place_stone(color, move.point)
        next_situation = (color.other, next_board.zobrist_hash())
        return next_situation not in game_state.previous_states


class SelfCaptureRule(Rule):
    @staticmethod
    def is_valid_move(game_state, color, move):
        next_board = copy.deepcopy(game_state.board)
        next_board.place_stone(color, move.point)
        new_group = next_board.get_go_group(move.point)
        return new_group.num_liberties != 0


class RuleSet:
    def __init__(self, *rules):
        self.rules = [BasicRule] + [*rules]

    def is_valid_move(self, game_state, color, move):
        for rule in self.rules:
            if not rule.is_valid_move(game_state, color, move):
                return False
        return True


def get_ai_rule_set():
    return RuleSet(SelfCaptureRule, SuperKoRule)
