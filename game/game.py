"""Module for maintaining game state and managing game interface.

Managing interface includes determining valid game inputs and querying the game state."""
from game import collision_registry
from game.collision_resolver import resolve_collisions
from game.entity import Entity, Tags
from game.helper import Point
from game.map import current_map, maps, reset_maps


class Game:
    def __init__(self) -> None:
        """Initialises the game"""
        self.reset_game()
        # ToDo: Load a player save file for any persistent items/preferences

    @property
    def map(self):
        return maps[current_map]

    @property
    def entities(self):
        return self.map.entities

    def kill_player(self) -> None:
        self.map.player.alive = False

    def player_alive(self) -> bool:
        return self.map.player.alive

    def get_player_pos(self) -> Point:
        return self.map.player.position

    def get_map_dims(self, world=None):
        if world:
            raise NotImplementedError
        return self.map.get_width(), self.map.get_height()

    def get_steps_left(self):
        """returns number of steps remaining"""
        return self.map.steps_left

    def get_max_steps(self):
        """returns number of steps remaining"""
        return self.map.max_steps

    @staticmethod
    def reset_game():
        reset_maps()

    def move(self, direction: Point) -> bool:
        """Read a move and if valid, perform it and update the game.

        Args:
            direction: A vector showing the displacement

        Returns True if the move was valid, False otherwise.
        """
        if not self.map.player.alive:
            return False

        pos = self.get_player_pos()
        new_pos = pos + direction

        # Check move is valid
        if self._is_move_invalid(new_pos, direction):
            return False

        # Set the player's next move
        self.map.player.next_move = direction

        # Update all creatures (including player!)
        self.map.update_creatures()
        resolve_collisions()
        self.map.cull_entities()
        return True

    def _is_move_invalid(self, new_pos: Point, direction: Point) -> bool:
        """Check various conditions"""
        # Move is out of bounds:
        # TODO: Surround map with rocks instead of padding, removing need to do this.
        if new_pos[0] < 0 or new_pos[1] < 0:
            return True
        if self.map.get_width() - 1 < new_pos[0] or self.map.get_height() - 1 < new_pos[1]:
            return True

        # Check for solid object blocking path by re-using the logic for if player can be 'pushed' in this direction.
        # TODO: What about when pushing an object into a spot where another object is due to appear?
        in_line: list[Entity] = []
        if blocked := collision_registry.PushCollision.get_pushable_line(self.map.player, direction, in_line):
            if blocked.position != new_pos or Tags.solid in blocked.tags:
                return True
        return False
