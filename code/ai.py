from helper import add_tuple
UP, LEFT, DOWN, RIGHT = (-1, 0), (0, -1), (1, 0), (0, 1)

class Ai():
    def __init__(self, state: int = 0):
        self.state: int = state

    def get_move(self, position: tuple, map: list) -> tuple:
        raise NotImplementedError


class DeadDoug(Ai):
    """Dead dougs don't die"""
    def get_move(self, position: tuple, map: list) -> tuple:
        return position


class NormalNorman(Ai):
    """Move right and left (0 or 1) or up and down (2 or 3)"""
    def get_move(self, position: tuple, map: list) -> tuple:
        if self.state == 0:
            self.state = 1
            return add_tuple(position, RIGHT)
        elif self.state == 1:
            self.state = 0
            return add_tuple(position, LEFT)
        elif self.state == 2:
            self.state = 3
            return add_tuple(position, UP)
        else:
            self.state = 2
            return add_tuple(position, DOWN)

class SpiralingStacy(Ai):
    """Moves anticlockwise (0 is bottom left) or clockwise (4 is bottom left)"""
    def get_move(self, position: tuple, map: list) -> tuple:
        if self.state == 0:
            self.state = 1
            return add_tuple(position, RIGHT)
        elif self.state == 1:
            self.state = 2
            return add_tuple(position, UP)
        elif self.state == 2:
            self.state = 3
            return add_tuple(position, LEFT)
        elif self.state == 3:
            self.state = 0
            return add_tuple(position, DOWN)
        elif self.state == 4:
            self.state = 5
            return add_tuple(position, UP)
        elif self.state == 5:
            self.state = 6
            return add_tuple(position, RIGHT)
        elif self.state == 6:
            self.state = 7
            return add_tuple(position, DOWN)
        else: # self.state == 7:
            self.state = 4
            return add_tuple(position, LEFT)


class BarrelingBarrel(Ai):
    """Moves not at all, up/down/left/right in state (0/1/2/3/4+) untill stat"""
    def get_move(self, position: tuple, map: list) -> tuple:
        if self.state == 0:
            return position
        elif self.state == 1:
            return add_tuple(position, UP)
        elif self.state == 2:
            return add_tuple(position, DOWN)
        elif self.state == 3:
            return add_tuple(position, LEFT)
        else: # self.state == 4:
            return add_tuple(position, RIGHT)


class DirtyDan(Ai):
    """mirrors the player's movements"""
    # I don't know how to do this
