"""Module for handling entities
ToDo: Make this a registry?
ToDo: Have world be global, there's no need to pass it as a parameter everywhere.
"""
from __future__ import annotations

import math
import random
from enum import Enum
from typing import Optional, Type

from game import db
from game.helper import DOWN, IDLE, LEFT, RIGHT, UP, Point, c, is_in_map

SPECIES: dict[str, Type[Entity]] = {}


class Tags(str, Enum):
    solid = "solid"
    hops = "hops"
    player = "player"
    pushable = "pushable"
    pusher = "pusher"
    kills_player = "kills_player"
    barrel = "barrel"
    no_animation = "no_animation"
    random_sprite = "random_sprite"


class Facing(int, Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


class InvalidState(Exception):
    pass


def solid_entity_at(point):
    return any(Tags.solid in entity for entity in db.world.entities if entity.position == point)


class Entity:
    """Thing on the map that is not part of the background"""

    default_tags: list[Tags] = []

    def __init__(
        self,
        name: Optional[str] = None,
        position: Optional[Point] = None,
        tags: Optional[list[Tags]] = None,
        state: int = 0,
        facing: Facing = Facing.UP,
    ):
        """
        Args:
            name: A human friendly name
            facing: which way the creature is initially facing
        """
        # TODO: Is name really needed? Use Property, or better yet a clever dunder __eq__?
        self.name: str = name or type(self).__name__
        self.position: Point = position or Point(-1, -1)
        self.tags: list[Tags] = tags or []
        self.tags.extend(self.default_tags)
        self.state: int = state
        self._facing: Facing = facing
        self.alive: bool = True
        self.position_history: list[Point] = []

    def _get_move(self, **kwargs) -> tuple[Point, int]:
        """Entities movement pattern.
        Get the next position object wants to move in, and the resulting state"""
        raise NotImplementedError

    def make_move(self):
        """Move entity and update their state according to their strategy."""
        self.position_history.append(self.position)
        move, self.state = self._get_move()

        # Should this be in _get_move?
        new_position = self.position + move
        if solid_entity_at(new_position):
            new_position -= move
        self.position = new_position

        assert type(self.position) == Point, f"{self.name} returned invalid move: {type(self.position)}."
        assert len(self.position) == 2, f"{self.name} requests invalid move: {self.position}"
        assert is_in_map(self.position, db.world.dims), f"{self} tried to leave the play area at {self.position}!"

    @property
    def facing(self) -> Facing:
        """Get the cardinal direction an entity should be facing."""
        next_move, _ = self._get_move()
        if next_move != Point(0, 0):
            # Adding a cheeky +1 to degrees so 45 and -45 don't both equate to the same direction.
            degrees = math.atan2(*next_move) / math.pi * 180 + 1
            compass_lookup = round(degrees / 90) % 360
            self._facing = [Facing.DOWN, Facing.LEFT, Facing.UP, Facing.RIGHT][compass_lookup % 4]
        return self._facing

    def __contains__(self, tag):
        return tag in self.tags

    def __repr__(self) -> str:
        try:
            random.seed(self.name)
            # Todo: implement random colours better than keyboard spam
            return c(self.name, fg=random.choice("krgybmcw"))
        finally:
            random.seed()

    __str__ = __repr__

    @classmethod
    def __init_subclass__(cls, *args, **kwargs):
        SPECIES[cls.__name__] = cls


class IdleIvan(Entity):
    """Default idle animation. #DeadDougDied"""

    def _get_move(self, **kwargs) -> tuple[Point, int]:
        return IDLE, 0


class Stone(IdleIvan):
    """Rock n stone to the bone"""


class Wall(IdleIvan):
    """Humpty dumpty had a great fall..."""


class SlidingStone(IdleIvan):
    """I see a red door and I want it painted black"""


class Player(Entity):
    """Player"""

    default_tags = [Tags.player]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.move_queue: list[Point] = []
        self.max_steps: int = 50
        self.steps_left: int = self.max_steps

    @property
    def facing(self) -> Facing:
        if not self.position_history:
            return Facing.UP
        last_move = self.position - self.position_history[-1]
        if last_move != Point(0, 0):
            # Adding a cheeky +1 to degrees so 45 and -45 don't both equate to the same direction.
            degrees = math.atan2(*last_move) / math.pi * 180 + 1
            compass_lookup = round(degrees / 90) % 360
            self._facing = [Facing.DOWN, Facing.LEFT, Facing.UP, Facing.RIGHT][compass_lookup % 4]
        return self._facing

    def _get_move(self, **kwargs):
        if not self.steps_left:
            self.alive = False
        self.steps_left -= 1
        if not self.move_queue:
            return IDLE, 0
        return self.move_queue.pop(0), 0


class NormalNorman(Entity):
    """Move right and left (0 or 1) or up and down (2 or 3)"""

    def _get_move(self, **kwargs) -> tuple[Point, int]:
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


class SpiralingStacy(Entity):
    """Moves anticlockwise (0 is bottom left) or clockwise (4 is bottom left)"""

    def _get_move(self, **kwargs) -> tuple[Point, int]:
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


class TrickyTrent(Entity):
    """Moves clockwise or anticlockwise in a diamond"""

    def _get_move(self, **kwargs) -> tuple[Point, int]:
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


class BarrelingBarrel(Entity):
    """Moves idle/up/down/left/right in state (0/1/2/3/4) until changed"""

    def _get_move(self, **kwargs) -> tuple[Point, int]:
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
        dest = self.position + direction
        if not is_in_map(dest, db.world.dims):
            return IDLE, 0
        # if any(entity for entity in entity_list if entity.position == dest):
        #    return IDLE, 0

        return direction, new_state


class DirtyDan(Entity):
    """mirrors the player's movements"""

    def _get_move(self, **kwargs) -> tuple[Point, int]:
        raise NotImplementedError


# TODO: add species names to map builder, remove the need for these poorly named creatures


class FrogY(SpiralingStacy):
    pass


class FrogR(NormalNorman):
    pass


class FrogP(TrickyTrent):
    pass


class Barrel(BarrelingBarrel):
    pass


class RockWall(Wall):
    pass


class InvisWall(Wall):
    pass
