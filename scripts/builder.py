# Map Builder

from json import load
import pygame as pg
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
Debounce = int(round(time() * 1000))  # set how much input debounce we want
Fps = 15  # set refresh rate
SaveDelay = 1  # Save wait time in secodns
SaveCycles = floor(Fps * SaveDelay)
ActionFlag = True
SaveCounter = SaveCycles + 1
MouseDown = False
SelectedTile = 0
Saved = "Saved"
ClickDown = tuple
ScreenSurf = pg.Surface

# select which map to edit
FileName = "map1"

# import files
MFile = open("../maps/Default.json")  # Metadata Jason File
try:
    MapFile = open("../maps/map1.map", "rb")  # Map CSV File
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
    Tiles.append(pg.image.load(AssetPath))
    TileName.extend([TileDict['level']])

TileType = [0] * len(TileName)
Ents = []
EntName = []

for EntDict in MetaData['Entities']:
    AssetPath = "../assets/" + EntDict['FileName']
    Ents.append(pg.image.load(AssetPath))
    EntName.extend([EntDict['Name']])

EntType = [1] * len(EntName)

All = Tiles + Ents
AllName = TileName + EntName
AllType = TileType + EntType


def amendtransparent(surf: pg.Surface) -> pg.Surface:
    """if a tile is tranparent replace it with a red cross"""
    alpha = pg.transform.average_color(surf.convert_alpha())
    if alpha[-1] == 0:
        surf = pg.image.load("../assets/TransparentME.png")
    return surf


def cellinterp(cell: list) -> list:
    """Takes the string from each cell, returns list of sprites to blit"""
    sprites2blit = []
    for names in cell:
        index = AllName.index(names[0])
        sprites2blit.append(All[index])
    return sprites2blit


def drawscreen(screen: pg.Surface, window: pg.surface.Surface) -> None:
    """Loop through Screen and blit tiles"""
    # Draw a grey rectangle over all screen to blank
    pg.draw.rect(
        window,
        (20, 20, 20),
        pg.Rect(0, 0, Width * SpriteRes * WindowScale, (Height + 1) * SpriteRes * WindowScale)
    )

    # loop over every tile on display in the map and blit sprite
    window.blit(screen, (0, 0))

    # Draw a black rectange for sprite options to sit on
    pg.draw.rect(
        window,
        (0, 0, 0),
        pg.Rect(SpriteRes - 2, Height * NewRes + SpriteRes - 2, Width * NewRes - SpriteRes * 2 - 14, SpriteRes + 4)
    )
    # Draw a white rectange for the currently selected sprite
    pg.draw.rect(
        window,
        (255, 255, 255),
        pg.Rect((((SpriteRes + 2) * SelectedTile) + SpriteRes - 2), (Height * NewRes) + SpriteRes - 2, SpriteRes + 4,
                SpriteRes + 4)
    )
    drawselectables(All, window)


def drawselectables(surfaces: list, window: pg.surface.Surface) -> None:
    """Place selectable options"""
    for surfnum, surf in enumerate(surfaces):
        window.blit(surf, ((surfnum*1.09)*SpriteRes+SpriteRes, NewRes*Height+SpriteRes), (0, 0, SpriteRes, SpriteRes))


def createmapsurf(maplist: list, top: int, left: int, zoom: int) -> pg.Surface:
    """loop over every tile on display and create a surface of the map"""
    mapsurf = pg.Surface((Width * NewRes, Height * NewRes + NewRes))
    for i2 in range(ceil(Width * (WindowScale / zoom))):
        if -1 < i2 + left < len(maplist[1]):  # only run if in range
            for j in range((1 + WindowScale - Zoom) + ceil(Height * (WindowScale / zoom))):
                if -1 < j + top < len(maplist):  # only run if in range
                    tile1 = maplist[(j + top) % len(maplist)][(i2 + left) % len(maplist[1])]
                    for surf in tile1:
                        w, h = surf.get_size()
                        mapsurf.blit(
                            pg.transform.scale(surf, (zoom * w, zoom * h)),
                            (i2 * SpriteRes * zoom, j * SpriteRes * zoom),
                            (0, 0, SpriteRes * zoom, SpriteRes * zoom)
                        )
    return mapsurf


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


def writemappickle(dat: list) -> None:
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


