"""Module for reading and manipulating the game board"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterator, overload

from game.entity import *
from game.helper import Point
from GAME_CONSTANTS import WORLD_NAME

# TODO: Insert these as per instance variable with class method getter which Pulls from current_map's dims
maps: dict[str, Map] = {}
current_map: str = WORLD_NAME


class Map:
    def __init__(self, map_file: Path) -> None:
        self.map_file: Path = map_file
        # TODO: Move max_steps & steps_left into the Entity/AI.
        self.max_steps: int = 50
        self.steps_left: int = 0
        self.dims: Point = Point(0, 0)
        self.entities: list[Entity] = []
        self.reset()

    def reset(self):
        self.steps_left = self.max_steps
        self.entities = []
        # TODO: Collision map?
        self.dims = self._populate_entity_list(self.map_file)
        maps[self.map_file.stem] = self

    def update_creatures(self) -> None:
        """Update all Creatures using move_object"""
        for entity in self.entities:
            # TODO: Remove need to send through entity list with some global access to worlds.
            entity.do_move(self.entities, Point(*self.dims))

        # Todo: Move steps left into Entity
        self.steps_left -= 1
        if not self.steps_left:
            self.player.alive = False

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

    def _new_entity_from_char(self, entity: str, point: Point):
        match entity:
            case "P":
                self.player = Player(
                    "Player",
                    position=point,
                    tags=[Tags.hops, Tags.pusher, Tags.player],
                )
                self.entities.append(self.player)
            case "F":
                self.entities.append(
                    NormalNorman(
                        "FrogR",
                        position=point,
                        tags=[Tags.hops, Tags.kills_player, Tags.pusher],
                    )
                )
            case "G":
                self.entities.append(
                    NormalNorman(
                        "FrogR",
                        position=point,
                        tags=[Tags.hops, Tags.kills_player, Tags.pusher],
                    )
                )
                # TODO: Make this less ugly. Create AI object here instead of in entity?
                self.entities[-1].state = 3
            case "B":
                self.entities.append(
                    BarrelingBarrel(
                        "Barrel",
                        position=point,
                        tags=[Tags.pushable, Tags.barrel],
                    )
                )
            case "W":
                self.entities.append(Wall("rockwall", position=point, tags=[Tags.solid, Tags.no_animation]))
            case "O":
                self.entities.append(Stone("Stone", position=point, tags=[Tags.solid, Tags.no_animation]))
            case "S":
                self.entities.append(
                    SpiralingStacy(
                        "FrogY",
                        position=point,
                        tags=[Tags.hops, Tags.kills_player, Tags.pusher],
                    )
                )
            case "T":
                self.entities.append(
                    TrickyTrent(
                        "FrogP",
                        position=point,
                        tags=[Tags.hops, Tags.kills_player, Tags.pusher],
                    )
                )
            case "L":
                self.entities.append(
                    SlidingStone(
                        "SlidingStone",
                        position=point,
                        tags=[Tags.pushable, Tags.no_animation],
                    )
                )

    def _populate_entity_list(self, map_file: Path) -> Point:
        """Read entities from a map file and insert them into the entity list"""
        with open(map_file) as file:
            y = 0
            max_x = 0
            for line in file:
                x = 0
                line = line.strip()
                if set(line) == {"-"}:
                    continue
                for char in line:
                    if char in ["|", "-"]:
                        continue
                    self._new_entity_from_char(char, Point(x, y))
                    x += 1
                    max_x = max(x, max_x)
                y += 1
        return Point(max_x, y)

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
    global maps
    for _map in maps.values():
        _map.reset()


Map(Path(f"maps/{WORLD_NAME}"))
