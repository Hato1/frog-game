"""
Find collisions in the world and resolve them with the registered collision types in collision registry.
The only function that should be needed elsewhere is resolve_collisions.
"""
import itertools
import logging
from collections import Counter
from typing import Iterable, Optional, Type

from game.collision_registry import CollisionRegistryBase
from game.entity import Entity
from game.helper import IndentedLogging, Point, c
from game.map import Map


def get_collision_for_pair(log, pair) -> CollisionRegistryBase:
    """Get the highest priority collision type for an entity pair"""
    highest: Optional[CollisionRegistryBase] = None

    # Iterate over every collision type
    for collision_name in CollisionRegistryBase.COLLISION_REGISTRY:

        # Get a handle to the collision class, and create an instance of it
        collision_class: Type[CollisionRegistryBase] = CollisionRegistryBase.COLLISION_REGISTRY[collision_name]
        collision_instance: CollisionRegistryBase = collision_class(*pair)

        if not highest or collision_instance.get_priority() > highest.get_priority():
            highest = collision_instance

    assert highest and highest.get_priority(), f"No applicable collision for pair: {pair[0]} and {pair[1]}."
    log(f"Found {type(highest).__name__} for {', '.join(str(x) for x in pair)}. Priority={highest.get_priority()}")
    return highest


def get_collision_for_tile(log, point: Point) -> CollisionRegistryBase:
    """Get the highest priority collision type for a point in the world"""
    entities_here: list[Entity] = Map.world[point]
    # Form a list containing all unique pairs of entities
    pairs: Iterable[tuple[Entity, Entity]] = itertools.combinations(entities_here, 2)
    highest: Optional[CollisionRegistryBase] = None

    for pair in pairs:
        collision_instance = get_collision_for_pair(log, pair)
        if not highest or collision_instance.get_priority() > highest.get_priority():
            highest = collision_instance

    assert highest and highest.get_priority(), f"No applicable collision at {Point} with entities: {entities_here}"
    log(c(f"Chose {type(highest).__name__} for ", fg="g") + ", ".join(str(x) for x in highest.entities) + ".")
    return highest


find_collision = get_collision_for_tile


def resolve_highest_priority_collision(log, point):
    collision_instance = find_collision(log, point)
    try:
        collision_instance.resolve_collision()
    except NotImplementedError as e:
        msg = f"{type(collision_instance).__name__} is not implemented"
        msg += f": {e}" if len(str(e)) else ""
        log(c(f"{msg}.", fg="r"))


def get_points_to_check_for_collisions():
    points = [entity.position for entity in Map.world.entities if entity.alive]
    counts = Counter(points)
    # No need to check collisions on a point with just one entity.
    # Convert to set to remove duplicates.
    points = {p for p in points if counts[p] > 1}
    return sorted(list(points))


def resolve_highest_priority_collisions(log):
    """Resolve the highest priority collision at each point.

    Returns True if something happened"""
    points_to_check = get_points_to_check_for_collisions()
    if not points_to_check:
        return True
    for point in points_to_check:
        entities = [e for e in Map.world[point] if e.alive]
        log(f"{point} contains {entities}")
        resolve_highest_priority_collision(log, point)
    return False


def resolve_collisions():
    """Resolve all collisions in the current world. Gives up after 13 iterations.

    An iteration involves a registered collision resolution taken at every coordinate containing at-least two entities.
    To prevent infinite loops and to assist debugging, this function logs with errors after 10 iterations before
    giving up entirely at 13 iterations.
    """
    collisions_settled = False
    log = IndentedLogging(logging.info)
    log("Settling collisions")
    for _ in range(10):
        collisions_settled |= resolve_highest_priority_collisions(log)
        if collisions_settled:
            log("Collisions settled.")
            return
        log("Collisions not settled, checking again..")

    logging.error("Collisions didn't finish settling! Trying 3 more times...")
    log = IndentedLogging(logging.error)
    for i in range(3):
        log(f"Iteration {i}")
        resolve_highest_priority_collisions(log=log)
