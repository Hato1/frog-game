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
    """Move right and left"""
    def get_move(self, position: tuple, map: list) -> tuple:
        if self.state == 0:
            self.state = 1
            return position[0]-1, position[1]
        else:
            self.state = 0
            return position[0]+1, position[1]
