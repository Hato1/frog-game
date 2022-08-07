"""Module for game logic"""
from .map import Map
from pathlib import Path
from .helper import Vector


class Game():
    def __init__(self) -> None:
        """Initialises the game with the first map"""
        self.map = Map(Path("maps/map5"))
        # ToDo: Check if player is dead and update self.player.
        self.player = True
        # ToDo: Load a player save file for any persistent items/preferences

    def move(self, direction: Vector) -> bool:
        """Read a move and if valid, perform it and update the game.

        Args:
            direction: A tuple showing the direction of movement

        Returns True if the move was valid, False otherwise.
        """
        pos, player = self.map.find_object('Player')
        new_pos = pos + direction

        # Check valid movement
        if 0 > new_pos[0] or 0 > new_pos[1]:
            return False
        if self.map.get_width()-1 < new_pos[1] or self.map.get_height()-1 < new_pos[0]:
            return False
        for obj in self.map[new_pos]:
            if obj.solid:
                return False

        # Set the player's next move
        player.next_move = direction

        # Update all creatures (including player!)
        self.map.update_creatures()

        #if self.map.is_player_dead():
        #    self.player = False
        self.player = self.map.player_alive
        return True

    def _update_game(self) -> None:
        # Update player pos
        pass

    def get_position(self) -> tuple:
        # returns postition
        pass

    def get_map(self) -> Map:
        # return full map
        return self.map
