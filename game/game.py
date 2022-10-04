"""Module for game logic"""
from pathlib import Path

from game.entity import Tags
from game.helper import Point
from game.map import Map


class Game:
    def __init__(self) -> None:
        """Initialises the game with the first map"""
        self.map = Map(Path("maps/map3"))
        # ToDo: Load a player save file for any persistent items/preferences

    def move(self, direction: Point) -> bool:
        """Read a move and if valid, perform it and update the game.

        Args:
            direction: A tuple showing the direction of movement

        Returns True if the move was valid, False otherwise.
        """
        if not self.player_alive():
            return False

        pos = self.get_player_pos()
        new_pos = pos + direction

        # Check move is valid
        if self._is_move_invalid(new_pos):
            return False

        # Set the player's next move
        self.map.player.next_move = direction

        # Update all creatures (including player!)
        self.map.update_creatures()

        return True

    def _is_move_invalid(self, new_pos: Point) -> bool:
        """Check various conditions"""
        # Move is out of bounds:
        if new_pos[0] < 0 or new_pos[1] < 0:
            return True
        if self.map.get_width() - 1 < new_pos[0] or self.map.get_height() - 1 < new_pos[1]:
            return True
        # Entity specific conditions:
        for obj in self.map[new_pos]:
            if Tags.solid in obj.tags:
                return True
        return False
        # Move pushes rock invalidly:
        #     if obj.tags:

    def _update_game(self) -> None:
        # Update player pos
        pass

    def get_position(self) -> tuple:
        # returns position
        pass

    def get_map(self) -> Map:
        # return full map
        return self.map

    def get_steps_remaining(self):
        """returns number of steps remaining"""
        return self.map.get_steps_left()

    def player_alive(self) -> bool:
        return self.map.player.alive

    def get_player_pos(self) -> Point:
        return self.map.player.position

    def kill_player(self) -> None:
        self.map.player.alive = False

    def get_map_dims(self):
        return self.map.get_width(), self.map.get_height()

    def get_entities(self):
        return self.map.get_entities()

    def get_steps_left(self):
        return self.map.get_steps_left()
