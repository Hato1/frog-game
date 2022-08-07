"""Behaviours for collisions between each pair of entities"""
from typing import TYPE_CHECKING
import logging

def collision_resolver(current_collision: tuple, remaining_pairs: list, collision_pos: tuple, new_map: "Map", collision_locs: list) -> None:
	logging.debug(msg="Ouch!")
	entity_pair = [new_map[collision_pos][a] for a in current_collision]
	for entity in entity_pair:
		if str(entity) == "Player":
			entity.alive = False
	return
