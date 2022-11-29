import itertools
import logging
from collections import Counter
from typing import Optional

from game.collision_factory import CollisionRegistryBase

from .entity import Entity
from .helper import IndentedLogging, Point, c
from .map import current_map, maps


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
            try:
                priority = collision_class.get_priority(*tags)
            except NotImplementedError:
                continue
            if priority > highest_priority:
                highest_priority_collision = collision_name
                highest_priority = priority

            # Note: if we need to create an instance first
            # collision_instance = collision_class()
            # collision_instance.add_update_delete(*args, **kwargs)

        assert highest_priority, f"No applicable collision for pair: {entity1} and {entity2}."
        return highest_priority_collision, highest_priority

    def get_highest_priority_collision_for_tile(self, point: Point, log=None):
        """Get the highest priority collision type for a point in the world"""

        # Form a list containing all unique pairs of entities
        entities_here = maps[current_map][point]
        pairs = itertools.combinations(entities_here, 2)

        highest_priority_collision = ""
        highest_priority_pair: Optional[tuple[Entity, Entity]] = None
        highest_priority = 0

        for pair in pairs:
            collision_name, priority = self.get_highest_priority_collision_for_pair(*pair)
            if log and priority:
                log(
                    f"Found {collision_name} for {', '.join(str(x) for x in pair)}. Priority={priority}"
                )
            if priority > highest_priority:
                highest_priority_collision = collision_name
                highest_priority_pair = pair
                highest_priority = priority

        assert highest_priority, "No applicable collision for point."
        if log:
            msg = c(f"Chose {highest_priority_collision} for ", fg="g")
            msg += ", ".join(str(x) for x in highest_priority_pair) + "."
            log(msg)

        return highest_priority_collision, highest_priority_pair

    find_collision = get_highest_priority_collision_for_tile


class CollisionResolver(object):
    collision_finder = CollisionFinder()

    def resolve_highest_priority_collision(self, point, log=None):
        collision, pair = self.collision_finder.find_collision(point, log)
        collision_class = CollisionRegistryBase.COLLISION_REGISTRY[collision]
        try:
            collision_class.resolve_collision(*pair)
        except NotImplementedError as e:
            msg = f"{collision} is not implemented"
            msg += f": {e}" if len(str(e)) else ""
            if log:
                log(c(msg + ".", fg="r"))
            else:
                logging.warning(msg)

    @staticmethod
    def get_points_to_check_for_collisions():
        points = [entity.position for entity in maps[current_map].entities if entity.alive]
        counts = Counter(points)
        # No need to check collisions on a point with just one entity.
        # Convert to set to remove duplicates.
        points = {p for p in points if counts[p] > 1}
        return sorted(list(points))

    def resolve_highest_priority_collisions(self, log=None):
        """Resolve the highest priority collision at each point.

        Returns True if something happened"""
        points_to_check = self.get_points_to_check_for_collisions()
        if not points_to_check:
            return True
        for point in points_to_check:
            if log:
                entities = [e for e in maps[current_map][point] if e.alive]
                log(f"{point} contains {entities}")
            self.resolve_highest_priority_collision(point, log)
        return False

    def resolve_collisions(self):
        collisions_settled = False
        log = IndentedLogging(logging.debug)
        for _ in range(10):
            collisions_settled |= self.resolve_highest_priority_collisions(log)
            if collisions_settled:
                return

        # TODO: Resolve collisions more with logging.
        logging.error("Collisions didn't finish settling! Enabling verbose mode.")
        log = IndentedLogging(logging.error)
        for i in range(3):
            log(f"Iteration {i}")
            self.resolve_highest_priority_collisions(log=log)


collision_resolver = CollisionResolver()
