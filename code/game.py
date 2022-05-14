"""Module for game logic"""
from map import Map
from pathlib import Path


class Game():
    def __init__(self) -> None:
        # Create map
        # Set player pos
        self.map = Map(Path("maps/map1"))

    def move(self, direction: int) -> None:
        # reject/ignore invalid input (eg: moving into a wall)
        # Call update game
        pass

    def _update_game(self) -> None:
        # Update player pos
        self.map.update_creatures()

    def get_position(self) -> tuple:
        # returns postition
        pass

    def get_map(self) -> Map:
        # return full map
        return self.map
