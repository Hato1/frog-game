"""Various helper functions"""
from __future__ import annotations
import pygame


def add_tuple(x: tuple, y: tuple) -> tuple:
    return tuple(x + y for x, y in zip(x, y))


class Vector(tuple):
    def __add__(self, thing2: tuple) -> Vector:
        return Vector((self[0]+thing2[0], self[1]+thing2[1]))

    def __type__(self) -> type[tuple]:
        return tuple


UP, LEFT, DOWN, RIGHT = Vector((-1, 0)), Vector((0, -1)), Vector((1, 0)), Vector((0, 1))


assets = {
    "Player": pygame.image.load("assets/Frog.png"),
    "Barrel": pygame.image.load("assets/Barrel.png"),
    "Frog": pygame.image.load("assets/BadFrog.png"),
    "Tileset": pygame.image.load("assets/Tileset.png"),
    "Grass": pygame.image.load("assets/Grass.png"),
    "Stone": pygame.image.load("assets/Stone.png"),
    "rockwall": pygame.image.load("assets/rockwall.png"),
}
