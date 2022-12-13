"""Module for reading and manipulating the game board"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterator, Optional, overload

from game import db
from game.entity import Entity, Tags
from game.helper import Point
from gui.map_parser import get_dims, parse_entities


class Map:
    def __init__(self, map_file: Path) -> None:
        self.map_file: Path = map_file
        self.dims: Point = Point(0, 0)
        self.entities: list[Entity] = []
        self.player: Optional[Entity] = None
        self.reset()

    def reset(self):
        # TODO: Collision map?
        self.dims = get_dims(self.map_file)  # Should this be here? it will not change between resets
        self.entities = parse_entities(self.map_file)
        players = [entity for entity in self.entities if Tags.player in entity.tags]
        assert len(players) == 1, f"{len(players)} players found: {players}"
        self.player = players[0]
        db.worlds[self.map_file.stem] = self

    def update_creatures(self) -> None:
        """Update all Creatures using move_object"""
        for entity in self.entities:
            entity.make_move()
        logging.info(self)

    def cull_entities(self):
        # This should be in entities getter? less efficient, more readable?
        self.entities = [e for e in self.entities if e.alive]

    @property
    def height(self) -> int:
        """Get the number of rows"""
        return self.dims.y

    @property
    def width(self) -> int:
        """Get the number of cols"""
        return self.dims.x

    @overload
    def __getitem__(self, index: int) -> list:
        ...

    @overload
    def __getitem__(self, index: tuple | Point) -> list[Entity]:
        ...

    def __getitem__(self, index: int | tuple) -> list[Entity] | list[list]:
        """Retrieve elements of the map at the given row or (row, col) pair"""
        if isinstance(index, int):
            return [entity for entity in self.entities if entity.position.x == index]
        elif isinstance(index, (tuple, Point)):
            index = Point(*index)
            return [entity for entity in self.entities if entity.position == index]
        raise ValueError

    def __iter__(self) -> Iterator:
        self.entities.sort(key=lambda x: x.position)
        yield from self.entities

    def __str__(self) -> str:
        """Get a human friendly representation of the map"""
        _map = [[" "] * self.width for _col in range(self.height)]
        for entity in self.entities:
            pos = entity.position
            _map[pos.y][pos.x] = entity.name[0]

        _map = ["".join(row) for row in _map]
        _map = "│" + "│\n│".join(_map) + "│"

        _map = "\n┌" + "─" * self.width + "┐\n" + _map
        _map = _map + "\n└" + "─" * self.width + "┘"
        return _map

    def __len__(self) -> int:
        raise NotImplementedError


def reset_maps():
    # global maps
    for _map in db.worlds.values():
        _map.reset()


Map(Path("maps/stage_test"))
