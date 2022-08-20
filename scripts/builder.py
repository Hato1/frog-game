# Map Builder
import math
from json import dump, load
import pygame
from math import floor, ceil
from time import time, sleep, perf_counter
import pickle

# Declare default values
Width = 16  # number of tiles wide the screen is (make adjustable in the future)
Height = 9  # number of high wide the screen is (make adjustable in the future)
WindowScale = 3  # zoom to calculate window size at (would be better to make adjustable)

# starting values
Zoom = 2  # default zoom level of the screen
CamPos = [0, 0]  # staring (top left) camera position
SpriteRes = 25  # resolution single tile sprites (1x1)

# calculate
NewRes = SpriteRes*WindowScale
debounce = int(round(time() * 1000))  # set how much input debounce we want
Fps = 15  # set refresh rate
Save_Delay = 1  # Save wait time in secodns
Save_cycles = math.floor(Fps*Save_Delay)
Action_flag = True
Save_counter = Save_cycles + 1
MouseDown = False
SelectedTile = 0
Saved = "Saved"

# select which map to edit
FileName = "Map1"

# import files
MFile = open("../maps/Default.json")  # Metadata Jason File
try:
    MapFile = open("../maps/Map1.map", "rb")  # Map CSV File
except FileNotFoundError:
    Data = []

# read map files from pickle
MetaData = load(MFile)
try:
    Data = pickle.load(MapFile)
    MapFile.close()
except NameError:
    Data = []
MapDims = MetaData['MapSize']

# Incert or remove row until matches row number specified in CSV
diff = MapDims[1] - len(Data)
if diff < 0:
    Data = Data[:diff]
if diff > 0:
    for i in range(diff):
        Data.append(list())

# ensure each list matchs the length if not place a stone background time or remove tiles
for row in Data:
    diff = MapDims[0] - len(row)
    if diff < 0:
        row = row[:diff]
    if diff > 0:
        for i in range(diff):
            row.extend([[["Stone"]]])

# Extract metadata info we want
Tiles = []
TileName = []

for TileDict in MetaData['Tiles']:
    AssetPath = "../assets/" + TileDict['FileName']
    Tiles.append(pygame.image.load(AssetPath))
    TileName.extend([TileDict['level']])

TileType = [0] * len(TileName)
Ents = []
EntName = []

for EntDict in MetaData['Entities']:
    AssetPath = "../assets/" + EntDict['FileName']
    Ents.append(pygame.image.load(AssetPath))
    EntName.extend([EntDict['Name']])

EntType = [1] * len(EntName)

All = Tiles + Ents
AllName = TileName + EntName
AllType = TileType + EntType


def amendtransparent(surf: pygame.Surface) -> pygame.Surface:
    """if a tile is tranparent replace it with a red cross"""
    alpha = pygame.transform.average_color(surf.convert_alpha())
    if alpha[-1] == 0:
        surf = pygame.image.load("../assets/TransparentME.png")
    return surf


def cellinterp(cell: list) -> list:
    """Takes the string from each cell, returns list of sprites to blit"""
    sprites2blit = []
    for names in cell:
        index = AllName.index(names[0])
        sprites2blit.append(All[index])
    return sprites2blit


