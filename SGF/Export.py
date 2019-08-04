from Models.Game import Game
from Models.BasicTypes import Color
from Models.State import State


class SGF:
    def __init__(self, game):
        self.nodes = []
        assert isinstance(game, Game)
        state = game.state
        while state.previous_state is not None:
            self.nodes = [self.state_to_sgf_dict(state)] + self.nodes
            state = state.previous_state

        self.nodes = [self.generate_sgf_header_dict(game)] + self.nodes

    # the header of an sgf file, also called the root node.
    @staticmethod
    def generate_sgf_header_dict(game):
        assert isinstance(game, Game)
        header = {
            'FF': 4,  # FF[4] means SGF version 4.
            'GM': 1,  # GM[1] means that the game is "go"
            'SZ': game.size,
            'BP': game.players[Color.black].user.display_name,
            'WP': game.players[Color.white].user.display_name,
            'RU': game.state.rule_set.name
        }

        return header

    @staticmethod
    def state_to_sgf_dict(state):
        assert isinstance(state, State)
        return {state.next_color.sgf_str: state.last_move.sgf_str}

    def __str__(self):
        string = "("
        for node in self.nodes:
            string += ";"
            for key in node:
                string += f'{key}[{node[key]}]\n'
        string += ")"
        return string

    def __repr__(self):
        return str(self)
