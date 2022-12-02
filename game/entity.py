"""Module for animate objects"""
import random
from typing import Optional

from game.ai import Ai, Tags
from game.helper import Point, c, get_facing_direction, is_in_map

# Delete me :(
MAP_WIDTH = 28
MAP_HEIGHT = 23

# TODO: Merge Entity and BaseAI?

# Entity facing direction constants to index in gui.py
UP, RIGHT, DOWN, LEFT = range(4)


class Entity:
    """Thing on the map that is not part of the background"""

    def __init__(
        self,
        name: str,
        strategy: Optional[Ai] = None,
        facing: int = UP,
        position: Optional[Point] = None,
        tags: Optional[list[Tags]] = None,
    ) -> None:
        """
        Args:
            name: A human friendly name
            strategy: name of creature AI, decides the creatures movement pattern
            facing: which way the creature is initially facing
        """
        # TODO: Configure strategies starting state
        self.strategy: Ai = strategy or Ai()
        # Used to force creatures next move, ignoring their strategy.
        # TODO: Is this necessary? Have player AI hold this instead.
        # TODO: Make this a list of points, FIFO.
        self.next_move: Optional[Point] = None
        self.name = name
        self.facing = facing
        self.position = position or Point(-1, -1)
        self.alive = True
        self.position_history: list[Point] = []
        self.tags: list[Tags] = tags or []

    def make_move(self, entity_list: list, dims: tuple[int, int]):
        """Move entity according to their strategy."""
        self.position_history.append(self.position)
        self.position, self.facing = self._get_next_move(self.position, entity_list, dims)

    def _get_next_move(self, position: Point, entity_list: list, dims: tuple[int, int]) -> tuple[Point, int]:
        # TODO: Remove need to send through entity list with some global access to worlds.
        if self.next_move:
            next_position = position + self.next_move
            direction = get_facing_direction(self.next_move, self.facing)
            self.next_move = None
        else:
            next_position, direction = self.strategy.make_move(position, self.facing, entity_list, dims)
        assert type(next_position) == Point, f"{self.name} returned invalid move: {type(next_position)}."
        assert len(next_position) == 2, f"{self.name} requests invalid move: {next_position}"
        assert is_in_map(next_position, dims), f"{self} tried to leave the play area at {next_position}!"
        return next_position, direction

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
