"""Module for reading and maniuplating the game board"""
from entity import Creature, Entity
from pathlib import Path
from multimethod import multimethod
from typing import Iterator


class Map():
    def __init__(self, map_file: Path) -> None:
        # Map is structured as map[x][y][object]
        self.map = self._read_map(map_file)

    def update_creatures(self) -> None:
        """
        Update all Creatures using move_object
        Run conflict resolver
        """
        pass

    def move_object(self, src: tuple, dst: tuple) -> None:
        """Uses conflict resolver"""
        pass

    def find_object(self, obj_name: str) -> tuple:
        """Get the coordinates of an object, if it exists"""
        for row in self.map:
            for obj in row:
                if obj.name == obj_name:
                    return (self.map.index(row), row.index(obj)), obj
        return (-1, -1)

    @multimethod
    def __getitem__(self, index: int) -> list[list]:
        return self.map[index]

    @__getitem__.register
    def _(self, index: tuple) -> list:
        return self.map[index[0]][index[1]]

    def __iter__(self) -> Iterator:
        return iter(self.map)

    def __str__(self) -> str:
        """Get a human friendly representation of the map"""
        map_width = len(self.map[0]) + 2
        human_friendly = "-" * map_width + "\n|"
        for x in self.map:
            for y in x:
                # Add blank if this is a empty space
                # Add first character of entity name otherwise
                if not y:
                    human_friendly += " "
                else:
                    human_friendly += y[0].name[0]
            human_friendly += "|\n|"
        human_friendly
        return human_friendly[:-1] + "-" * map_width

    def __len__(self) -> int:
        return len(self.map)

    def _read_map(self, map_file: Path) -> list:
        """Read map from file"""
        pre_map: list[list[list]] = []
        with open(map_file) as f:
            for row in f.readlines():
                row = row.strip()
                if set(row) == {"-"}:
                    continue
                pre_map.append([])
                for col in row:
                    if col in ['|', '-']:
                        continue
                    pre_map[-1].append([])
                    if col == "P":
                        pre_map[-1][-1].append(Creature("Player"))
                    elif col == "F":
                        pre_map[-1][-1].append(Creature("Frog"))
                    elif col == "B":
                        pre_map[-1][-1].append(Entity("Barrel", True))
        return pre_map

    def _conflict_resolver(self, objects: list, map: list[list[list]]) -> None:
        # Update the conflicting square
        #
        pass
