"""Module for game logic"""
from .map import Map
from pathlib import Path


class Game():
    def __init__(self) -> None:
        """Initialises the game with the first map"""
        self.map = Map(Path("maps/map3"))
        # ToDo: Check if player is dead and update self.player.
        self.player = True
        # ToDo: Load a player save file for any persistent items/preferences

    def move(self, direction: tuple) -> bool:
        """Read a move and if valid, perform it and update the game.

        Args:
            direction: A tuple showing the direction of movement

        Returns True if the move was valid, False otherwise.
        """
        pos, player = self.map.find_object('Player')
        new_pos = direction + pos

        # Check valid movement
        if 0 > new_pos[0] or 0 > new_pos[1]:
            return False
        if self.map.get_width()-1 < new_pos[1] or self.map.get_height()-1 < new_pos[0]:
            return False
        for obj in self.map[new_pos]:
            if obj.solid:
                return False

        # Set the player's next move
        player.next_move = new_pos

        # Update all creatures (including player!)
        player_killed = self.map.update_creatures()
        if player_killed:
            self.player = False

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