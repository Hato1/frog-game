"""
Behaviours for collisions between each pair of entities

Function names are "strategy1_strategy2"
as per Entity.get_strategy_name()

Each function takes bits: dict -> None



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
    TODO: rename things to make more sense

Question: would it make more sense to refactor this all into entity.get_move()?
"""
import logging
from typing import TYPE_CHECKING, Callable, Iterable, Literal

from game.entity import Entity, Tags

if TYPE_CHECKING:
    from game.map import Map
# from collections import namedtuple
# from .entity import AI_DICT
from game.helper import DOWN, IDLE, LEFT, RIGHT, UP, Point

EntityPair = tuple[Entity, Entity]


def get_highest_priority_fn(pairs: list[EntityPair]) -> tuple[Callable, EntityPair]:
    """Returns the function that resolves the highest priority interaction, and the pair involved.
    TODO: Think about the case of equal priority interactions
    TODO: Think about whether using "case:" would make sense
    """

    # Kill player
    if pair := check_get_pair(pairs, (Tags.player, Tags.kills_player)):
        # Perhaps make a new fn which also removes non-interacting creatures from collisions_here
        return kill_player, pair

    # Push entities
    # TODO: Predefine order of check_get_pair so we don't have to mess with pair indexes
    if pair := check_get_pair(pairs, (Tags.pushable, Tags.pusher)):
        # TODO: ensure two "SlidingStone"s cannot collide
        # Make this a generic fn unless barrel
        if check_for_tag(pair, Tags.barrel):
            barrel_state = get_state(pair, Tags.barrel)
            if barrel_state:
                # Behaviour for rolling barrel to kill frogs goes here
                return pusher_boringbarrel, pair
            else:
                return pusher_boringbarrel, pair
        else:
            return simple_push, pair
    if pair := check_get_pair(pairs, (Tags.barrel, Tags.solid)):
        return blocked_barrel, pair

    # if pair := check_get_pair(pairs, "SlidingStone", "BarrelingBarrel"):
    #     return SlidingStone_BarrelingBarrel, pair
    # if check_pairs(pair_names, "Player"):
    #     if check_names(entity_names, creatures_which_kill_player_outright):
    #         return kill_player
    #     if check_names(entity_names, "BarrelingBarrel"):
    #         return Player_BarrelingBarrel
    # Generic behaviours:
    # Solid entities block:
    if pair := check_get_pair(pairs, Tags.solid):
        return simple_block, pair
    # No collision found
    return no_conflict_warning, pairs[0]


# Generic functions:
def check_get_pair(
    pairs: list[EntityPair],
    tags: tuple[Tags, Tags] | Tags,
) -> EntityPair | Literal[False]:
    """
    Checks tags against tags in pairs
    also checks reverse order
    If multiple pairs are found, return the first instance
    ^^ This might do some funky stuff when different states of some entities are involved
    (Consider the case of two barreling barrels colliding into a boing barrel)
    Also has functionality to find single tags (like solid)
    """
    match tags:
        case tuple():
            if pair := [
                pair
                for pair in pairs
                if tags[0] in pair[0].tags
                and tags[1] in pair[1].tags
                or tags[1] in pair[0].tags
                and tags[0] in pair[1].tags
            ]:
                return pair[0]
        case Tags():  # Single tag
            if pair := [pair for pair in pairs if tags in pair[0].tags or tags in pair[1].tags]:
                return pair[0]
    return False


def check_for_tag(entities: Iterable, tag: Tags) -> bool:
    """checks if any entity in entities has given tag"""
    tag_set = set(tag for entity in entities for tag in entity.tags)
    return tag in tag_set


def get_state(pair: tuple, tag: Tags) -> int:
    """gives the state of the named entity"""
    return pair[get_ind(pair, tag)].get_state()


def push(pusher: Entity, pushee: Entity, entity_list: list) -> Point | bool:
    """pusher pushes pushee, returns direction of push"""
    push_direction = pusher.position - pusher.position_history[-1]
    if push_direction == Point(0, 0):
        return False
    if pushee.force_move([push_direction], entity_list):
        return push_direction
    else:
        return False


def block(_blocker: Entity, blockee: Entity, entity_list: list) -> Point:
    """blocks blockee"""
    push_direction = blockee.position_history[-1] - blockee.position
    blockee.force_move([push_direction], entity_list)
    return push_direction


def get_ind(pair: tuple, tag: Tags) -> bool:
    """given a pair and tag, finds its index with tag, preference to 1"""
    # pair is length 2: ind is equivalently is_index_one: bool
    return tag in pair[1].tags


def remove_from_collisions(pairs: list[EntityPair], target_entity: Entity) -> None:
    for pair in pairs:
        if target_entity in pair:
            pairs.remove(pair)


