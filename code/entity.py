"""Module for animate objects"""


class Entity():
    def __init__(self, name: str) -> None:
        # sprite
        # orientation [1-4]
        # blocking?
        self.name = name


class Creature(Entity):
    def __init__(self, name: str) -> None:
        # state
        # super init
        super(Creature, self).__init__(name)

    def update(self) -> tuple:
        # get position object wants to move to
        pass


class ai():
    def __init__(self, ai: str):
        pass
