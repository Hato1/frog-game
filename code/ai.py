from helper import UP, LEFT, DOWN, RIGHT


class Ai():
    def __init__(self, state: int = 0):
        self.state: int = state

    def _get_move(self, position: tuple, _map: list) -> tuple[tuple, int]:
        """Get the next position object wants to move in, and the resulting state"""
        raise NotImplementedError

    def make_move(self, position: tuple, _map: list) -> tuple:
        """Get next position and update state"""
        move, newstate = self._get_move(position, _map)
        self.state = newstate
        return move


class DeadDoug(Ai):
    """Dead dougs don't die"""
    def _get_move(self, position: tuple, map: list) -> tuple[tuple, int]:
        return position, 0


class NormalNorman(Ai):
    """Move right and left (0 or 1) or up and down (2 or 3)"""
    def _get_move(self, position: tuple, map: list) -> tuple[tuple, int]:
        match self.state:
            case 0:
                return position + RIGHT, 1
            case 1:
                return position + LEFT, 0
            case 2:
                return position + UP, 3
            case 3:
                return position + DOWN, 2
        assert False


class SpiralingStacy(Ai):
    """Moves anticlockwise (0 is bottom left) or clockwise (4 is bottom left)"""
    def _get_move(self, position: tuple, map: list) -> tuple[tuple, int]:
        match self.state:
            case 0:
                return position + RIGHT, 1
            case 1:
                return position + UP, 2
            case 2:
                return position + LEFT, 3
            case 3:
                return position + DOWN, 0
            case 4:
                return position + UP, 5
            case 5:
                return position + RIGHT, 6
            case 6:
                return position + DOWN, 7
            case 7:
                return position + LEFT, 4
        assert False


class BarrelingBarrel(Ai):
    """Moves not at all, up/down/left/right in state (0/1/2/3/4+) untill stat"""
    def _get_move(self, position: tuple, map: list) -> tuple[tuple, int]:
        match self.state:
            case 0:
                return position, 0
            case 1:
                return position + UP, 1
            case 2:
                return position + DOWN, 2
            case 3:
                return position + LEFT, 3
            case 4:
                return position + RIGHT, 4
        assert False


class DirtyDan(Ai):
    """mirrors the player's movements"""
    # I don't know how to do this