def drawscreen(maplist: list, top: int, left: int, zoom: int):
    """Loop through Screen and blit tiles"""
    # Draw a grey rectangle over all screen to blank
    pygame.draw.rect(
        Window,
        (20, 20, 20),
        pygame.Rect(0, 0, Width*SpriteRes*WindowScale, (Height+1)*SpriteRes*WindowScale)
    )

    # loop over every tile on display in the map and blit sprite
    for i2 in range(ceil(Width*(WindowScale/zoom))):
        if -1 < i2 + left < len(maplist[1]):  # only run if in range
            for j in range((1+WindowScale-Zoom)+ceil(Height*(WindowScale/zoom))):
                if -1 < j + top < len(maplist):  # only run if in range
                    tile1 = maplist[(j + top) % len(maplist)][(i2 + left) % len(maplist[1])]
                    for surf in tile1:
                        w, h = surf.get_size()
                        Window.blit(
                            pygame.transform.scale(surf, (zoom*w, zoom*h)),
                            (i2*SpriteRes*zoom, j*SpriteRes*zoom),
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
    indexes = 0
    for surfnum, surf in enumerate(surfaces):
        Window.blit(surf, ((surfnum*1.09)*SpriteRes+SpriteRes, NewRes*Height+SpriteRes), (0, 0, SpriteRes, SpriteRes))


def selecttile(click: tuple) -> int:
    """retuns the index of the clicked tile"""
    tileindex = floor(click[0]/(SpriteRes+2) - 1)
    return tileindex


def clickedindex(click: tuple, campos: list) -> tuple:
    """return the row and column of the clicked tile"""
    index = list()
    for i1 in range(len(click)):
        index.append(
            (floor(click[i1]/(SpriteRes*Zoom))+campos[i1]) % MapDims[i1]
        )
    return tuple(index)


def writemappickle(dat: list):
    """Save the map file to a pickle"""
    file = open("../maps/map1.map", "wb")
    pickle.dump(dat, file)


def applytile(maplist: list, tile: list, tiletype: int) -> list:
    """Take the current selected tile object and apply to map"""
    if tiletype == 1:
        tile = list([tile])
        maplist.append(tile)
    if tiletype == 0:
        liststr = list(maplist)
        liststr[0] = list([tile])
        maplist = liststr
    return maplist


# initalise map
BaseMaplist = [[cellinterp(cell) for cell in row] for row in Data]

Window = pygame.display.set_mode((Width*NewRes, Height*NewRes + NewRes))
pygame.display.set_caption(f'Frog game editor{FileName} ({Saved})')

for i3 in range(len(All)):
    All[i3] = amendtransparent(All[i3])

drawscreen(BaseMaplist, CamPos[1], CamPos[0], Zoom)

pygame.display.flip()

while True:
    t1_start = perf_counter()  # start the cycle time counter

    # handle pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)

        # use arrow keys to navigate the map
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
            MouseDown = True
            # on left click
            if event.button == pygame.BUTTON_LEFT:
                ClickDown = pygame.mouse.get_pos()

                # If clicking on editable area apply currently selected tile
                if ClickDown[1] < Height*NewRes and AllType[SelectedTile] == 1:
                    Action_flag = False  # reset the save timer
                    Saved = "Unsaved"
                    pygame.display.set_caption(f'Frog game editor{FileName} ({Saved})')
                    ind = clickedindex(ClickDown, CamPos)
                    Data[ind[1]][ind[0]] = applytile(Data[ind[1]][ind[0]], AllName[SelectedTile], AllType[SelectedTile])

                # If clicking on tile selection area adjust selected tile
                if Height*NewRes+SpriteRes < ClickDown[1] < Height*NewRes+(2 * SpriteRes):
                    SelectedTile = selecttile(ClickDown)

            # on right click delet top entity
            if event.button == pygame.BUTTON_RIGHT:
                ClickDown = pygame.mouse.get_pos()

                # Remove top entity if it exists
                if ClickDown[1] < Height * NewRes:
                    ind = clickedindex(ClickDown, CamPos)
                    if len(Data[ind[1]][ind[0]]) > 1:
                        Action_flag = False  # reset the save timer
                        Saved = "Unsaved"
                        pygame.display.set_caption(f'Frog game editor{FileName} ({Saved})')
                        Data[ind[1]][ind[0]] = Data[ind[1]][ind[0]][:-1]

        # if clickup with background tile type selected do a drag
        if event.type == pygame.MOUSEBUTTONUP:
            MouseDown = False
            if AllType[SelectedTile] == 0 and event.button == pygame.BUTTON_LEFT:
                ClickUp = pygame.mouse.get_pos()
                if ClickUp[1] < Height*NewRes > ClickDown[1]:
                    Action_flag = False  # reset the save timer
                    Saved = "Unsaved"
                    pygame.display.set_caption(f'Frog game editor{FileName} ({Saved})')

                    IndexDown = clickedindex(ClickDown, CamPos)
                    IndexUp = clickedindex(ClickUp, CamPos)

                    rows = IndexUp[1] - IndexDown[1]
                    cols = IndexUp[0] - IndexDown[0]

                    if rows < 0:
                        rs = -1
                    else:
                        rs = 1
                    rows = abs(rows)+1

                    if cols < 0:
                        cs = -1
                    else:
                        cs = 1
                    cols = abs(cols)+1

                    for r in range(rows):
                        for c in range(cols):
                            Data[IndexDown[1]+(r*rs)][IndexDown[0]+(c*cs)] = applytile(
                                Data[IndexDown[1]+(r*rs)][IndexDown[0]+(c*cs)],
                                AllName[SelectedTile],
                                AllType[SelectedTile]
                            )

        # on scroll zoom
        if event.type == pygame.MOUSEWHEEL and int(round(time() * 1000)) > debounce:
            debounce = int(round(time() * 1000)) + 150
            Zoom = Zoom + event.y
            Zoom = 1 if Zoom < 1 else Zoom
            Zoom = WindowScale if Zoom > WindowScale else Zoom

        # redarw map now event is resolved
        BaseMaplist = [[cellinterp(cell) for cell in row] for row in Data]
        drawscreen(BaseMaplist, CamPos[1], CamPos[0], Zoom)
        pygame.display.flip()

    # if mouse state is down highligh selected cells
    if MouseDown is True and AllType[SelectedTile] == 0:
        MousePos = pygame.mouse.get_pos()
        BaseMaplist = [[cellinterp(cell) for cell in row] for row in Data]
        drawscreen(BaseMaplist, CamPos[1], CamPos[0], Zoom)
        pygame.draw.rect(
            Window,
            (255, 255, 255),
            pygame.Rect(
                min(ClickDown[0], MousePos[0]),
                min(ClickDown[1], MousePos[1]),
                abs(MousePos[0]-ClickDown[0]),
                abs(MousePos[1]-ClickDown[1])),
            2)
        pygame.display.flip()

    # Save map to pickle file
    if Action_flag is False:  # If an action occurs
        Save_counter = 0  # Reset save delay
        Action_flag = True  # Reset action flag to true

    Save_counter = Save_counter + 1  # Increment counter eah time the code runs

    # Once save delay is met save the file
    if Save_counter == Save_cycles:
        writemappickle(Data)
        f = open("test.txt", "w")
        dump(Data, f)
        f.close()
        Saved = "Saved"
        pygame.display.set_caption(f'Frog game editor{FileName} ({Saved})')

    # sleep to maintain a constant frame time
    runtime = perf_counter()-t1_start
    # print(runtime)
    if runtime > (1/Fps):
        runtime = 0
    sleep((1/Fps)-runtime)
