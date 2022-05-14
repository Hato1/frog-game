# gui.py  - displays things
#         - recieves the input
# This will send the input to the game.py
#       Recieve back the new_map
# display the new map
import sys
import pygame
import random
from game import Game
pygame.init()


def process_event(event: pygame.event.Event, game: Game) -> None:
    """Accepts user input

    W: move up
    A: move left
    S: move down
    D: move right
    Q: quits the game
    """
    UP, LEFT, DOWN, RIGHT = (-1, 0), (0, -1), (1, 0), (0, 1)
    if event.type == pygame.QUIT:
        sys.exit()
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_q:
            sys.exit()
        if event.key == pygame.K_w:
            game.move(UP)
        elif event.key == pygame.K_a:
            game.move(LEFT)
        elif event.key == pygame.K_s:
            game.move(DOWN)
        elif event.key == pygame.K_d:
            game.move(RIGHT)


def sprite_frame(row: int, col: int = 0) -> tuple[int, int, int, int]:
    """takes a tuple, nrow,ncol"""
    return (col * 25, row * 25, 25, 25)


def inds_to_world(row: int, col: int) -> tuple:
    offset = ((8 + col) * 25,
              4 * 25 + row * 25)
    return offset


def get_disp(frogloc: tuple[int, int]) -> tuple[int, int, int, int]:
    frogx = (frogloc[1] + 8) * 25 - 188
    froggy = (frogloc[0] + 4 - 4) * 25
    return (frogx, froggy, frogx + 16 * 25, froggy + 9 * 25)


def guiloop() -> None:
    # define a few variables
    # Make this init gui
    # size of window
    size = width, height = 16 * 25, 9 * 25

    # Initialise the game
    game = Game()

    # Load the map
    c_map = game.get_map()

    # load assets into dict # SEPERATE FUN
    image_assets = {
        "Player": pygame.image.load("assets/Frog.png"),
        "Barrel": pygame.image.load("assets/Barrel.png"),
        "Frog": pygame.image.load("assets/BadFrog.png"),
        "Tileset": pygame.image.load("assets/Tileset.png")
    }

    # nrow is number of elements in a row
    obj_nrow = len(c_map)
    # ncol is number of elements in a col
    obj_ncol = len(c_map[0])

    # This is the nmber of columns/nmber of elements in each row
    wld_nrow = obj_nrow + 16
    # This is the number of rows
    wld_ncol = obj_ncol + 8

    # Initialises the entire world (width, height)
    world = pygame.Surface((wld_nrow * 25, wld_ncol * 25))

    # Pretty sure row is col and col is row
    for row in range(wld_nrow):
        for col in range(wld_ncol):

            rand_tile = random.randint(0, 3)
            world.blit(image_assets["Tileset"],
                       (row * 25, col * 25),
                       sprite_frame(rand_tile, 1))
            rand_tile = random.randint(0, 15)
            world.blit(image_assets["Tileset"],
                       (row * 25, col * 25),
                       sprite_frame(rand_tile, 11))

    # Make drawworld a fn
    # make world_with_objects = world a thing
    # make add objects a fn

    # populate it with onjects
    for row in range(obj_nrow):
        for col in range(obj_ncol):
            for k in c_map[row][col]:
                imgk = image_assets[k.name]
                world.blit(imgk, inds_to_world(row, col), sprite_frame(3))

    froglocation, null = c_map.find_object("Player")
    screen = pygame.display.set_mode(size, pygame.SCALED | pygame.RESIZABLE)
    screen.blit(world, (0, 0), get_disp(froglocation))
    pygame.display.flip()

    # start the loop
    while True:
        for event in pygame.event.get():
            process_event(event, game)
    #     # other conditions here

    #     # update map thing here
    #     # include searches of current and old map to interpolate
    #     # tempmap:
    #     c_map = [[["f"]] * 25] * 25

    #     # Draw the things
    #     screen.fill(black)
    #     screen.blit(pl_frog_all, pl_frogrect)
    #     pygame.display.flip()


guiloop()
