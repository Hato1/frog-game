"""Module for animate objects"""
from typing import Optional


class Entity():
    def __init__(self, name: str, solid: bool = False) -> None:
        """
        Args:
            name: A human friendly name
            solid: Does the object block the path?
        """
        # sprite?
        # orientation [1-4]
        self.name = name
        self.solid = solid


class Creature(Entity):
    def __init__(self, name: str) -> None:
        self.state = 0
        self.next_move: Optional[tuple] = None
        super(Creature, self).__init__(name)

    def get_next_move(self, position: tuple, map: list) -> tuple:
        if self.next_move:
            try:
                return self.next_move
            finally:
                self.next_move = None
        return position

    def update(self) -> tuple:
        # get position object wants to move to
        pass


class ai():
    def __init__(self, ai: str):
        pass
