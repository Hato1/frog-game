# Upcoming Features:

Collision resolver

Step limit before death.

Boost fps. Hitting 14 while idle, and as low as 3 when spamming. Multiprocessing?

Animations that animate instead of teleport. (sliding frogs)

Sound effects

Music

Barrelling barrel

Map Parser Parser:
	Files:
		map.csv
			Each value being a string, with background and entity elements
			Ex: "G;S0;S2" makes grass the basemap, and spawns 2 SpiralingStacys, with initial states 0 and 2
		map.jayson
			specifies tilesets, leaf densities, hues etc
	Functions:
		ParseGraphics(map.csv, map.json) -> listoflistoflistsofsprites OR Map (?)
		make_basemap(map: outputfromParseGraphics) -> pygame.Surface
		ParseEntities(map.csv) -> Map

Let the map continue updating after death after a couple seconds
