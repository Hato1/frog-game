"""Module for animate objects"""
from typing import Optional
from ai import NormalNorman, DeadDoug
AI_DICT = {"NormalNorman": NormalNorman, "DeadDoug": DeadDoug}


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
    def __init__(self, name: str, strategy: Optional[str] = None) -> None:
        self.state = 0
        if strategy:
            self.strategy = AI_DICT[strategy]()
        else:
            self.strategy = AI_DICT["DeadDoug"]()
        self.next_move: Optional[tuple] = None
        super(Creature, self).__init__(name)

    def get_next_move(self, position: tuple, _map: list) -> tuple:
        if self.next_move:
            try:
                return self.next_move
            finally:
                self.next_move = None
        move = self.strategy.get_move(position, _map)
        assert type(move) == tuple, f"{self.name} has a bad AI and you should feel bad."
        assert len(move) == 2, f"{self.name} has a bad AI and you should feel bad."
        return move

    def update(self) -> tuple:
        # get position object wants to move to
        pass


class Ai():
    def __init__(self, ai: str):
        pass
