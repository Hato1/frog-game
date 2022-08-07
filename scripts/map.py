"""Module for reading and maniuplating the game board"""
from __future__ import annotations
from .entity import Creature, Entity
from pathlib import Path
from multimethod import multimethod
from typing import Iterator, Optional
from .helper import Point
from .collision_resolver import collision_resolver

class Map():
    def __init__(self, map_file: Optional[Path]) -> None:
        self.player = Creature("Player")
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
        for pos, entities in self._iterate():
            for entity in entities:
                if type(entity) == Creature:
                    new_pos = entity.get_next_move(pos, self.map)
                    assert self.in_map(new_pos), f"{entity.name} Cheated!"
                    moves_made.append([entity, pos, new_pos])

                    # This moves the man
                    for i in range(len(new_map[pos]))[::-1]:
                        newentitylist = new_map[pos]
                        entitytomove = newentitylist[i]
                        if entitytomove.id == entity.id:
                            new_map[pos].pop(i)
                    new_map[new_pos].append(entity)
                    entity.position = new_pos
        self._collision_detector(new_map, moves_made)
        self.map = new_map.map

    def move_object(self, src: tuple, dst: tuple) -> None:
        """Uses conflict resolver"""
        pass

    def find_object(self, obj_name: str) -> tuple:
        """Get the coordinates of an object, if it exists"""
        for pos, entities in self._iterate():
            for entity in entities:
                if entity.name == obj_name:
                    return pos, entity
        # for row in range(self.get_nrows()):
        #     for col in range(self.get_ncols()):
        #         for obj in self[row, col]:
        #             if obj.name == obj_name:
        #                 print(row, col)
        #                 return Point(row, col), obj
        assert False
        # return Point(-1, -1)

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
        if self.get_width()-1 < pos[1] or self.get_height()-1 < pos[0]:
            return False
        return True

    def get_nrows(self) -> int:
        """Get the height of the map"""
        return len(self.map)

    def get_ncols(self) -> int:
        """Get the width of the map"""
        return len(self.map[0])

    def get_height(self) -> int:
        """Get the number of rows"""
        return self.get_nrows()

    def get_width(self) -> int:
        """Get the number of cols"""
        return self.get_ncols()

    def is_player_alive(self) -> bool:
        return self.player.alive

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

    def _iterate(self) -> Iterator[tuple[Point, list]]:
        for row in range(self.get_nrows()):
            for col in range(self.get_ncols()):
                yield Point(row, col), self[row][col]

    def __str__(self) -> str:
        """Get a human friendly representation of the map"""
        map_ncols = len(self.map[0]) + 2
        human_friendly = "-" * map_ncols + "\n|"
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
        return human_friendly[:-1] + "-" * map_ncols

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
                        pre_map[-1][-1].append(self.player)
                        self.player.position = Point(len(pre_map)-1, len(pre_map[-1])-1)
                    elif col == "F":
                        pre_map[-1][-1].append(Creature("FrogR", "NormalNorman"))
                    elif col == "G":
                        pre_map[-1][-1].append(Creature("FrogR", "NormalNorman"))
                        pre_map[-1][-1][-1].strategy.state = 3
                    elif col == "B":
                        pre_map[-1][-1].append(Entity("Barrel"))
                    elif col == "W":
                        pre_map[-1][-1].append(Entity("rockwall", True))
                    elif col == "O":
                        pre_map[-1][-1].append(Entity("Stone", True))
                    elif col == "S":
                        pre_map[-1][-1].append(Creature("FrogY", "SpiralingStacy"))
                    elif col == "T":
                        pre_map[-1][-1].append(Creature("FrogP", "TrickyTrent"))
        return pre_map

    def _collision_detector(self, new_map: Map, moves_made: list) -> None:
        """calls collision_sorter on all tiles untill no conflicts are reported"""
        #proposed_map = self.copy()
        collision_locs = [(x, y) for x in range(self.get_nrows()) for y in range(self.get_ncols())]
        while collision_locs != []:
            # This is bad, and only runs one pass of conflict resolution
            collision_pos = collision_locs.pop(0)
            self._collision_sorter(collision_pos, new_map, collision_locs)

    def _collision_sorter(self, collision_pos: tuple, new_map: Map, collision_locs: list) -> None:
        """sorts conflicts on the given tile, calls collision_resolver for each* """
        creatures = new_map[collision_pos]
        num_creatures = len(creatures)
        if num_creatures < 2:
            return
        remaining_pairs = [(x, y) for x in range(num_creatures) for y in range(x+1, num_creatures)]
        while remaining_pairs != []:
            current_collision = remaining_pairs.pop()
            collision_resolver(current_collision, remaining_pairs, collision_pos, new_map, collision_locs)
