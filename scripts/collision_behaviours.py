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

# from collections import namedtuple
# from .entity import AI_DICT
# from .helper import Point
from typing import TYPE_CHECKING

# from .entity import Creature, Entity

# Dumb hacky hack for PyCharm type checking
if TYPE_CHECKING:
    from .map import Map


creatures_which_do_not_interact = "DeadDoug"
creatures_which_kill_player_outright = ("NormalNorman", "SpiralingStacy", "TrickyTrent")
creatures_which_kill_each_other = ("NormalNorman", "SpiralingStacy", "TrickyTrent")


def get_fn(entity_names: list):
    """picks the fn based on creatures' strategy names"""
    # want to make a check for Entity (not Creature), return no_conflict
    # if any([type()])
    if any([name in creatures_which_do_not_interact for name in entity_names]):
        return no_conflict
    if any([name == "Player" for name in entity_names]):
        if any([name in creatures_which_kill_player_outright for name in entity_names]):
            return kill_player

    warning(
        "{} and {} have no programmed interaction!".format(
            entity_names[0], entity_names[1]
        )
    )
    return no_conflict


def no_conflict(map: "Map"):
    return


def NormalNorman_NormalNorman(map: "Map") -> None:
    # LEAPFROG #Prefreence to up, followed by right
    return


def kill_player(map: "Map") -> None:
    map.player.alive = False
    return
