from dlgo import goboard
from dlgo.utils import print_move, print_board, point_from_coords
from dlgo.rules import get_ai_rule_set
from six.moves import input


def main():
    board_size = 9
    game = goboard.GameState.new_game(board_size, get_ai_rule_set())

    while not game.is_over():
        print(chr(27))
        print_board(game.board)

        human_move = input('-- ')
        point = point_from_coords(human_move.strip())
        move = goboard.Move.play(point)

        print_move(game.next_color, move)
        game = game.apply_move(move)


if __name__ == '__main__':
    main()
