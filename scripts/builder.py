# Map Builder

import json
import pygame
import csv
import math
import time

Width = 16
Height = 9
Zoom = 2
CamPos = [0, 0]
SpriteRes = 25
WindowScale = 3
NewRes = SpriteRes*WindowScale
debounce = int(round(time.time() * 1000))
SelectedTile = 0

# import map files
MFile = open("../maps/Default.json")
MapFile = open("../maps/Map1.csv")

# read map files
MetaData = json.load(MFile)
Map = csv.reader(MapFile)
Data = list(Map)
MapFile.close()
MapDims = [Data[1].__len__(), Data.__len__()]

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


BaseMaplist = [[cellinterp(cell) for cell in row] for row in Data]

Window = pygame.display.set_mode((Width*NewRes, Height*NewRes + NewRes))


def drawscreen(maplist: list, top: int, left: int, zoom: int):
    """Loop through Screen and blit tiles"""
    pygame.draw.rect(
        Window,
        (20, 20, 20),
        pygame.Rect(0,0,Width*SpriteRes*WindowScale,(Height+1)*SpriteRes*WindowScale)
    )

    for i in range(math.ceil(Width*(WindowScale/zoom))):
        for j in range((1+WindowScale-Zoom)+math.ceil(Height*(WindowScale/zoom))):
            tile = maplist[(j + top) % maplist.__len__()][(i + left) % maplist[1].__len__()]
            for surf in tile:
                w, h = surf.get_size()
                Window.blit(
                    pygame.transform.scale(surf, (zoom*w, zoom*h)),
                    (i*SpriteRes*zoom, j*SpriteRes*zoom),
                    (0, 0, SpriteRes*zoom, SpriteRes*zoom)
                )
    # Draw a black rectange for sprite options to sit on
    pygame.draw.rect(
        Window,
        (0, 0, 0),
        pygame.Rect(SpriteRes-2, Height*NewRes+SpriteRes-2, Width*NewRes-SpriteRes*2-14, SpriteRes+4)
    )
    # Draw a white rectange for the currently selected sprite
    pygame.draw.rect(
        Window,
        (255, 255, 255),
        pygame.Rect((((SpriteRes+2)*SelectedTile)+SpriteRes-2), (Height*NewRes)+SpriteRes-2, SpriteRes+4, SpriteRes+4)
    )
    drawselectables(All)


def drawselectables(surfaces: list):
    """Place selectable options"""
    c = 0
    for surf in surfaces:
        Window.blit(surf, ((c*1.09)*SpriteRes+SpriteRes, NewRes*Height+SpriteRes), (0, 0, SpriteRes, SpriteRes))
        c = c + 1


def selecttile(click: tuple) -> int:
    """retuns the index of the clicked tile"""
    tileindex = math.floor(click[0]/(SpriteRes+2) - 1)
    return tileindex


def clickedindex(click: tuple, campos: list) -> tuple:
    """return the row and column of the clicked tile"""
    index = list()
    for i in range(click.__len__()):
        index.append(
            (math.floor(click[i]/(SpriteRes*Zoom))+campos[i]) % MapDims[i]
        )
    return tuple(index)


drawscreen(BaseMaplist, CamPos[1], CamPos[0], Zoom)
pygame.display.flip()


def writemap(dat: list):
    file = open("../maps/map1.csv", "w", newline='')
    mapwriter = csv.writer(file)
    for row in dat:
        mapwriter.writerow(row)
    file.close()


writemap(Data)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                CamPos[1] = CamPos[1] - 1
            if event.key == pygame.K_DOWN:
                CamPos[1] = CamPos[1] + 1
            if event.key == pygame.K_LEFT:
                CamPos[0] = CamPos[0] - 1
            if event.key == pygame.K_RIGHT:
                CamPos[0] = CamPos[0] + 1

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                Click = pygame.mouse.get_pos()
                if Click[1] < Height*NewRes:
                    ind = clickedindex(Click, CamPos)
                    Data[ind[1]][ind[0]] += AllChar[SelectedTile]
                    print(ind)
                    writemap(Data)

                if Height*NewRes+SpriteRes < Click[1] < Height*NewRes+(2 * SpriteRes):
                    SelectedTile = selecttile(Click)

            if event.button == pygame.BUTTON_RIGHT:
                Click = pygame.mouse.get_pos()
                if Click[1] < Height * NewRes:
                    ind = clickedindex(Click, CamPos)
                    Data[ind[1]][ind[0]] = Data[ind[1]][ind[0]].rstrip(Data[ind[1]][ind[0]][-1])
                    writemap(Data)

        if event.type == pygame.MOUSEWHEEL and int(round(time.time() * 1000)) > debounce:
            debounce = int(round(time.time() * 1000)) + 150
            Zoom = Zoom + event.y
            Zoom = 1 if Zoom < 1 else Zoom
            Zoom = WindowScale if Zoom > WindowScale else Zoom

        BaseMaplist = [[cellinterp(cell) for cell in row] for row in Data]
        drawscreen(BaseMaplist, CamPos[1], CamPos[0], Zoom)
        pygame.display.flip()
