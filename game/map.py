"""Module for reading and manipulating the game board"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterator, overload

from game import ai
from game.entity import Entity, Tags
from game.helper import Point
from GAME_CONSTANTS import WORLD_NAME

MAP_WIDTH = 0
MAP_HEIGHT = 0
maps: dict[str, Map] = {}
current_map: str = WORLD_NAME


class Map:
    def __init__(self, map_file: Path) -> None:
        self.map_file = map_file
        self.steps_left = 0
        self.entities: list[Entity] = []
        self.reset()

    def update_creatures(self) -> None:
        """Update all Creatures using move_object"""
        for entity in self.entities:
            entity.make_move(self.entities, Point(MAP_WIDTH, MAP_HEIGHT))

        self.steps_left -= 1
        if not self.steps_left:
            self.player.alive = False

        logging.info(self)

    def cull_entities(self):
        self.entities = [e for e in self.entities if e.alive]

    def find_object(self, obj_name: str) -> tuple:
        """Get the coordinates of an object"""
        for entity in self.entities:
            if str(entity) == obj_name:
                return entity.position
        raise ValueError

    @staticmethod
    def get_height() -> int:
        """Get the number of rows"""
        return MAP_HEIGHT

    @staticmethod
    def get_width() -> int:
        """Get the number of cols"""
        return MAP_WIDTH

    def get_steps_left(self) -> int:
        """Get the number of remaining steps"""
        # Todo: Decide whether to insert into entity?
        return self.steps_left

    def is_player_alive(self) -> bool:
        return self.player.alive

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
        _map = [[" "] * self.get_width() for _col in range(self.get_height())]
        for entity in self.entities:
            pos = entity.position
            _map[pos.y][pos.x] = entity.name[0]

        _map = ["".join(row) for row in _map]
        _map = "│" + "│\n│".join(_map) + "│"

        _map = "\n┌" + "─" * self.get_width() + "┐\n" + _map
        _map = _map + "\n└" + "─" * self.get_width() + "┘"
        return _map

    def __len__(self) -> int:
        raise NotImplementedError

    def _new_entity_from_char(self, entity: str, point: Point):
        match entity:
            case "P":
                self.player = Entity(
                    "Player",
                    ai.IdleIvan(),
                    position=point,
                    tags=[Tags.hops, Tags.pusher, Tags.player],
                )
                self.entities.append(self.player)
            case "F":
                self.entities.append(
                    Entity(
                        "FrogR",
                        ai.NormalNorman(),
                        position=point,
                        tags=[Tags.hops, Tags.kills_player, Tags.pusher],
                    )
                )
            case "G":
                self.entities.append(
                    Entity(
                        "FrogR",
                        ai.NormalNorman(),
                        position=point,
                        tags=[Tags.hops, Tags.kills_player, Tags.pusher],
                    )
                )
                # TODO: Make this less ugly. Create AI object here instead of in entity?
                self.entities[-1].strategy.state = 3
            case "B":
                self.entities.append(
                    Entity(
                        "Barrel",
                        ai.BarrelingBarrel(),
                        position=point,
                        tags=[Tags.pushable, Tags.barrel],
                    )
                )
            case "W":
                self.entities.append(Entity("rockwall", position=point, tags=[Tags.solid, Tags.no_animation]))
            case "O":
                self.entities.append(Entity("Stone", position=point, tags=[Tags.solid, Tags.no_animation]))
            case "S":
                self.entities.append(
                    Entity(
                        "FrogY",
                        ai.SpiralingStacy(),
                        position=point,
                        tags=[Tags.hops, Tags.kills_player, Tags.pusher],
                    )
                )
            case "T":
                self.entities.append(
                    Entity(
                        "FrogP",
                        ai.TrickyTrent(),
                        position=point,
                        tags=[Tags.hops, Tags.kills_player, Tags.pusher],
                    )
                )
            case "L":
                self.entities.append(
                    Entity(
                        "SlidingStone",
                        ai.IdleIvan(),
                        position=point,
                        tags=[Tags.pushable, Tags.no_animation],
                    )
                )

    def _populate_entity_list(self, map_file: Path) -> tuple[int, int]:
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
        return max_x, y

    def get_entities(self):
        return self.entities

    def reset(self):
        self.steps_left = 50
        self.entities = []
        # TODO: Collision map?
        global MAP_WIDTH
        global MAP_HEIGHT
        MAP_WIDTH, MAP_HEIGHT = self._populate_entity_list(self.map_file)
        maps[self.map_file.stem] = self


def reset_maps():
    global maps
    for _map in maps.values():
        _map.reset()


Map(Path(f"maps/{WORLD_NAME}"))
