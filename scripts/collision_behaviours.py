"""
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
from typing import Union

from .entity import Entity

# from collections import namedtuple
# from .entity import AI_DICT
from .helper import DOWN, IDLE, LEFT, RIGHT, UP, Point

# Dumb hacky hack for PyCharm type checking. Needs TYPE_CHECKING from typing
# if TYPE_CHECKING:
#     from .map import Map


creatures_which_do_not_interact = "DeadDoug"
creatures_which_kill_player_outright = ("NormalNorman", "SpiralingStacy", "TrickyTrent")
creatures_which_kill_each_other = ("NormalNorman", "SpiralingStacy", "TrickyTrent")
creatures_which_push_rocks = (
    "NormalNorman",
    "SpiralingStacy",
    "TrickyTrent",
    "Player",
    "BarrelingBarrel",
)


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
    if pair := check_get_pair(pairs, "Player", "BarrelingBarrel"):
        return Player_BarrelingBarrel, pair
    if pair := check_get_pair(pairs, "SlidingStone_Any", creatures_which_push_rocks):
        return SlidingStone_Any, pair

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


def push(pusher: Entity, pushee: Entity) -> Point:
    """pusher pushes pushee, returns direction of push"""
    push_direction = pusher.position - pusher.position_history[-1]
    pushee.force_move([push_direction])
    return push_direction


# Fn shunted to entity.force_move()
# def move_entity(entity: Entity, direction: Point) -> None:
# 	"""Moves entity in direction"""
# 	entity.position += direction


def get_ind(pair: tuple, name: str) -> bool:
    """given a pair and entity name, finds its index in pair"""
    return pair[1].get_strategy_name() == name


def remove_from_collisions(target_entity):
    # indices_with_entity = [i for i, entity in enumerate(collisions_here)
    # if entity == target_entity]
    return


# From here down are the functions which resolve specific interactions
# These take the form of:
# temp_fn(pair: tuple, pairs: list of tuples, entities_on_space: list) -> list


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


def Player_BarrelingBarrel(pair: tuple, pairs: list, entities_on_space: list) -> list:
    # up/down/left/right in state (0/1/2/3/4)
    # TODO: remove barrel from pairs
    barrel_ind = get_ind(pair, "BarrelingBarrel")
    push_dir = push(pair[not barrel_ind], pair[barrel_ind])

    # WET line incoming:
    next_state = [
        i for i, d in enumerate([IDLE, UP, DOWN, LEFT, RIGHT]) if d == push_dir
    ]
    # ^^ duplicate of facing from helper.py
    pair[barrel_ind].force_state(next_state[0])
    pair[barrel_ind].force_facing(push_dir)
    return [pair[barrel_ind]]


def SlidingStone_Any(pair: tuple, pairs: list, entities_on_space: list) -> list:
    """Sliding Stone gets pushed around"""
    SS_ind = get_ind(pair, "SlidingStone")
    push(pair[not SS_ind], pair[SS_ind])
    return [pair[SS_ind]]
