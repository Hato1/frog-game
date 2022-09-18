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
    TODO: Force moved entities should go to front of list, if move unmade, or back if move extra
    TODO: should really make "pair" a named tuple to avoid indexing shenanigans
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
creatures_which_push = (
    "NormalNorman",
    "SpiralingStacy",
    "TrickyTrent",
    "Player",
    "SlidingStone",
)
creatures_which_get_pushed = (
    "SlidingStone",
    "BarrelingBarrel",
)
creatures_which_barrel_kills = (
    "NormalNorman",
    "SpiralingStacy",
    "TrickyTrent",
    "Player",
)


def get_highest_priorityfn(pairs: list):
    """Returns the function that resolves the highest priority interaction, and the pair involved.
    TODO: Think about the case of equal priority interactions
    TODO: Think about whether using "case:" would make sense
    TODO: Named tuples instead of magic strings.
    """
    # pair_names = [(e.get_strategy_name() for e in pair) for pair in pairs]

    # Kill player
    if pair := check_get_pair(pairs, "Player", creatures_which_kill_player_outright):
        # Perhaps make a new fn which also removes non-interacting creatures from collisions_here
        return kill_player, pair
    # if pair := check_get_pair(pairs, "Player", "BarrelingBarrel"):
    #     return Player_BarrelingBarrel, pair

    # Push objects
    # TODO: Predefine order of check_get_pair so we don't have to mess with pair indexes
    if pair := check_get_pair(pairs, creatures_which_get_pushed, creatures_which_push):
        if all(entity.get_strategy_name() == "SlidingStone" for entity in pair):
            warning("Multiple sliding stones on same space not implemented")
            return no_conflict, pair
        if "BarrelingBarrel" in [entity.get_strategy_name() for entity in pair]:
            barrel_state = pair[get_ind(pair, "BarrelingBarrel")].get_state()
            if not barrel_state:
                return pusher_boringbarrel, pair
        if "SlidingStone" in [entity.get_strategy_name() for entity in pair]:
            return slidingstone_any, pair
    # if pair := check_get_pair(pairs, "SlidingStone", "BarrelingBarrel"):
    #     return SlidingStone_BarrelingBarrel, pair
    # if check_pairs(pair_names, "Player"):
    #     if check_names(entity_names, creatures_which_kill_player_outright):
    #         return kill_player
    #     if check_names(entity_names, "BarrelingBarrel"):
    #         return Player_BarrelingBarrel

    # No collision found
    return no_conflict_warning, pairs[0]


# Generic functions:
def check_get_pair(
    pairs: list, special_names0: Union[tuple, str], special_names1: Union[tuple, str]
):  # -> Union[tuple, []]
    """
    Checks entity names in pair against reference lists
    also checks reverse order
    If multiple pairs are found, return the first instance
    ^^ This might do some funky stuff when different states of sme entities are involved
    (Consider the case of two brreling barells colliding into a boing barrel)
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


def check_state(pair: tuple, which: str) -> int:
    """gives the state of the named entity"""
    return pair[get_ind(pair, which)].get_state()


def push(pusher: Entity, pushee: Entity) -> Point:
    """pusher pushes pushee, returns direction of push"""
    push_direction = pusher.position - pusher.position_history[-1]
    pushee.force_move([push_direction])
    return push_direction


def block(_blocker: Entity, blockee: Entity) -> Point:
    """blocks blockee"""
    push_direction = blockee.position_history[-1] - blockee.position
    blockee.force_move([push_direction])
    return push_direction


# Fn shunted to entity.force_move()
# def move_entity(entity: Entity, direction: Point) -> None:
#   """Moves entity in direction"""
#   entity.position += direction


def get_ind(pair: tuple, name: str) -> bool:
    """given a pair and entity name, finds its index in pair"""
    # pair is length 2: ind is equivalently is_index_one: bool
    # This is a bit difficult to read, feel free to veto
    return pair[1].get_strategy_name() == name


def remove_from_collisions(pairs: list, target_entity: Entity):
    for pair in pairs:
        if target_entity in pair:
            pairs.remove(pair)


# From here down are the functions which resolve specific interactions
# These take the form of:
# temp_fn(pair: tuple, pairs: list of tuples, entities_on_space: list) -> list


def no_conflict(_pair: tuple, _pairs: list, _entities_on_space: list) -> list:
    return []


def no_conflict_warning(pair: tuple, _pairs: list, _entities_on_space: list) -> list:
    warning(
        f"{pair[0].get_strategy_name()} and {pair[1].get_strategy_name()} have no programmed interaction!"
    )
    return []


def kill_player(pair: tuple, _pairs: list, _entities_on_space: list) -> list:
    p = pair[get_ind(pair, "Player")]
    p.alive = False
    return []


def normalnorman_normalnorman(
    _pair: tuple, _pairs: list, _entities_on_space: list
) -> list:
    # LEAPFROG #Prefreence to up, followed by right
    return []


def pusher_boringbarrel(pair: tuple, pairs: list, _entities_on_space: list) -> list:
    # still/up/down/left/right in state (0/1/2/3/4)
    # TODO: remove barrel from pairs
    barrel_ind = get_ind(pair, "BarrelingBarrel")
    push_dir = push(pair[not barrel_ind], pair[barrel_ind])

    # WET line incoming:
    next_state = [
        i for i, d in enumerate([IDLE, UP, DOWN, LEFT, RIGHT]) if d == push_dir
    ]
    # ^^ duplicate of facing from helper.py
    if not next_state:
        remove_from_collisions(pairs, pair[barrel_ind])
    pair[barrel_ind].force_state(next_state[0])
    pair[barrel_ind].force_facing(push_dir)
    return [pair[barrel_ind]]


def slidingstone_any(pair: tuple, pairs: list, _entities_on_space: list) -> list:
    """Sliding Stone gets pushed around"""
    ss_ind = get_ind(pair, "SlidingStone")
    move = push(pair[not ss_ind], pair[ss_ind])
    if move != IDLE:
        remove_from_collisions(pairs, pair[ss_ind])
    return [pair[ss_ind]]


def slidingstone_barrelingbarrel(
    pair: tuple, _pairs: list, _entities_on_space: list
) -> list:
    """Sliding Stone stops Barreling Barrel"""
    barrel_ind = get_ind(pair, "BarrelingBarrel")
    block(pair[not barrel_ind], pair[barrel_ind])
    pair[barrel_ind].force_state(0)
    return [pair[barrel_ind]]


# def SlidingStone_BoringBarrel(pair: tuple, pairs: list, entities_on_space: list) -> list:
#     """Sliding Stone pushes Barreling Barrel"""
#     barrel_ind = get_ind(pair, "BarrelingBarrel")
#     push(pair[not barrel_ind], pair[barrel_ind])
#     pair[barrel_ind].force_state(?)
#     return [pair[barrel_ind]]
