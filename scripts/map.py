"""Module for reading and manipulating the game board"""
from __future__ import annotations

import copy
import logging
from pathlib import Path
from typing import Iterator, Optional, Union, overload

from .collision_behaviours import get_highest_priorityfn
from .entity import Entity
from .helper import Point

# from multimethod import multimethod


class Map:
    def __init__(self, map_file: Optional[Path]) -> None:
        self.steps_left = 25
        self.entities: list[Entity] = []
        # TODO: Collision map?
        if map_file:
            self.width, self.height = self._populate_entity_list(map_file)

    def update_creatures(self) -> None:
        """
        Update all Creatures using move_object
        Run conflict resolver
        """
        for entity in self.entities:
            entity.make_move(self.entities)

        self._collision_handler()

        self.steps_left -= 1
        if not self.steps_left:
            self.player.alive = False

        logging.debug(self)

    def _collision_handler(self) -> None:
        """
        Finds positions of collisions (collision_detector), wraps over them all (resolve_space) until all resolved
        """
        # Hours spent on collision resolution: 19.5
        # Would be more efficient to have a boolean table for "Does this tile need conflict resolution"
        collision_positions = self._collision_detector()

        # May want to initialise a second instance of map and collision positions for iterative resolutions:
        # new_map_nplus1 = new_map.copy()
        # collision_positions_nplus1 = []
        while collision_positions:
            current_collision_position = collision_positions.pop(0)
            positions_to_recheck = self._resolve_space(current_collision_position)
            collision_positions.extend(positions_to_recheck)

    def _resolve_space(self, position):
        """makes list of pairs (make_pairs), resolves pairs in priority order per get_highest_priorityfn"""
        entities_on_space = [e for e in self.entities if e.position == position]
        pairs = self._make_pairs(entities_on_space)
        moved_entities = []
        while pairs:
            temp_fn, pair = get_highest_priorityfn(pairs)
            pairs.remove(pair)
            # We pass pairs to remove objects from it that leave the space.
            moved_entities.extend(temp_fn(pair, pairs, entities_on_space))
        return [e.position for e in moved_entities]

    def _collision_detector(self) -> list[Point]:
        """
        Finds and returns all potential collision locations
        {} is set, to ensure uniqueness
        """
        # TODO: Only return positions with at-least 2 entities
        return sorted(list({entity.position for entity in self.entities}))

    def _make_pairs(
        self,
        entities_on_space: list,
    ) -> list[tuple[Entity, Entity]]:
        """
        Makes a list of pointers to each pair of creatures
        # TODO: Resolve entities in some order (order of arrival?). Currently alphabetical.
        Returns:
            list: All pairs of entities on space
        """
        num_entities = len(entities_on_space)
        return [
            (entities_on_space[x], entities_on_space[y])
            for x in range(num_entities)
            for y in range(x + 1, num_entities)
        ]

        # Something like below might instead resolve by alphabetical order
        # entity_pair = [new_map[current_collision_position][a] for a in current_collision_position]
        # entity_pair.sort(key = lambda ent: ent.get_strategy_name())
        # entity_strategies = [ent.get_strategy_name() for ent in entity_pair]

    def move_object(self, src: tuple, dst: tuple) -> None:
        """Uses conflict resolver"""
        pass

    def find_object(self, obj_name: str) -> tuple:
        """Get the coordinates of an object"""
        for entity in self.entities:
            if str(entity) == obj_name:
                return entity.position
        raise ValueError

    def copy(self) -> Map:
        new_map = Map(None)
        # TODO: Do we really need to deep copy?
        new_map.entities = copy.deepcopy(self.entities)
        return new_map

    def in_map(self, pos: tuple) -> bool:
        raise NotImplementedError
        # if pos[0] < 0 or pos[1] < 0:
        #     return False
        # return self.get_width() - 1 >= pos[1] and self.get_height() - 1 >= pos[0]

    def get_height(self) -> int:
        """Get the number of rows"""
        return self.height

    def get_width(self) -> int:
        """Get the number of cols"""
        return self.width

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
    def __getitem__(self, index: Union[tuple, Point]) -> list:
        ...

    def __getitem__(self, index: Union[int, tuple]) -> Union[list, list[list]]:
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

        _map = "┌" + "─" * self.get_width() + "┐\n" + _map
        _map = _map + "\n└" + "─" * self.get_width() + "┘"
        return _map

    def __len__(self) -> int:
        raise NotImplementedError

    def _new_entity_from_char(self, entity: str, point: Point):
        match entity:
            case "P":
                self.player = Entity("Player", "Player", position=point)
                self.entities.append(self.player)
            case "F":
                self.entities.append(Entity("FrogR", "NormalNorman", position=point))
            case "G":
                self.entities.append(Entity("FrogR", "NormalNorman", position=point))
                # TODO: Make this less ugly. Create AI object here instead of in entity?
                self.entities[-1].strategy.state = 3
            case "B":
                self.entities.append(
                    Entity("Barrel", "BarrelingBarrel", position=point)
                )
            case "W":
                self.entities.append(Entity("rockwall", solid=True, position=point))
            case "O":
                self.entities.append(Entity("Stone", solid=True, position=point))
            case "S":
                self.entities.append(Entity("FrogY", "SpiralingStacy", position=point))
            case "T":
                self.entities.append(Entity("FrogP", "TrickyTrent", position=point))

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
