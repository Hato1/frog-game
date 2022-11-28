"""Item factory for matching a pair of entities to their collision resolution function"""
from __future__ import annotations

import random
from typing import Type

from .entity import Tags
from .map import current_map, maps


class CollisionRegistryBase:
    COLLISION_REGISTRY: dict[str, Type[CollisionRegistryBase]] = {}

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.COLLISION_REGISTRY[cls.__name__] = cls  # Add class to registry.

    @classmethod
    def get_registry(cls):
        return cls.COLLISION_REGISTRY

    def get_priority(self, *args, **kwargs) -> int:
        """Get the priority of this collision rule in context.

        A priority of -1 means this collision rule isn't applicable.
        """
        raise NotImplementedError()

    def resolve_collision(self, *args, **kwargs) -> None:
        """Applies the collision rule"""
        raise NotImplementedError()


class KillCollision(CollisionRegistryBase):
    @classmethod
    def get_priority(cls, tags1, tags2, **kwargs):
        priority = -1
        if Tags.player in tags1 and Tags.kills_player in tags2:
            priority = 1
        elif Tags.player in tags2 and Tags.kills_player in tags1:
            priority = 1
        elif Tags.hops in tags1 and Tags.hops in tags2:
            priority = 5
        return priority

    @classmethod
    def resolve_collision(cls, entity1, entity2, **kwargs):
        tags1, tags2 = entity1.tags, entity2.tags
        if Tags.player in tags1 and Tags.kills_player in tags2:
            entity1.alive = False
        elif Tags.player in tags2 and Tags.kills_player in tags1:
            entity2.alive = False
        elif Tags.hops in tags1 and Tags.hops in tags2:
            random.choice([entity1, entity2]).alive = False
        maps[current_map].cull_entities()


class PushCollision(CollisionRegistryBase):
    @classmethod
    def get_priority(cls, tags1, tags2, **kwargs):
        priority = -1
        if Tags.pushable in tags1 and Tags.pusher in tags2:
            priority = 10
        if Tags.pushable in tags2 and Tags.pusher in tags1:
            priority = 10
        return priority

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
    def push(cls, pushable, direction):
        pushables = [pushable]
        blocked = cls.get_pushable_line(pushables[-1], direction, pushables)
        if not blocked:
            for pushable in pushables:
                pushable.position_history.append(pushable.position)
                pushable.position += direction
                # TODO: Barrel state change using enum or pushable.trigger(cls.__name__)
        return not blocked

    @classmethod
    def resolve_collision(cls, entity1, entity2, **kwargs):
        tags1, tags2 = entity1.tags, entity2.tags
        pusher = None
        pushable = None
        if Tags.pusher in tags1 and Tags.pushable in tags2:
            pusher, pushable = entity1, entity2
        if Tags.pusher in tags2 and Tags.pushable in tags1:
            if pusher:
                raise NotImplementedError("Both objects are Pushers and Pushable")
            pusher, pushable = entity2, entity1
        direction = pusher.position - pusher.position_history[-1]

        success = cls.push(pushable, direction)
        if not success:
            pusher.position = pusher.position_history[-1]
