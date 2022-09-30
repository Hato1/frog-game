from __future__ import annotations

from copy import copy
from typing import TYPE_CHECKING

import pygame as pg

from gui.asset_loader import get_creature_sprite, get_default_sprite, get_random_sprite
from gui.helper import coords_to_pixels, get_disp
from gui.hud import add_hud

if TYPE_CHECKING:
    from game.helper import Point
    from gui.hud import Hud


def draw_game(
    basemap: pg.Surface,
    screen: pg.surface,
    hud: Hud,
    entities: list,
    frame: int,
    draw_player: bool,
):
    """Draws entities on basemap"""

    # TODO: Improve sprite animation stage transitions.
    animation_stage = [0, 2, 3][frame % 3]

    display_box = None
    scene = copy(basemap)
    for entity in entities:
        if entity.animates():
            sprite = get_creature_sprite(entity, animation_stage)
        elif entity.randomises():
            sprite = get_random_sprite(entity)
        else:
            sprite = get_default_sprite(entity)
        if entity.name == "Player":
            display_box = get_disp(*entity.position)
            if not draw_player:
                continue
        scene.blit(sprite, coords_to_pixels(entity.position))
    assert display_box
    screen.blit(scene, (0, 0), display_box)
    add_hud(screen, hud)
    pg.display.flip()


def get_interpolated_position(entity, travel_progress: float) -> Point:
    """Get the position of the entity between tiles

    The source point is the last entity position,
    The destination point is the current entity position

    Returns:
        The point at travel_progress% of the way between the source and destination points.
    """
    last_position = entity.position_history[-1]
    difference = entity.position - last_position
    return last_position + difference * travel_progress


def animate_step(
    basemap: pg.Surface,
    screen: pg.Surface,
    hud: Hud,
    entities: list,
    frame: int,
    animation_length: int,
):
    # TODO: Improve sprite animation stage transitions.
    animation_stage = [0, 2, 3][frame % 3]
    # TODO: Remove magic strings
    # TODO: Stay DRY by creating a common helper function with draw_game

    speed = 10

    for frame in range(animation_length):
        display_box = None
        scene = copy(basemap)
        for entity in entities:
            if entity.animates():
                sprite = get_creature_sprite(entity, animation_stage)
            elif entity.randomises():
                sprite = get_random_sprite(entity)
            else:
                sprite = get_default_sprite(entity)
            interpolated_position = get_interpolated_position(entity, frame / animation_length)
            scene.blit(sprite, coords_to_pixels(interpolated_position))
            if entity.name == "Player":
                display_box = get_disp(*interpolated_position)
        assert display_box
        screen.blit(scene, (0, 0), display_box)
        add_hud(screen, hud)
        pg.display.flip()
        pg.time.wait(speed)
