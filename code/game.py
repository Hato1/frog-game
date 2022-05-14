"""Module for game logic"""
from map import Map
from pathlib import Path

UP, LEFT, DOWN, RIGHT = (-1, 0), (0, -1), (1, 0), (0, 1)


class Game():
    def __init__(self) -> None:
        # Create map
        # Set player pos
        self.map = Map(Path("maps/map1"))

    def move(self, direction: tuple) -> None:
        # reject/ignore invalid input (eg: moving into a wall)
        # Call update game
        pos, player = self.map.find_object('player')
        new_pos = pos + direction

        # Check valid movement
        for obj in self.map[new_pos]:
            if obj.solid:
                return None

        # Set the player's next move
        player.next_move = new_pos

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
