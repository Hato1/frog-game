"""Module for game logic"""
from map import Map
from pathlib import Path


class Game():
    def __init__(self) -> None:
        """Initialises the game with the first map"""
        self.map = Map(Path("maps/map1"))

    def move(self, direction: tuple) -> bool:
        """Read a move and if valid, perform it and update the game.

        Args:
            direction: A tuple showing the direction of movement

        Returns True if the move was valid, False otherwise.
        """
        pos, player = self.map.find_object('player')
        new_pos = pos + direction

        # Check valid movement
        for obj in self.map[new_pos]:
            if obj.solid:
                return False

        # Set the player's next move
        player.next_move = new_pos
        return True

        # Update all creatures (including player!)
        self.map.update_creatures()

    def _update_game(self) -> None:
        # Update player pos
        self.map.update_creatures()

    def get_position(self) -> tuple:
        # returns postition
        pass

    def get_map(self) -> Map:
        # return full map
        return self.map
