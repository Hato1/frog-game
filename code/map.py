"""Module for reading and maniuplating the game board"""
from __future__ import annotations
from entity import Creature, Entity
from pathlib import Path
from multimethod import multimethod
from typing import Iterator
import copy


class Map():
    def __init__(self, map_file: Path) -> None:
        # Map is structured as map[x][y][object]
        self.map = self._read_map(map_file)

    def update_creatures(self) -> None:
        """
        Update all Creatures using move_object
        Run conflict resolver
        """
        new_map = self.copy()
        moves_made: list = []
        for row in range(len(self)):
            for col in range(len(self[row])):
                pos = row, col
                for entity in self[pos]:
                    if type(entity) == Creature:
                        new_pos = entity.get_next_move(pos, self.map)
                        assert self.in_map(new_pos), f"{entity.name} Cheated!"
                        moves_made.append([entity, pos, new_pos])
                        for i in range(len(new_map[pos])):
                            if new_map[pos][i].name == entity.name:
                                new_map[pos].pop(i)
                        new_map[new_pos].append(entity)
        self.map = new_map.map

    def move_object(self, src: tuple, dst: tuple) -> None:
        """Uses conflict resolver"""
        pass

    def find_object(self, obj_name: str) -> tuple:
        """Get the coordinates of an object, if it exists"""
        for row in self.map:
            for col in row:
                for obj in col:
                    if obj.name == obj_name:
                        return (self.map.index(row), row.index(col)), obj
        return (-1, -1)

    def copy(self) -> Map:
        new = copy.deepcopy(self)
        #new.map = copy.copy(self.map)
        return new

    def in_map(self, pos: tuple) -> bool:
        if 0 > pos[0] or 0 > pos[1]:
            return False
        if self.height()-1 < pos[0] or self.width()-1 < pos[1]:
            return False
        return True

    def height(self) -> int:
        return len(self.map[0])

    def width(self) -> int:
        return len(self.map)

    @multimethod
    def __getitem__(self, index: int) -> list[list]:
        """Index into map with an int"""
        return self.map[index]

    @__getitem__.register
    def _(self, index: tuple) -> list:
        """Index into map with a tuple"""
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
                        pre_map[-1][-1].append(Creature("Frog", "NormalNorman"))
                    elif col == "B":
                        pre_map[-1][-1].append(Entity("Barrel", True))
        return pre_map

    def _conflict_resolver(self, objects: list, map: list[list[list]]) -> None:
        # Update the conflicting square
        #
        pass
