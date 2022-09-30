from game.helper import (
    DOWN,
    IDLE,
    LEFT,
    RIGHT,
    UP,
    Point,
    get_facing_direction,
    is_in_map,
)


class Ai:
    def __init__(self, state: int = 0):
        self.state: int = state

    def _get_move(self, position: Point, entity_list: list, dims) -> tuple[Point, int]:
        """Get the next position object wants to move in, and the resulting state"""
        raise NotImplementedError

    def make_move(
        self, position: Point, direction: int, entity_list: list, dims: tuple[int, int]
    ) -> tuple[Point, int]:
        """Get next position and update state"""
        move, new_state = self._get_move(position, entity_list, dims)
        direction = get_facing_direction(move, direction)

        self.state = new_state
        return Point._make(position + move), direction


class Player(Ai):
    """This is a hacky solution used for conflict resolution"""

    def _get_move(self, position: Point, entity_list: list, dims) -> tuple[Point, int]:
        return IDLE, 0


class DeadDoug(Ai):
    """Idle"""

    def _get_move(self, position: Point, entity_list: list, dims) -> tuple[Point, int]:
        return IDLE, 0


class InvalidState(Exception):
    pass


class NormalNorman(Ai):
    """Move right and left (0 or 1) or up and down (2 or 3)"""

    def _get_move(self, position: Point, entity_list: list, dims) -> tuple[Point, int]:
        match self.state:
            case 0:
                return RIGHT, 1
            case 1:
                return LEFT, 0
            case 2:
                return UP, 3
            case 3:
                return DOWN, 2
        raise InvalidState


class SpiralingStacy(Ai):
    """Moves anticlockwise (0 is bottom left) or clockwise (4 is bottom left)"""

    def _get_move(self, position: Point, entity_list: list, dims) -> tuple[Point, int]:
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
        raise InvalidState


class TrickyTrent(Ai):
    """Moves clockwise or anticlockwise in a diamond"""

    def _get_move(self, position: Point, entity_list: list, dims) -> tuple[Point, int]:
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
        raise InvalidState


class BarrelingBarrel(Ai):
    """Moves idle/up/down/left/right in state (0/1/2/3/4) until changed"""

    def _get_move(self, position: Point, entity_list: list, dims) -> tuple[Point, int]:
        match self.state:
            case 0:
                return IDLE, 0
            case 1:
                direction, new_state = UP, 1
            case 2:
                direction, new_state = DOWN, 2
            case 3:
                direction, new_state = LEFT, 3
            case 4:
                direction, new_state = RIGHT, 4
            case _:
                raise InvalidState
        dest = position + direction
        if not is_in_map(dest, dims):
            return IDLE, 0
        if any(entity for entity in entity_list if entity.position == dest):
            return IDLE, 0

        return direction, new_state


class DirtyDan(Ai):
    """mirrors the player's movements"""

    def _get_move(self, position: Point, entity_list: list, dims) -> tuple[Point, int]:
        raise NotImplementedError


class SlidingStone(Ai):
    """DeadDoug, but pushable"""

    def _get_move(self, position: Point, entity_list: list, dims) -> tuple[Point, int]:
        return IDLE, 0
