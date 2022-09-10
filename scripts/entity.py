"""Module for animate objects"""
from typing import Optional

from .ai import (
    BarrelingBarrel,
    DeadDoug,
    NormalNorman,
    Player,
    SpiralingStacy,
    TrickyTrent,
)
from .helper import Point, Vector, facing

# TODO: Rename DeadDoug to InanimateIvan
AI_DICT = {
    "NormalNorman": NormalNorman,
    "DeadDoug": DeadDoug,
    "SpiralingStacy": SpiralingStacy,
    "BarrelingBarrel": BarrelingBarrel,
    "TrickyTrent": TrickyTrent,
    "Player": Player,
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
        self.state = 0
        self.strategy_name = strategy
        self.strategy = AI_DICT[strategy]()
        # Used to force creatures next move, ignoring their strategy.
        # TODO: Make this a list of points, FIFO.
        # TODO: Remove Vectors and replace with Points
        self.next_move: Optional[Vector] = None

        self.id = Entity.next_id
        Entity.next_id += 1
        self.name = name
        self.solid = solid
        self.direction = direction
        self.position = position

    def __str__(self) -> str:
        return self.name

    def get_next_move(self, position: Point, _map: list) -> Point:
        if self.next_move:
            self.direction = facing(self.next_move, self.direction)
            try:
                return position + self.next_move
            finally:
                self.next_move = None
        move, self.direction = self.strategy.make_move(position, self.direction, _map)
        assert type(move) == Point, f"{self.name} returned invalid move: {type(move)}."
        assert len(move) == 2, f"{self.name} requests invalid move: {move}"
        return move

    def get_strategy_name(self) -> str:
        return self.strategy_name
