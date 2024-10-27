# This file contains the Tilemap class, which is used to render the tilemap of the game.
# it also contains methods to get the neighboring tiles and their rects for collision detection.
# collision detection with the player entity is done in the PhysicsEntity class.
import pygame

# define the neighboring offset list containing the relative positions of the neighboring tiles to a tile
NEIGHBORING_OFFSET = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]
# define the collidable tiles set containing the tile types that the player can collide with
COLLIDABLE_TILES = {'grass', 'stone'}

# define the Tilemap class
class Tilemap:
    # define the constructor
    def __init__(self, game, tile_size=16):
        self.game = game
        self.tile_size = tile_size
        # create a dictionary to store the tilemap
        self.tilemap = {}
        # create a list to store the offgrid tiles
        self.offgrid_tiles = []

    # define a method to generate the tilemap
        for i in range(10):
            # add a grass tile to the tilemap at the specified horizontal position
            self.tilemap[str(3 + i) + ';10'] = {'type': 'grass', 'variant': 3, 'pos': (3 + i, 10)}
            # add a stone tile to the tilemap at the specified vertical position
            self.tilemap['10;' + str(5 + i)] = {'type': 'stone', 'variant': 0, 'pos': (10, 5 + i)}

    # define a method to get the neighboring tiles relative to a specific position
    def tiles_around(self, pos):
        # create an empty list to store the neighboring tiles
        neighboring_tiles = []
        # get the tile location by dividing the x and y position by the tile size
        tile_location = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        # loop through the neighboring offsets to get the neighboring tiles
        for offset in NEIGHBORING_OFFSET:
            # create a relative tile position by adding the offset to the tile location
            checked_location = str(tile_location[0] + offset[0]) + ';' + str(tile_location[1] + offset[1])
            # check if the checked location key is in the tilemap's keys
            if checked_location in self.tilemap:
                # append the tile to the neighboring tiles list if it is in the tilemap's keys
                neighboring_tiles.append(self.tilemap[checked_location])

        # return the neighboring tiles
        return neighboring_tiles

    # define a method to get the neighboring tiles's rects for collision detection
    def neighboring_tiles_physics(self, pos):
        # create an empty list to store the neighboring tile rects
        rects = []
        # loop through the neighboring tiles to get the rects
        for tile in self.tiles_around(pos):
            # check if the tile type is in the collidable tiles set
            if tile['type'] in COLLIDABLE_TILES:
                # append the rect of the tile to the list
                rects.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))

        # return the list of neighboring tile rects
        return rects

    # define a method to render the tilemap
    def render(self, surface, offset=(0, 0)):
        # loop through the offgrid tiles to render them
        for tile in self.offgrid_tiles:
            # get the asset from the game assets dictionary using the tile type and variant
            surface.blit(self.game.assets[tile['type']][tile['variant']], tile['pos'][0] - offset[0], tile['pos'][1] - offset[1])
        
        for x in range(offset[0] // self.tile_size, (offset[0] + surface.get_width()) // self.tile_size + 1):
            for y in range(offset[1] // self.tile_size, (offset[1] + surface.get_height()) // self.tile_size + 1):
                loc = str(x) + ';' + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    surface.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))