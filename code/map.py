"""Module for reading and maniuplating the game board"""
from __future__ import annotations
from entity import Creature, Entity
from pathlib import Path
from multimethod import multimethod
from typing import Iterator, Optional
from helper import Vector


class Map():
    def __init__(self, map_file: Optional[Path]) -> None:
        # Map is structured as map[row][col][object]
        if map_file:
            self.map = self._read_map(map_file)
        else:
            self.map = []

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
                        new_pos = entity.get_next_move(Vector(pos), self.map)
                        assert self.in_map(new_pos), f"{entity.name} Cheated!"
                        moves_made.append([entity, pos, new_pos])
                        for i in range(len(new_map[pos]))[::-1]:
                            y = new_map[pos]
                            x = y[i]
                            if x.id == entity.id:
                                new_map[pos].pop(i)
                        new_map[new_pos].append(entity)
        self.map = new_map.map

    def move_object(self, src: tuple, dst: tuple) -> None:
        """Uses conflict resolver"""
        pass

    def find_object(self, obj_name: str) -> tuple:
        """Get the coordinates of an object, if it exists"""
        for row in range(self.get_width()):
            for col in range(self.get_height()):
                for obj in self[row, col]:
                    if obj.name == obj_name:
                        return (row, col), obj
        return (-1, -1)

    def copy(self) -> Map:
        new_map = Map(None)
        for row in self.map:
            new_map.map.append([])
            for entities in row:
                new_map.map[-1].append([])
                for entity in entities:
                    new_map.map[-1][-1].append(entity)
        return new_map

    def in_map(self, pos: tuple) -> bool:
        if 0 > pos[0] or 0 > pos[1]:
            return False
        if self.get_width()-1 < pos[0] or self.get_height()-1 < pos[1]:
            return False
        return True

    def get_height(self) -> int:
        return len(self.map)

    def get_width(self) -> int:
        return len(self.map[0])

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
                    elif col == "G":
                        pre_map[-1][-1].append(Creature("Frog", "NormalNorman"))
                        pre_map[-1][-1][-1].strategy.state = 3
                    elif col == "B":
                        pre_map[-1][-1].append(Entity("Barrel"))
                    elif col == "W":
                        pre_map[-1][-1].append(Entity("rockwall", True))
                    elif col == "S":
                        pre_map[-1][-1].append(Creature("Frog", "SpiralingStacy"))
        return pre_map

    def _conflict_resolver(self, objects: list, map: list[list[list]]) -> None:
        # Update the conflicting square
        #
        pass
