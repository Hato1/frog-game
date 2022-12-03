"""Registry of collision objects for resolving collision pairs.

To add a new collision type, simply create a new collision object that subclasses
CollisionRegistryBase and it'll be added to the registry automatically."""
from __future__ import annotations

import random
from typing import Type

from .entity import Entity, Tags
from .helper import DOWN, LEFT, RIGHT, UP, Point, get_facing_direction
from .map import current_map, maps


class CollisionRegistryBase:
    COLLISION_REGISTRY: dict[str, Type[CollisionRegistryBase]] = {}

    def __init__(self, entity1: Entity, entity2: Entity):
        self.entities = entity1, entity2

    @classmethod
    def __init_subclass__(cls, **kwargs):
        cls.COLLISION_REGISTRY[cls.__name__] = cls  # Add class to registry.

    @classmethod
    def get_registry(cls):
        return cls.COLLISION_REGISTRY

    def get_priority(self, *args, **kwargs) -> int:
        """Get the priority of this collision rule. Returns 0 if not applicable."""
        raise NotImplementedError()

    def resolve_collision(self, *args, **kwargs) -> None:
        """Applies the collision rule"""
        raise NotImplementedError()


class KillCollision(CollisionRegistryBase):
    def __init__(self, a, b):
        super().__init__(a, b)

        p = 0
        if Tags.player in a and Tags.kills_player in b:
            self.marked_frog = a
            p = 1
        elif Tags.player in b and Tags.kills_player in a:
            self.marked_frog = b
            p = 1
        elif Tags.hops in b and Tags.hops in a:
            self.marked_frog = random.choice(self.entities)
            p = 5
        self.priority = p

    def get_priority(self, **kwargs):
        return self.priority

    def resolve_collision(self, **kwargs):
        self.marked_frog.alive = False
        maps[current_map].cull_entities()


class PushCollision(CollisionRegistryBase):
    def __init__(self, a, b):
        super().__init__(a, b)

        p = 0
        if Tags.pushable in a and Tags.pusher in b:
            self.pusher = b
            self.pushable = a
            p = 10
        if Tags.pushable in b and Tags.pusher in a:
            self.pusher = a
            self.pushable = b
            p = 10
        if Tags.pusher in a and Tags.pusher in b and Tags.pushable in a and Tags.pushable in b:
            raise NotImplementedError("Both objects are Pushers and Pushable")
        self.priority = p

    def get_priority(self, **kwargs):
        return self.priority

    @classmethod
    def get_pushable_line(cls, pushable, direction, pushables):
        recurse = False
        new_pos = pushable.position + direction
        # There may be multiple things to push on this tile
        pushables = pushables or []
        for entity in maps[current_map][new_pos]:
            if Tags.solid in entity.tags or Tags.pusher in entity.tags:
                return entity
            elif Tags.pushable in entity.tags:
                recurse = True
                pushables.append(entity)
        if recurse:
            return cls.get_pushable_line(pushables[-1], direction, pushables)
        return False

    @classmethod
    def push(cls, pushable: Entity, direction: Point):
        pushables: list[Entity] = [pushable]
        blocked = cls.get_pushable_line(pushables[-1], direction, pushables)
        if not blocked:
            for pushable in pushables:
                pushable.position_history.append(pushable.position)
                pushable.position += direction
                # TODO: Barrel state change using enum or pushable.trigger(cls.__name__)
                if pushable.name == "Barrel":
                    next_state = [UP, DOWN, LEFT, RIGHT].index(direction) + 1
                    # TODO: Make this cleaner, with a middleman property in Entity, perhaps?
                    pushable.strategy.state = next_state
                    # TODO: Get facing direction should be part of setter for entity.
                    pushable.facing = get_facing_direction(direction, pushable.facing)
        return not blocked

    def resolve_collision(self, **kwargs):
        direction = self.pusher.position - self.pusher.position_history[-1]

        success = self.push(self.pushable, direction)
        if not success:
            self.pusher.position = self.pusher.position_history[-1]
