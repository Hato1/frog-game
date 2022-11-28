"""Module for animate objects"""
import random
from enum import Enum
from typing import Optional

from game.ai import Ai
from game.helper import Point, c, get_facing_direction, is_in_map

# Delete me :(
MAP_WIDTH = 28
MAP_HEIGHT = 23


class Tags(str, Enum):
    solid = "solid"
    hops = "hops"
    player = "player"
    pushable = "pushable"
    pusher = "pusher"
    kills_player = "kills_player"
    barrel = "barrel"
    no_animation = "no_animation"


# Entity facing direction constants to index in gui.py
UP, RIGHT, DOWN, LEFT = range(4)


def solid_entity_at(point, entity_list):
    return any(Tags.solid in entity.tags for entity in entity_list if entity.position == point)


def entity_at(point, entity_list):
    return any(entity for entity in entity_list if entity.position == point)


class Entity:
    """Thing on the map that is not part of the background"""

    next_id = 0
    default_point = Point(-1, -1)

    def __init__(
        self,
        name: str,
        strategy: Optional[Ai] = None,
        direction: int = UP,
        position: Point = default_point,
        tags: Optional[list[str]] = None,
    ) -> None:
        self.alive = True
        """
        Args:
            name: A human friendly name
            strategy: name of creature AI, decides the creatures movement pattern
            direction: which way the creature is initially facing
        """
        # Entities do not have states. Entity.strategies have states
        # self.strategy_name = strategy
        self.strategy: Ai = strategy or Ai()
        # Used to force creatures next move, ignoring their strategy.
        # Is this necessary, or is force_move sufficient?
        # TODO: Make this a list of points, FIFO.
        self.next_move: Optional[Point] = None

        self.id = Entity.next_id
        Entity.next_id += 1
        self.name = name
        self.direction = direction
        self.position = position
        self.alive = True
        # TODO: also needs other properties, eg state
        self.position_history: list[Point] = []
        self.tags = tags or []

    def __repr__(self) -> str:
        try:
            random.seed(self.name)
            return c(self.name, fg=random.choice("krgybmcw"))
        finally:
            random.seed()

    __str__ = __repr__

    def force_move(self, forced_moves: list[Point], entity_list):
        """Handles moves forced by collisions"""
        # Perhaps change facing direction here?
        # Would be nice to integrate into get_next_move or make_move
        for move in forced_moves:
            assert move != Point(0, 0)
            check_tile = self.position
            while True:
                check_tile += move
                if solid_entity_at(check_tile, entity_list):
                    return False
                elif not is_in_map(check_tile, Point(MAP_WIDTH, MAP_HEIGHT)):
                    return False
                # Temp, stops entities from being force pushed onto something
                elif not entity_at(check_tile, entity_list):
                    self.position = self.position + move
                    break
        return True

    def force_state(self, next_state: int) -> None:
        self.strategy.state = next_state

    def force_facing(self, move) -> None:
        self.direction = get_facing_direction(move, self.direction)

    def make_move(self, entity_list: list, dims: tuple[int, int]):
        """Default move behaviour"""
        # TODO: Ensure position history is sensible when force_move is used
        self.position_history.append(self.position)
        self.position, self.direction = self.get_next_move(self.position, entity_list, dims)
        # assert self.in_map(new_pos), f"{entity.name} Cheated!"

    def get_next_move(
        self, position: Point, entity_list: list, dims: tuple[int, int]
    ) -> tuple[Point, int]:
        if self.next_move:
            next_position = position + self.next_move
            direction = get_facing_direction(self.next_move, self.direction)
            self.next_move = None
        else:
            next_position, direction = self.strategy.make_move(
                position, self.direction, entity_list, dims
            )
        assert (
            type(next_position) == Point
        ), f"{self.name} returned invalid move: {type(next_position)}."
        assert len(next_position) == 2, f"{self.name} requests invalid move: {next_position}"
        assert is_in_map(
            next_position, dims
        ), f"{self} tried to leave the play area at {next_position}!"
        return next_position, direction

    def get_strategy_name(self) -> str:
        return self.strategy.get_name()

    def get_state(self) -> int:
        return self.strategy.state

    def animates(self):
        return Tags.no_animation not in self.tags

    def randomises(self):
        return self.name in ["Stone"]
