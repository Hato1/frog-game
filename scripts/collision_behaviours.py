"""
TODO: URGENT - make temp_fn(pair, pairs, entities_on_space): return moved_entities
TODO: URGENT - make get_highest_priorityfn(pairs): return temp_fn, pair
Behaviours for collisions between each pair of entities

Function names are "strategy1_strategy2"
as per Entity.get_strategy_name()

Each function takes map: Map, self in map.py and -> None

Function names are WET :[

list of potential entities (see ai.dict):
"Player": Player
"NormalNorman": NormalNorman
"DeadDoug": DeadDoug
"SpiralingStacy": SpiralingStacy
"BarrelingBarrel": BarrelingBarrel
"TrickyTrent": TrickyTrent

Important variables to modify in place:
new_map - Map
    new map to make changes to

collisions_here - List of collisions on current tile
    need to remove collisions involving an entity which die or are removed

collision_positions - List of Points where collisions occur
    need to append with points entities are moved to

Notes:
    Force moved entities should go to front of list, if move unmade, or back if move extra
"""
from logging import warning

# from collections import namedtuple
# from .entity import AI_DICT
# from .helper import Point
from typing import Union

# from .entity import Creature, Entity

# Dumb hacky hack for PyCharm type checking. Needs TYPE_CHECKING from typing
# if TYPE_CHECKING:
#     from .map import Map


creatures_which_do_not_interact = "DeadDoug"
creatures_which_kill_player_outright = ("NormalNorman", "SpiralingStacy", "TrickyTrent")
creatures_which_kill_each_other = ("NormalNorman", "SpiralingStacy", "TrickyTrent")
# get_highest_priorityfn(pairs): return temp_fn, pair


def get_highest_priorityfn(pairs: list):
    """
    returns the pair with highest priority, and the fn to handle their collision
    TODO: think about the case of equal priority interactions
    """
    # want to make a check for Entity (not Creature), return no_conflict
    # if any([type()])
    # pair_names = [(e.get_strategy_name() for e in pair) for pair in pairs]

    if pair := check_get_pair(pairs, "Player", creatures_which_kill_player_outright):
        # Perhaps make a new fn which also removes non-interacting creatures from collisions_here
        return kill_player, pair
    # if check_pairs(pair_names, "Player"):
    #     if check_names(entity_names, creatures_which_kill_player_outright):
    #         return kill_player
    #     if check_names(entity_names, "BarrelingBarrel"):
    #         return Player_BarrelingBarrel
    # if check_names("Barrel"):
    #     makehappy(barrel)
    pair = pairs[0]
    warning(
        "{} and {} have no programmed interaction!".format(
            pair[0].get_strategy_name(), pair[1].get_strategy_name()
        )
    )
    return no_conflict, pair


# Generic functions:
def check_get_pair(
    pairs: list, special_names0: Union[tuple, str], special_names1: Union[tuple, str]
) -> list:
    """
    Checks entity names in pair against reference lists
    also checks reverse order
    If multiple pairs are found, return the first instance
    """
    pair = [
        pair
        for pair in pairs
        if (pair[0].get_strategy_name() in special_names0)
        and (pair[1].get_strategy_name() in special_names1)
        or (pair[1].get_strategy_name() in special_names0)
        and (pair[0].get_strategy_name() in special_names1)
    ]
    if pair:
        pair = pair[0]
    return pair


# def get_ind(name: str) -> int:
#     """given an entity name, finds its index in entity_strategies (= current_collision)"""
#     entities_are_name = entity_strategies == name
#     return [i for i, x in enumerate(entities_are_name) if x]


def remove_from_collisions(target_entity):
    # indices_with_entity = [i for i, entity in enumerate(collisions_here)
    # if entity == target_entity]
    return


def no_conflict(pair: tuple, pairs: list, entities_on_space: list) -> list:
    return []


def kill_player(pair: tuple, pairs: list, entities_on_space: list) -> list:
    warning("DIE PLAYER!!")
    return []


def NormalNorman_NormalNorman(
    pair: tuple, pairs: list, entities_on_space: list
) -> list:
    # LEAPFROG #Prefreence to up, followed by right
    return []


# def Player_BarrelingBarrel(pair: tuple, pairs: list, entities_on_space: list) -> list:
#     # up/down/left/right in state (0/1/2/3/4+)
#     barrel = current_collision[get_ind("BarrelingBarrel")]
#     return []