def mainloop(window: pg.display) -> None:
    global Zoom
    global SelectedTile
    global ClickDown
    global Debounce
    global MouseDown
    global ScreenSurf
    global ActionFlag
    global SaveCounter
    t1_start = perf_counter()  # start the cycle time counter

    # handle pygame events
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit(0)

        # use arrow keys to navigate the map
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_UP:
                CamPos[1] = CamPos[1] - 1
            if event.key == pg.K_DOWN:
                CamPos[1] = CamPos[1] + 1
            if event.key == pg.K_LEFT:
                CamPos[0] = CamPos[0] - 1
            if event.key == pg.K_RIGHT:
                CamPos[0] = CamPos[0] + 1

        if event.type == pg.MOUSEBUTTONDOWN:
            MouseDown = True
            # on left click
            if event.button == pg.BUTTON_LEFT:
                ClickDown = pg.mouse.get_pos()

                # If clicking on editable area apply currently selected tile
                if ClickDown[1] < Height*NewRes and AllType[SelectedTile] == 1:
                    ActionFlag = False  # reset the save timer
                    pg.display.set_caption(f'Frog game editor{FileName} (Unsaved)')
                    ind = clickedindex(ClickDown, CamPos)
                    Data[ind[1]][ind[0]] = applytile(Data[ind[1]][ind[0]], AllName[SelectedTile], AllType[SelectedTile])

                # If clicking on tile selection area adjust selected tile
                if Height*NewRes+SpriteRes < ClickDown[1] < Height*NewRes+(2 * SpriteRes):
                    SelectedTile = selecttile(ClickDown)

            # on right click delet top entity
            if event.button == pg.BUTTON_RIGHT:
                ClickDown = pg.mouse.get_pos()

                # Remove top entity if it exists
                if ClickDown[1] < Height * NewRes:
                    ind = clickedindex(ClickDown, CamPos)
                    if len(Data[ind[1]][ind[0]]) > 1:
                        ActionFlag = False  # reset the save timer
                        pg.display.set_caption(f'Frog game editor{FileName} (Unsaved)')
                        Data[ind[1]][ind[0]] = Data[ind[1]][ind[0]][:-1]

        # if clickup with background tile type selected do a drag
        if event.type == pg.MOUSEBUTTONUP:
            MouseDown = False
            if AllType[SelectedTile] == 0 and event.button == pg.BUTTON_LEFT:
                click_up = pg.mouse.get_pos()
                if click_up[1] < Height*NewRes > ClickDown[1]:
                    ActionFlag = False  # reset the save timer
                    pg.display.set_caption(f'Frog game editor{FileName} (Unsaved)')

                    index_down = clickedindex(ClickDown, CamPos)
                    index_up = clickedindex(click_up, CamPos)

                    rows = index_up[1] - index_down[1]
                    cols = index_up[0] - index_down[0]

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
                            Data[index_down[1]+(r*rs)][index_down[0]+(c*cs)] = applytile(
                                Data[index_down[1]+(r*rs)][index_down[0]+(c*cs)],
                                AllName[SelectedTile],
                                AllType[SelectedTile]
                            )

        # on scroll zoom
        if event.type == pg.MOUSEWHEEL and int(round(time() * 1000)) > Debounce:
            Debounce = int(round(time() * 1000)) + 150
            Zoom = Zoom + event.y
            Zoom = 1 if Zoom < 1 else Zoom
            Zoom = WindowScale if Zoom > WindowScale else Zoom

        # redarw map now event is resolved
        base_map_list = [[cellinterp(cell) for cell in row1] for row1 in Data]
        ScreenSurf = createmapsurf(base_map_list, CamPos[1], CamPos[0], Zoom)
        drawscreen(ScreenSurf, window)
        pg.display.flip()

    # if mouse state is down highligh selected cells
    if MouseDown is True and AllType[SelectedTile] == 0:
        mousepos = pg.mouse.get_pos()
        drawscreen(ScreenSurf, window)
        pg.draw.rect(
            window,
            (255, 255, 255),
            pg.Rect(
                min(ClickDown[0], mousepos[0]),
                min(ClickDown[1], mousepos[1]),
                abs(mousepos[0]-ClickDown[0]),
                abs(mousepos[1]-ClickDown[1])),
            2)
        pg.display.flip()

    # Save map to pickle file
    if ActionFlag is False:  # If an action occurs
        SaveCounter = 0  # Reset save delay
        ActionFlag = True  # Reset action flag to true

    SaveCounter = SaveCounter + 1  # Increment counter eah time the code runs

    # Once save delay is met save the file
    if SaveCounter == SaveCycles:
        writemappickle(Data)
        pg.display.set_caption(f'Frog game editor{FileName} (Saved)')

    # sleep to maintain a constant frame time
    runtime = perf_counter()-t1_start
    # print(runtime)
    if runtime > (1/Fps):
        runtime = 0
    sleep((1/Fps)-runtime)


def main() -> None:
    # Initialise
    basemaplist = [[cellinterp(cell) for cell in row1] for row1 in Data]  # make list to be used as screen
    window = pg.display.set_mode((Width * NewRes, Height * NewRes + NewRes))  # set display size
    for i3, sprite in enumerate(All):
        All[i3] = amendtransparent(sprite)
    pg.display.set_caption(f'Frog game editor{FileName}')
    screensurf = createmapsurf(basemaplist, CamPos[1], CamPos[0], Zoom)
    drawscreen(screensurf, window)
    pg.display.flip()

    while True:
        mainloop(window)


main()
