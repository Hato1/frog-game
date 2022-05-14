"""Module for reading and maniuplating the game board"""
from entity import Creature, Entity
from pathlib import Path


class Map():
    def __init__(self) -> None:
        # create map
        # Map is structured as map[x][y][object]
        self.map: list[list[list]]
        self.map = self._read_map(Path("maps/map1"))

    def __getitem__(self, index: int) -> list[list]:
        return self.map[index]

    def move_object(self, src: tuple, dst: tuple) -> None:
        pass

    def _read_map(self, map_file: Path) -> list:
        """Read map from file"""
        pre_map: list[list[list]] = []
        with open(map_file) as f:
            for row in f.readlines():
                row = row.strip()
                pre_map.append([])
                for col in row:
                    if col in ['|', '-']:
                        continue
                    pre_map[-1].append([])
                    if col == "P":
                        pre_map[-1][-1].append(Creature("Player"))
                    elif col == "F":
                        pre_map[-1][-1].append(Creature("Frog"))
                    elif col == "R":
                        pre_map[-1][-1].append(Entity("Rock"))
        return pre_map

    def _conflict_resolver(self, objects: list, map: list[list[list]]) -> None:
        # Update the conflicting square
        #
        pass
