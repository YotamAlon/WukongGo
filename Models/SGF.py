from Models.Game import Game
from Models.BasicTypes import Color
from Models.State import State


class SGF:
    def __init__(self, game=None, nodes=None):
        if game is not None:
            self.nodes = []
            assert isinstance(game, Game)
            state = game.state
            while state.previous_state is not None:
                self.nodes = [self.state_to_sgf_dict(state)] + self.nodes
                state = state.previous_state

            self.nodes = [self.header_from_game(game)] + self.nodes
        if nodes is not None:
            self.nodes = nodes

    # the header of an sgf file, also called the root node.
    @staticmethod
    def header_from_game(game):
        assert isinstance(game, Game)
        header = {
            'FF': 4,  # FF[4] means SGF version 4.
            'GM': 1,  # GM[1] means that the game is "go"
            'SZ': game.size,
            'BP': game.players[Color.black].user.display_name,
            'WP': game.players[Color.white].user.display_name,
            'RU': game.state.rule_set.name,
            'KM': game.state.rule_set.komi.w_score
        }

        return header

    @staticmethod
    def header_from_string(string):
        assert isinstance(string, str)
        string = string.strip()
        key_mode = True
        index = 0
        node = {}
        key = ""
        value = ""
        while index < len(string):
            if string[index] == "\n":
                pass
            elif string[index] == "[":
                key_mode = False
                value = ""
            elif string[index] == "]":
                key_mode = True
                node[key] = value
                key = ""
            elif key_mode:
                key += string[index]
            elif not key_mode:
                value += string[index]
            index += 1
        return node

    @staticmethod
    def move_from_string(string):
        assert isinstance(string, str)
        string = string.strip()
        return {string[0]: string[2:4]}

    @staticmethod
    def state_to_sgf_dict(state):
        assert isinstance(state, State)
        return {state.next_color.sgf_str: state.last_move.sgf_str}

    @staticmethod
    def from_string(string):
        nodes_s = string.split(";")
        nodes_s = nodes_s[1:]  # ignoring the starting "(" for now. later we will go into different variations.
        nodes = [SGF.header_from_string(nodes_s[0])]
        nodes += [SGF.move_from_string(m) for m in nodes_s[1:]]
        return SGF(nodes=nodes)

    @property
    def header(self):
        return self.nodes[0]

    @property
    def moves(self):
        return self.nodes[1:]

    def __str__(self):
        string = "("
        for node in self.nodes:
            string += "\n;"
            for key in node:
                string += f'{key}[{node[key]}]'
        string += "\n)"
        return string

    def __repr__(self):
        return str(self)
