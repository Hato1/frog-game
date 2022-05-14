"""Module for game logic"""
from entity import Entity
from map import Map


class Game():
    def __init__(self) -> None:
        # Create map
        # Set player pos
        self.map = Map

    def move(self, direction: int) -> None:
        # reject/ignore invalid input (eg: moving into a wall)
        # Update player pos
        # Update all Creatures
        # Run conflict resolver
        pass

    def _conflict_resolver(self, objects: list, map: Map) -> None:
        # Update the conflicting square
        # 
        pass

    def update_game(self) -> None:
        pass

    def get_position(self) -> tuple:
        # returns postition
        pass

    def get_map(self) -> list[list]:
        # return full map
        pass
