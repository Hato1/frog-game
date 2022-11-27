"""Module for reading and manipulating the game board"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable, Iterator, overload

from game import ai
from game.collision_behaviours import get_highest_priority_fn
from game.entity import Entity, Tags
from game.helper import Point
from GAME_CONSTANTS import WORLD_NAME

# from multimethod import multimethod
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
        """
        Update all Creatures using move_object
        Run conflict resolver
        """
        for entity in self.entities:
            entity.make_move(self.entities, Point(MAP_WIDTH, MAP_HEIGHT))

        # self._collision_handler()

        self.steps_left -= 1
        if not self.steps_left:
            self.player.alive = False

        logging.info(self)

    def cull_entities(self):
        self.entities = [e for e in self.entities if e.alive]

    def _collision_handler(self) -> None:
        """Resolves all collisions.

        Find positions of collisions (collision_detector) and iteratively resolve them (resolve_space)

        Hours spent on collision resolution: 26
        """
        # Would be more efficient to have a boolean table for "Does this tile need conflict resolution"
        collision_points = self._collision_detector()

        # Initialise a number of collisions resolved, to throw an error if it loops
        num_collisions_resolved = 0

        while collision_points:
            current_collision_position = collision_points.pop(0)

            positions_to_recheck, num_collisions_resolved = self._resolve_space(
                current_collision_position,
                num_collisions_resolved,
                verbose=num_collisions_resolved > 1000,
            )
            assert num_collisions_resolved < 1015, "Infinite loop in collision resolution!"
            # TODO: make sure there aren't duplicate points causing trouble
            collision_points.extend(positions_to_recheck)

    def _resolve_space(
        self,
        position: Point,
        num_collisions_resolved: int,
        verbose: bool = False,
    ) -> tuple[list[Point], int]:
        """Resolves all collisions on a single point.

        makes list of entity pairs (make_pairs), resolves pairs in priority order per get_highest_priorityfn
        returns (points_to_recheck, num_resolved_cols)"""
        entities_on_space = [e for e in self.entities if e.position == position]
        pairs = self._make_pairs(entities_on_space)
        moved_entities = []
        while pairs:
            highest_priority_fn, pair = get_highest_priority_fn(pairs)
            pairs.remove(pair)
            # We pass pairs to remove objects from it that leave the space.
            bits = {
                "pair": pair,
                "pairs": pairs,
                "entities_on_space": entities_on_space,
                "entity_list": self.entities,
                "the_map": self,
            }
            moved_entities.extend(highest_priority_fn(bits))
            num_collisions_resolved += 1
            if verbose:
                self.log_collision_resolution(highest_priority_fn, pair)
        return [e.position for e in moved_entities], num_collisions_resolved

    def _collision_detector(self) -> list[Point]:
        """
        Finds and returns all potential collision locations
        {} is set, to ensure uniqueness
        """
        # TODO: Only return positions with at least 2 entities
        return sorted(list({entity.position for entity in self.entities}))

    @staticmethod
    def _make_pairs(
        entities_on_space: list,
    ) -> list[tuple[Entity, Entity]]:
        """Generate all unique combinations of entity pairs."""
        num_entities = len(entities_on_space)
        return [
            (entities_on_space[x], entities_on_space[y])
            for x in range(num_entities)
            for y in range(x + 1, num_entities)
        ]

    @staticmethod
    def log_collision_resolution(temp_fn: Callable, pair: tuple) -> None:
        """if infinite loop, prints an error with a few useful diagnostics"""
        logging.error(
            f"Traceback: Used resolution function '{temp_fn.__qualname__}' at {pair[0].position} on {[e.get_strategy_name() for e in pair]}"
        )

    def move_object(self, src: tuple, dst: tuple) -> None:
        """Uses conflict resolver"""
        pass

    def find_object(self, obj_name: str) -> tuple:
        """Get the coordinates of an object"""
        for entity in self.entities:
            if str(entity) == obj_name:
                return entity.position
        raise ValueError

    # def copy(self) -> Map:
    #     new_map = Map(None)
    #     # TODO: Do we really need to deep copy?
    #     new_map.entities = copy.deepcopy(self.entities)
    #     return new_map

    def in_map(self, pos: tuple) -> bool:
        raise NotImplementedError
        # if pos[0] < 0 or pos[1] < 0:
        #     return False
        # return self.get_width() - 1 >= pos[1] and self.get_height() - 1 >= pos[0]

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
                self.entities.append(
                    Entity("rockwall", position=point, tags=[Tags.solid, Tags.no_animation])
                )
            case "O":
                self.entities.append(
                    Entity("Stone", position=point, tags=[Tags.solid, Tags.no_animation])
                )
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
