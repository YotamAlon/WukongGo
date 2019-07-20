from dlgo.gotypes import Point, Color


class User:
    def __init__(self, token):
        self.token = token

    @property
    def type(self):
        raise NotImplementedError()


class ActiveUser(User):
    def __init__(self, token, color):
        super.__init__(token)
        self.color = color

    def get_next_move(self, game_state):
        raise NotImplementedError()

    @property
    def type(self):
        return "active"


class Player(ActiveUser):
    def get_next_move(self, game_state):
        # not sure how to handle getting a move from a button, actively.
        raise NotImplementedError()

    @property
    def type(self):
        return super.type + ";player"


