import copy


class Rule:
    def __init__(self):
        pass

    def is_legal(self, game_state, player, move):
        raise NotImplementedError

    def basic_checks(self, player, move):
        if not move.is_play:
            return True
        if player.color is None:
            return False
        return None


class SuperKoRule(Rule):
    def is_legal(self, game_state, player, move):
        result = self.basic_checks(player, move)
        if result is not None:
            return result
        next_board = copy.deepcopy(game_state.board)
        next_board.place_stone(player.color, move.point)
        next_situation = (player.color.other, next_board.zobrist_hash())
        return next_situation not in game_state.previous_states


class SuicideRule(Rule):
    def is_legal(self, game_state, player, move):
        result = self.basic_checks(player, move)
        if result is not None:
            return result
        next_board = copy.deepcopy(game_state.board)
        next_board.place_stone(player.color, move.point)
        new_group = next_board.get_go_group(move.point)
        return new_group.num_liberties != 0
