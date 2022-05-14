"""Module for animate objects"""


class Entity():
    def __init__(self, name: str, solid: bool = False) -> None:
        """
        Args:
            name: A human friendly
            solid: Does the object block the path?
        """
        # sprite?
        # orientation [1-4]
        self.name = name
        self.solid = solid


class Creature(Entity):
    def __init__(self, name: str) -> None:
        # state
        # super init
        self.next_move = None
        super(Creature, self).__init__(name)

    def update(self) -> tuple:
        # get position object wants to move to
        pass


class ai():
    def __init__(self, ai: str):
        pass
