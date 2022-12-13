from __future__ import annotations

import math
import random
from enum import Enum
from typing import Optional, Type

from game.helper import Point, c

# TODO: Make this an entity class attribute?
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

    def make_move(self) -> Point:
        """Move entity and update their state according to their strategy."""
        self.position_history.append(self.position)
        move, self.state = self._get_move()
        self.position = self.position + move

        assert type(self.position) == Point, f"{self.name} returned invalid move: {type(self.position)}."
        assert len(self.position) == 2, f"{self.name} requests invalid move: {self.position}"
        return self.position

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
