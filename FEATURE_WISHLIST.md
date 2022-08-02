# Upcoming Features:

Collision detector

Collision resolver

Step limit before death.

Boost fps. Hitting 14 while idle, and as low as 3 when spamming. Multiprocessing?

Map Parser Parser:
	Files:
		map.csv
			Each value being an odd length string, first being background, then alternating entity and entity state
			Ex: "GS0S2" makes grass the basemap, and spawns 2 SpiralingStacys, with initial states 0 and 2
		map.jayson
			specifies tilesets, leaf densities, hues etc
	Functions:
		ParseGraphics(map.csv, map.json) -> listoflistoflistsofsprites OR Map (?)
		make_basemap(map: outputfromParseGraphics) -> pygame.Surface
		ParseEntities(map.csv) -> Map
