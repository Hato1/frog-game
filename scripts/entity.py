"""Module for animate objects"""
from typing import Optional
from .helper import Vector, facing
from .ai import NormalNorman, DeadDoug, SpiralingStacy, BarrelingBarrel, TrickyTrent
AI_DICT = {
    "NormalNorman": NormalNorman,
    "DeadDoug": DeadDoug,
    "SpiralingStacy": SpiralingStacy,
    "BarrelingBarrel": BarrelingBarrel,
    "TrickyTrent": TrickyTrent,
}
UP, RIGHT, DOWN, LEFT = range(4)


class Entity():
    """Entities do not move"""
    next_id = 0

    def __init__(
        self,
        name: str,
        solid: bool = False,
        direction: int = UP
    ) -> None:
        """
        Args:
            name: A human friendly name
            solid: Does the object block the path?
        """
        self.id = Entity.next_id
        Entity.next_id += 1
        self.name = name
        self.solid = solid
        self.direction = direction

    def __str__(self):
        return self.name


class Creature(Entity):
    """Creatures do move"""
    def __init__(
        self,
        name: str,
        strategy: Optional[str] = "DeadDoug",
        direction: int = UP
    ) -> None:
        """
        Args:
            strategy: name of creature AI, decides the creatures movement pattern
            direction: which way the creature is initially facing"""
        self.state = 0
        self.strategy = AI_DICT[strategy]()
        # Can be used to force creatures next move, ignoring their strategy.
        self.next_move: Optional[tuple] = None
        super(Creature, self).__init__(name, direction)

    def get_next_move(self, position: tuple, _map: list) -> tuple:
        if self.next_move:
            self.direction = facing(self.next_move-position, self.direction)
            try:
                return self.next_move
            finally:
                self.next_move = None
        move, self.direction = self.strategy.make_move(position, self.direction, _map)
        assert type(move) == Vector, f"{self.name} returned invalid move: {type(move)}."
        assert len(move) == 2, f"{self.name} requests invalid move: {move}"
        return move
