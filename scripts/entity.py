"""Module for animate objects"""
from typing import Optional

from .ai import (
    BarrelingBarrel,
    DeadDoug,
    NormalNorman,
    Player,
    SlidingStone,
    SpiralingStacy,
    TrickyTrent,
)
from .helper import Point, facing

# TODO: Rename DeadDoug to InanimateIvan
AI_DICT = {
    "NormalNorman": NormalNorman,
    "DeadDoug": DeadDoug,
    "SpiralingStacy": SpiralingStacy,
    "BarrelingBarrel": BarrelingBarrel,
    "TrickyTrent": TrickyTrent,
    "Player": Player,
    "SlidingStone": SlidingStone,
}

# Entity facing direction constants to index in gui.py
UP, RIGHT, DOWN, LEFT = range(4)


class Entity:
    """Thing on the map that is not part of the background"""

    next_id = 0
    default_point = Point(-1, -1)

    def __init__(
        self,
        name: str,
        strategy: str = "DeadDoug",
        direction: int = UP,
        position: Point = default_point,
        solid: bool = False,
    ) -> None:
        self.alive = True
        """
        Args:
            name: A human friendly name
            strategy: name of creature AI, decides the creatures movement pattern
            solid: Whether other objects can move onto this object's space.
            direction: which way the creature is initially facing
        """
        # self.state = 0
        # Entities do not have states. Entity.strategys have states
        self.strategy_name = strategy
        self.strategy = AI_DICT[strategy]()
        # Used to force creatures next move, ignoring their strategy.
        # Is this neccesary, or is force_move sufficient?
        # TODO: Make this a list of points, FIFO.
        self.next_move: Optional[Point] = None

        self.id = Entity.next_id
        Entity.next_id += 1
        self.name = name
        self.solid = solid
        self.direction = direction
        self.position = position
        self.alive = True
        # TODO: also needs other properties, eg state
        self.position_history: list[Point] = []

    def __str__(self) -> str:
        return self.name

    def force_move(self, forced_moves: list[Point]):
        """Handles moves forced by collisions"""
        # Perhaps change facing direction here?
        # Would be nice to integrate into get_next_move or make_move
        for move in forced_moves:
            self.position = self.position + move

    def force_state(self, next_state: int) -> None:
        self.strategy.state = next_state

    def force_facing(self, move) -> None:
        self.direction = facing(move, self.direction)

    def make_move(self, _map: list):
        """Default move behaviour"""
        # TODO: Ensure position history is sensible when force_move is used
        self.position_history.append(self.position)
        self.position, self.direction = self.get_next_move(self.position, _map)
        # assert self.in_map(new_pos), f"{entity.name} Cheated!"

    def get_next_move(self, position: Point, _map: list) -> tuple[Point, int]:
        if self.next_move:
            next_position = position + self.next_move
            direction = facing(self.next_move, self.direction)
            self.next_move = None
        else:
            next_position, direction = self.strategy.make_move(
                position, self.direction, _map
            )
        assert (
            type(next_position) == Point
        ), f"{self.name} returned invalid move: {type(next_position)}."
        assert (
            len(next_position) == 2
        ), f"{self.name} requests invalid move: {next_position}"
        return next_position, direction

    def get_strategy_name(self) -> str:
        return self.strategy_name

    def get_state(self) -> int:
        return self.strategy.state
