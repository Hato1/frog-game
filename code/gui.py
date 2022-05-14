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


def sprite_frame(row: int, col: int = 0) -> tuple:
    """takes a """
    return (col * 25, row * 25, 25, 25)


def inds_to_world(row: int, col: int) -> tuple:
    offset = (7.5 * 25 + 0.5 + 25 * col,
              4 * 25 + row * 25)
    return offset


def get_disp(frogloc) -> tuple:
    frogx = (frogloc[1] + 8) * 25 - 188
    frogy = (frogloc[0] + 4 - 4) * 25
    return (frogx, frogy, frogx + 16 * 25, frogy + 9 * 25)


def guiloop():
    # define a few variables
    size = width, height = 16 * 25, 9 * 25
    # black = 50, 0, 0

    # initialise the display window
    screen = pygame.display.set_mode(size, pygame.SCALED | pygame.RESIZABLE)

    # Initialise the game
    game = Game()

    # Load the map
    c_map = game.get_map()

    # load assets into dict

    image_assets = {
        "Player": pygame.image.load("assets/Frog.png"),
        "Barrel": pygame.image.load("assets/Barrel.png"),
        "Frog": pygame.image.load("assets/BadFrog.png"),
        "Tileset": pygame.image.load("assets/Tileset.png")
    }
    # print(spriteframe(3))
    # print(c_map) ## This is a temp thing
    # c_mmap = c_map
    # c_map = c_map.map
    obj_nrow = len(c_map)
    obj_ncol = len(c_map[0])
    wld_nrow = obj_nrow + 8
    wld_ncol = obj_ncol + 16

    # print(c_map)
    # pl_frogrect = pl_frog_all.get_rect()

    # Initialises the entire world
    world = pygame.Surface((len(c_map) * 25, len(c_map[0] * 25)))
    for row in range(wld_nrow):
        for col in range(wld_ncol):
            rand_tile = random.randint(0, 3)
            world.blit(image_assets["Tileset"],
                       (col * 25, row * 25),
                       sprite_frame(rand_tile, 1))
            rand_tile = random.randint(0, 15)
            world.blit(image_assets["Tileset"],
                       (col * 25, row * 25),
                       sprite_frame(rand_tile, 11))

    # populate it with onjects
    for row in range(obj_nrow):           # i is x
        for col in range(obj_ncol):    # row is y
            for k in c_map[row][col]:
                imgk = image_assets[k.name]
                # imgkrect.move((-col * 25, -row * 25))
                # world.blit(imgk, imgkrect)
                world.blit(imgk, inds_to_world(row, col), sprite_frame(3))

    froglocation, null = c_map.find_object("Frog")
    # print((froglocation[0] * 25, froglocation[1] * 25))
    screen.blit(world, (0, 0), get_disp(froglocation))

    pygame.display.flip()

    # start the loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
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
# pygame.init()

# speed = [2, 2]
# black = 0, 0, 0

# screen = pygame.display.set_mode(size)

# ball = pygame.image.load("assets/intro_ball.gif")
# ballrect = ball.get_rect()

# while True:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             sys.exit()

#     ballrect = ballrect.move(speed)
#     if ballrect.left < 0 or ballrect.right > width:
#         speed[0] = -speed[0]
#     if ballrect.top < 0 or ballrect.bottom > height:
#         speed[1] = -speed[1]

#     #screen.fill(black)
#     screen.blit(ball, ballrect) # blit is put on top
#     pygame.display.flip()       # flip is render/put on scree
