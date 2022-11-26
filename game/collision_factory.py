"""Item factory for matching a pair of entities to their collision resolution function"""
import itertools
import logging
from collections import Counter

from .map import Map
from .world import world


class CollisionRegistryBase(type):

    COLLISION_REGISTRY: dict = {}

    def __new__(cls, name, bases, attrs):
        # instantiate a new type corresponding to the type of class being defined
        # this is currently RegisterBase but in child classes will be the child class
        new_cls = type.__new__(cls, name, bases, attrs)
        cls.COLLISION_REGISTRY[new_cls.__name__] = new_cls
        return new_cls

    @classmethod
    def get_registry(cls):
        return dict(cls.COLLISION_REGISTRY)


class BaseRegisteredCollisionClass(metaclass=CollisionRegistryBase):
    def get_priority(self, *args, **kwargs):
        """Get the priority of this collision rule in context.

        A priority of 0 means this collision rule isn't applicable.
        """
        raise NotImplementedError()

    def resolve_collision(self, *args, **kwargs):
        """
        Applies the collision rule
        """
        raise NotImplementedError()


class KillCollision(BaseRegisteredCollisionClass):
    @classmethod
    def get_priority(cls, *args, **kwargs):
        ...

    @classmethod
    def resolve_collision(cls, *args, **kwargs):
        ...


class CollisionFinder(object):
    @staticmethod
    def get_highest_priority_collision_for_pair(entity1, entity2):
        """Get the highest priority collision type for an entity pair"""
        tags = entity1.tags, entity2.tags

        highest_priority_collision = ""
        highest_priority = 0

        # Iterate over every collision type
        for collision_name in CollisionRegistryBase.COLLISION_REGISTRY:

            # Get a handle to the collision class
            collision_class = CollisionRegistryBase.COLLISION_REGISTRY[collision_name]

            # Call the class method get_priority on the collision class
            priority = collision_class.get_priority(*tags)
            if priority > highest_priority:
                highest_priority_collision = collision_name
                highest_priority = priority

            # Note: if we need to create an instance first
            # collision_instance = collision_class()
            # collision_instance.add_update_delete(*args, **kwargs)

        assert highest_priority, "No applicable collision for pair"
        return highest_priority_collision, highest_priority

    def get_highest_priority_collision_for_tile(self, point):
        """Get the highest priority collision type for a point in the world"""

        # Form a list containing all unique pairs of entities
        pairs = itertools.combinations(world[point], 2)

        highest_priority_collision = ""
        highest_priority_pair: list["Map"] = []
        highest_priority = 0

        for pair in pairs:
            collision_name, priority = self.get_highest_priority_collision_for_pair(*pair)
            if priority > highest_priority:
                highest_priority_collision = collision_name
                highest_priority = priority

        assert highest_priority, "No applicable collision for point"
        return highest_priority_collision, highest_priority_pair

    find_collision = get_highest_priority_collision_for_tile


class CollisionResolver(object):
    collision_finder = CollisionFinder()

    def resolve_highest_priority_collision(self, point):
        collision, pair = self.collision_finder.find_collision(point)
        collision_class = CollisionRegistryBase.COLLISION_REGISTRY[collision]
        collision_class.resolve_collision(pair)

    @staticmethod
    def get_points_to_check_for_collisions():
        points = [entity.position for entity in world.entities]
        counts = Counter(points)
        # No need to check collisions on a point with just one entity.
        # Convert to set to remove duplicates.
        points = {pos for pos in points if counts[id] > 1}
        return sorted(list(points))

    def resolve_highest_priority_collisions(self):
        """Resolve the highest priority collision at each point.

        Returns True if something happened"""
        points_to_check = self.get_points_to_check_for_collisions()
        if not points_to_check:
            return False
        for point in points_to_check:
            self.resolve_highest_priority_collision(point)
        return True

    def resolve_collisions(self):
        collisions_settled = False
        for _ in range(10):
            collisions_settled |= self.resolve_highest_priority_collisions()

        if not collisions_settled:
            # TODO: Resolve collisions more with logging.
            logging.error("Collisions didn't finish settling!")


collision_resolver = CollisionResolver()
