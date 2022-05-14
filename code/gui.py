# gui.py  - displays things
#         - recieves the input
# This will send the input to the game.py
#       Recieve back the new_map
# display the new map
import sys
import pygame
from game import Game
pygame.init()


def guiloop():
    # define a few variables
    size = width, height = 16 * 25, 9 * 25
    # black = 50, 0, 0

    # initialise the display window
    screen = pygame.display.set_mode(size)

    # Initialise the game
    game = Game()

    # Load the map
    c_map = game.get_map()

    # load assets into dict

    image_assets = {
        "Player": pygame.image.load("assets/Frog.png"),
        "Barrel": pygame.image.load("assets/Barrel.png"),
        "Frog": pygame.image.load("assets/Frog.png"),
    }
    # print(c_map)
    c_map = c_map.map

    # pl_frogrect = pl_frog_all.get_rect()

    # Initialises the entire world
    # world = pygame.Surface((len(c_map) * 25, len(c_map[0] * 25)))
    for row in range(len(c_map)):           # i is x
        for col in range(len(c_map[row])):    # row is y
            for k in c_map[row][col]:
                imgk = image_assets[k.name]
                # imgkrect.move((-col * 25, -row * 25))
                # world.blit(imgk, imgkrect)
                screen.blit(imgk, (col * 25, row * 25))

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
#     pygame.display.flip()       # flip is render/put on screen
