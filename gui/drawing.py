import random
from copy import copy

import pygame as pg

from gui.asset_loader import get_assets, get_spritesheet_dims
from gui.helper import coords_to_pixels, get_disp, get_sprite_box
from gui.hud import Hud, add_hud


def get_creature_sprite(entity, animation_stage: int) -> pg.Surface:
    """Get a creature sprite ot the specified animation frame.

    Also rotates the creature to the directions it is facing."""
    assets = get_assets()
    sprite = assets[entity.name]
    sprite_index = (0, animation_stage)
    creature_sprite = pg.Surface((25, 25))
    creature_sprite.fill((255, 255, 255))
    creature_sprite.set_colorkey("white")
    creature_sprite.blit(sprite, (0, 0), get_sprite_box(*sprite_index))
    creature_sprite = pg.transform.rotate(creature_sprite, 90 * entity.direction)
    return creature_sprite


def get_random_sprite(entity):
    """Get a random sprite from a spritesheet.

    Currently used to randomise rock patterns
    """
    assets = get_assets()
    spritesheet_dims = get_spritesheet_dims()
    sprite = assets[entity.name]
    # TODO: Delete this hacky fix to prevent rock textures randomising.
    # TODO: Stone should be a part of basemap to improve fps.
    random.seed(f"{entity.position}")
    plain_tile_index = 0
    sprite_num = random.randrange(spritesheet_dims["Stone"][plain_tile_index])
    sprite_index = plain_tile_index, sprite_num
    random.seed()

    random_sprite = pg.Surface((25, 25))
    random_sprite.fill((255, 255, 255))
    random_sprite.set_colorkey("white")
    random_sprite.blit(sprite, (0, 0), get_sprite_box(*sprite_index))

    return random_sprite


def get_default_sprite(entity):
    """Get first sprite

    Currently used to get rockwall sprite
    """
    assets = get_assets()
    sprite = assets[entity.name]
    # TODO: Delete this hacky fix to prevent rock textures randomising.
    # TODO: Stone should be a part of basemap to improve fps.
    plain_tile_index = 0
    sprite_num = 0
    sprite_index = plain_tile_index, sprite_num

    random_sprite = pg.Surface((25, 25))
    random_sprite.fill((255, 255, 255))
    random_sprite.set_colorkey("white")
    random_sprite.blit(sprite, (0, 0), get_sprite_box(*sprite_index))

    return random_sprite


def get_interpolated_position(entity, travel_progress: float):
    """Gets the position between the entity"""
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
