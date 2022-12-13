"""Module for reading and manipulating the game board"""
from __future__ import annotations

import logging
from typing import Iterator, Optional, overload

from game.entity_base import Entity, Tags
from game.helper import Point, classproperty
from GAME_CONSTANTS import WORLD_NAME


class Map:
    worlds: dict[str, Map] = {}
    current_world_name = WORLD_NAME
    player: Optional[Entity] = None

    def __init__(self, map_name: str, entities: list[Entity], player, dims) -> None:
        self.map_name: str = map_name
        self.dims: Point = dims
        self.entities: list[Entity] = entities
        self.player: Entity = player
        self.worlds[self.map_name] = self

    def set_entities(self, entities):
        """Used to reset a map."""
        self.entities = entities

    def update_creatures(self) -> None:
        """Update all Creatures using move_object"""
        for entity in self.entities:
            new_position = entity.make_move()

            if any(Tags.solid in e for e in self.entities if e.position == new_position and e != entity):
                entity.position = entity.position_history[-1]
            assert self.is_in_map(new_position), f"{entity} tried to leave the play area at {new_position}!"
        logging.info(self)

    def is_in_map(self, point: Point) -> bool:
        """Return whether point lies in the map"""
        return 0 <= point.x < self.dims[0] and 0 <= point.y < self.dims[1]

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

    @classproperty
    def world(self) -> Map:
        return self.worlds[self.current_world_name]

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