def check_push(the_map: "Map", current_point: Point, push_direction: Point) -> list:
    """
    recursively checks all spaces in front of a push
    either returns a list of entities to force move (empty if invalid push)
    we check "Can current pushable move?", denoted by list or false
    """
    pushable_entities_here = [
        entity for entity in the_map[current_point] if Tags.pushable in entity.tags
    ]
    if check_for_tag(the_map[current_point + push_direction], Tags.solid):
        return []
    # This might be able to be made more efficient
    elif not check_for_tag(the_map[current_point + push_direction], Tags.pushable):
        return pushable_entities_here
    else:
        if entities_ahead := check_push(the_map, current_point + push_direction, push_direction):
            entities_ahead += pushable_entities_here
        return entities_ahead


# ======================================================================================================================
# From here down are the functions which resolve specific interactions
# These take the form of:
# temp_fn(bits{pair: tuple, pairs: list of tuples, entities_on_space: list, entity_list: list})
# -> list of entities whose positions need to be re-checked
# ======================================================================================================================


def no_conflict(bits: dict) -> list:
    return []


def no_conflict_warning(bits: dict) -> list:
    logging.warning(
        f"{bits['pair'][0].get_strategy_name()} and {bits['pair'][1].get_strategy_name()} have no programmed interaction!"
    )
    return []


def kill_player(bits: dict) -> list:
    pair = bits["pair"]
    p = pair[get_ind(pair, Tags.player)]
    p.alive = False
    return []


def simple_push(bits: dict) -> list:
    """tag pushee gets pushed"""
    # More like "simple" push ammirite?? haha.. =(

    # TODO: add forcemoved spaces to collision list
    pair, pairs, entity_list, the_map = (
        bits["pair"],
        bits["pairs"],
        bits["entity_list"],
        bits["the_map"],
    )
    # Get push direction, and which is pushing
    pusher_ind = get_ind(pair, Tags.pusher)
    push_direction = pair[pusher_ind].position - pair[pusher_ind].position_history[-1]
    current_point = pair[0].position

    if entities_to_push := check_push(the_map, current_point, push_direction):
        # Valid move, move all pushees, remove from current push
        assert all(
            entity.force_move([push_direction], entity_list) for entity in entities_to_push
        ), "I have no idea how you got here"
        remove_from_collisions(pairs, pair[not pusher_ind])
    else:
        block(pair[not pusher_ind], pair[pusher_ind], entity_list)
        entities_to_push = [pair[pusher_ind]]
    return entities_to_push


def simple_block(bits: dict) -> list:
    """tag solid pushes back other entity"""
    pair, pairs, entity_list = bits["pair"], bits["pairs"], bits["entity_list"]
    solid_ind = get_ind(pair, Tags.solid)
    move = block(pair[solid_ind], pair[not solid_ind], entity_list)
    # TODO: ensure move actually occurs (not pushed into a solid entity or off map)
    # if move:
    remove_from_collisions(pairs, pair[not solid_ind])
    return [pair[not solid_ind]] if move else []


def blocked_barrel(bits: dict) -> list:
    """tag solid pushes back other entity"""
    pair = bits["pair"]
    pair[get_ind(pair, Tags.barrel)].force_state(0)
    return simple_block(bits)


# def normalnorman_normalnorman(bits: dict) -> list:
#     # LEAPFROG #Prefreence to up, followed by right
#     return []


def pusher_boringbarrel(bits: dict) -> list:
    """move the barrel, then change its state"""
    # still/up/down/left/right in state (0/1/2/3/4)

    pair, pairs, entity_list = bits["pair"], bits["pairs"], bits["entity_list"]
    barrel_ind = get_ind(pair, Tags.barrel)
    push_dir = push(pair[not barrel_ind], pair[barrel_ind], entity_list)
    if not push_dir:
        return []

    # WET line incoming, duplicate of facing from helper.py
    next_state = [i for i, d in enumerate([IDLE, UP, DOWN, LEFT, RIGHT]) if d == push_dir]
    if not next_state:
        remove_from_collisions(pairs, pair[barrel_ind])
        return []
    pair[barrel_ind].force_state(next_state[0])
    pair[barrel_ind].force_facing(push_dir)
    return [pair[barrel_ind]]


def slidingstone_barrelingbarrel(bits: dict) -> list:
    """Sliding Stone stops Barreling Barrel"""
    pair, entity_list = bits["pair"], bits["entity_list"]
    barrel_ind = get_ind(pair, Tags.barrel)
    block(pair[not barrel_ind], pair[barrel_ind], entity_list)
    pair[barrel_ind].force_state(0)
    return [pair[barrel_ind]]


# def SlidingStone_BoringBarrel(pair: tuple, pairs: list, entities_on_space: list) -> list:
#     """Sliding Stone pushes Barreling Barrel"""
#     barrel_ind = get_ind(pair, "BarrelingBarrel")
#     push(pair[not barrel_ind], pair[barrel_ind])
#     pair[barrel_ind].force_state(?)
#     return [pair[barrel_ind]]
