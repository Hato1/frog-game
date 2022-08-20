from .helper import UP, LEFT, DOWN, RIGHT, IDLE, facing, Vector, Point


class Ai:
    def __init__(self, state: int = 0):
        self.state: int = state

    def _get_move(self, position: Point, _map: list) -> tuple[Vector, int]:
        """Get the next position object wants to move in, and the resulting state"""
        raise NotImplementedError

    def make_move(self, position: Point, direction: int, _map: list) -> tuple[Point, int]:
        """Get next position and update state"""
        move, new_state = self._get_move(position, _map)
        direction = facing(move, direction)

        self.state = new_state
        return Point._make(position + move), direction


class DeadDoug(Ai):
    """Dead dougs don't die"""
    def _get_move(self, position: Point, _map: list) -> tuple[Vector, int]:
        return IDLE, 0


class NormalNorman(Ai):
    """Move right and left (0 or 1) or up and down (2 or 3)"""
    def _get_move(self, position: Point, _map: list) -> tuple[Vector, int]:
        match self.state:
            case 0:
                return RIGHT, 1
            case 1:
                return LEFT, 0
            case 2:
                return UP, 3
            case 3:
                return DOWN, 2
        assert False


class SpiralingStacy(Ai):
    """Moves anticlockwise (0 is bottom left) or clockwise (4 is bottom left)"""
    def _get_move(self, position: Point, _map: list) -> tuple[Vector, int]:
        match self.state:
            case 0:
                return RIGHT, 1
            case 1:
                return UP, 2
            case 2:
                return LEFT, 3
            case 3:
                return DOWN, 0
            case 4:
                return UP, 5
            case 5:
                return RIGHT, 6
            case 6:
                return DOWN, 7
            case 7:
                return LEFT, 4
        assert False


class TrickyTrent(Ai):
    """Moves clockwise or anticlockwise in a diamond"""
    def _get_move(self, position: Point, _map: list) -> tuple[Vector, int]:
        match self.state:
            case 0:
                return UP + RIGHT, 1
            case 1:
                return RIGHT + DOWN, 2
            case 2:
                return DOWN + LEFT, 3
            case 3:
                return LEFT + UP, 0
            case 4:
                return RIGHT + DOWN, 5
            case 5:
                return UP + RIGHT, 6
            case 6:
                return LEFT + UP, 7
            case 7:
                return DOWN + LEFT, 4
        assert False


class BarrelingBarrel(Ai):
    """Moves not at all, up/down/left/right in state (0/1/2/3/4+) until stat"""
    def _get_move(self, position: Point, _map: list) -> tuple[Vector, int]:
        match self.state:
            case 0:
                return IDLE, 0
            case 1:
                return UP, 1
            case 2:
                return DOWN, 2
            case 3:
                return LEFT, 3
            case 4:
                return RIGHT, 4
        assert False


class DirtyDan(Ai):
    """mirrors the player's movements"""
    # I don't know how to do this
