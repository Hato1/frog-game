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
#import logging
#from collections import namedtuple
#from .entity import AI_DICT
from .helper import Point
#from .map import Map

def no_conflict(map: "Map"): return


def NormalNorman_NormalNorman(map: "Map") -> None:
	# LEAPFROG #Prefreence to up, followed by right
	return


def Player_NormalNorman(map: "Map") -> None:
	map.player.alive = False
	return
