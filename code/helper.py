"""Various helper functions"""
import pygame


def add_tuple(x: tuple, y: tuple) -> tuple:
    return tuple(x + y for x, y in zip(x, y))


assets = {
    "Player": pygame.image.load("assets/Frog.png"),
    "Barrel": pygame.image.load("assets/Barrel.png"),
    "Frog": pygame.image.load("assets/BadFrog.png"),
    "Tileset": pygame.image.load("assets/Tileset.png"),
    "Grass": pygame.image.load("assets/Grass.png"),
    "Stone": pygame.image.load("assets/Stone.png"),
    "rockwall": pygame.image.load("assets/rockwall.png"),
}
