"""Module for reading and maniuplating the game board"""
from entity import Entity


class Map():
    def __init__(self) -> None:
        # create map
        # Map is structured as map[x][y][object]
        self.map = [[None, None], [None, Entity()]]

    def move_object(self, src: tuple, dst: tuple) -> None:
        pass

    def _parse_map(self, map_string: str) -> list:
        return []

    def _map_builder(self) -> None:
        """Create the game board in a user friendly manner"""
        self.map = self._parse_map(
            "          "
            "          "
            "     P    "
            "          "
            "          "
        )

    def _conflict_resolver(self, objects: list, map: list[list[list]]) -> None:
        # Update the conflicting square
        #
        pass
