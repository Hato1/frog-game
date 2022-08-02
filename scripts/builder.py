# Map Builder

import json
import pygame
import csv

Width = 16
Height = 9
DefZoom = 3
Zoom = 3
Left = 0
Top = 0
SpriteRes = 25
NewRes = SpriteRes*DefZoom

# import map files
MFile = open("../maps/Default.json")
MapFile = open("../maps/Map1.csv")

# read map files
MetaData = json.load(MFile)
Map = csv.reader(MapFile)

# Extract metadata info we want
Tiles = []
TileChar = []

for TileDict in MetaData['Tiles']:
    AssetPath = "../assets/" + TileDict['FileName']
    Tiles.append(pygame.image.load(AssetPath))
    TileChar.append(TileDict["Character"])

Ents = []
EntChar = []

for EntDict in MetaData['Entities']:
    AssetPath = "../assets/" + EntDict['FileName']
    Ents.append(pygame.image.load(AssetPath))
    EntChar.append(EntDict["Character"])

All = Tiles + Ents
AllChar = TileChar + EntChar


def cellinterp(cell: str) -> list:
    """Takes the string from each cell, returns list of sprites to blit"""
    sprites2blit = []
    for ch in cell:
        index = AllChar.index(ch)
        # make sure state characters done make problems

        sprites2blit.append(All[index])
    return sprites2blit


BaseMaplist = [[cellinterp(cell) for cell in row] for row in Map]

Window = pygame.display.set_mode((Width*NewRes, Height*NewRes + NewRes))


def drawscreen(maplist: list, top: int, left: int, zoom: int):
    """Loop through Screen and blit tiles"""

    for i in range(maplist[1].__len__()):
        for j in range(maplist.__len__()):
            tile = maplist[(j + top) % maplist.__len__()][(i + left) % maplist[1].__len__()]
            for surf in tile:
                w, h = surf.get_size()
                Window.blit(
                    pygame.transform.scale(surf, (zoom*w, zoom*h)),
                    (i*SpriteRes*zoom, j*SpriteRes*zoom),
                    (0, 0, SpriteRes*zoom, SpriteRes*zoom)
                )
    pygame.draw.rect(
        Window,
        (0, 0, 0),
        pygame.Rect(SpriteRes-2, Height*NewRes+SpriteRes-2, Width*NewRes-SpriteRes*2-4, SpriteRes+4)
    )
    placeselectables(All)


def placeselectables(surfaces: list):
    """Place selectable options"""
    c = 0
    for surf in surfaces:
        Window.blit(surf, ((c*1.09)*SpriteRes+SpriteRes, NewRes*Height+SpriteRes), (0, 0, SpriteRes, SpriteRes))
        c = c + 1


drawscreen(BaseMaplist, Top, Left, Zoom)
pygame.display.flip()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                Top = Top - 1
            if event.key == pygame.K_DOWN:
                Top = Top + 1
            if event.key == pygame.K_LEFT:
                Left = Left - 1
            if event.key == pygame.K_RIGHT:
                Left = Left + 1
            drawscreen(BaseMaplist, Top, Left, Zoom)
            pygame.display.flip()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                Click = pygame.mouse.get_pos()
                print("L")
                print(Click)
                # if Click[0] < Height*NewRes:
                #   apply tile function to
                # if Click[0] > Height*NewRes:
                # change selected variable
            if event.button == pygame.BUTTON_RIGHT:
                Click = pygame.mouse.get_pos()
                print("R")
                print(Click)
            drawscreen(BaseMaplist, Top, Left, Zoom)
            pygame.display.flip()
