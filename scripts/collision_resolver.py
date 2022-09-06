# mypy: ignore-errors
"""Behaviours for collisions between each pair of entities"""
import logging
from typing import TYPE_CHECKING

# Dumb hacky hack for PyCharm type checking
if TYPE_CHECKING:
    from .map import Map


# from .entity import AI_DICT

# Current AIs: AI_DICT = {
#    "NormalNorman": NormalNorman,
#    "DeadDoug": DeadDoug,
#    "SpiralingStacy": SpiralingStacy,
#    "BarrelingBarrel": BarrelingBarrel,
#    "TrickyTrent": TrickyTrent,
#     PLAYER UGH
# }


def collision_resolver(
    current_collision: tuple,
    remaining_pairs: list,
    collision_pos: tuple,
    new_map: "Map",
    collision_locs: list,
) -> None:
    """This fn gets the entities, abd calls the appropriate fn based on their strategy"""
    # CAUTION, I THINK THIS MIGHT DUPLIACATE ENTITIES NOT GET POINTERS JACOB???!?
    entity_pair = [new_map[collision_pos][a] for a in current_collision]
    logging.debug(entity_pair)
    entity_pair.sort(key=lambda ent: ent.get_strategy_name())
    entity_strategies = [ent.get_strategy_name() for ent in entity_pair]
    # noinspection PyBroadException
    try:
        temp_fn = locals()["_".join(entity_strategies)]
    except Exception:
        # Except what? -Jacob
        temp_fn = no_conflict
    temp_fn(current_collision, remaining_pairs, collision_pos, new_map, collision_locs)

    return


def no_conflict(
    current_collision: tuple,
    remaining_pairs: list,
    collision_pos: tuple,
    new_map: "Map",
    collision_locs: list,
) -> None:
    return


def NormalNorman_NormalNorman(
    current_collision: tuple,
    remaining_pairs: list,
    collision_pos: tuple,
    new_map: "Map",
    collision_locs: list,
) -> None:
    # LEAPFROG #Prefreence to up, followed by right
    return
