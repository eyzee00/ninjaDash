# This file contains the Tilemap class, which is used to render the tilemap of the game.
# it also contains methods to get the neighboring tiles and their rects for collision detection.
# collision detection with the player entity is done in the PhysicsEntity class.
import pygame
import json

AUTOTILE_MAP = {
    tuple(sorted([(1, 0), (0, 1)])): 0,
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
    tuple(sorted([(-1, 0), (0, 1)])): 2, 
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3,
    tuple(sorted([(-1, 0), (0, -1)])): 4,
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,
    tuple(sorted([(1, 0), (0, -1)])): 6,
    tuple(sorted([(1, 0), (0, -1), (0, 1)])): 7,
    tuple(sorted([(1, 0), (-1, 0), (0, 1), (0, -1)])): 8,
}

# define the neighboring offset list containing the relative positions of the neighboring tiles to a tile
NEIGHBORING_OFFSET = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]
# define the collidable tiles set containing the tile types that the player can collide with
COLLIDABLE_TILES = {'grass', 'stone'}
AUTOTILABLE_TILES = {'grass', 'stone'}
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

    def extract(self, id_pairs, keep=False):
        matches = []
        for tile in self.offgrid_tiles.copy():
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())

                if not keep:
                    self.offgrid_tiles.remove(tile)

        for location in self.tilemap:
            tile = self.tilemap[location]
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                matches[-1]['pos'] = matches[-1]['pos'].copy()
                matches[-1]['pos'][0] *= self.tile_size
                matches[-1]['pos'][1] *= self.tile_size
                if not keep:
                    del self.tilemap[location]
        return matches

    def save(self, path):
        file = open(path, 'w')
        json.dump({'tilemap': self.tilemap, 'tile_size': self.tile_size, 'offgrid': self.offgrid_tiles}, file)
        file.close()


    def check_solid(self, pos):
        checked_location = str(int(pos[0] // self.tile_size)) + ';' + str(int(pos[1] // self.tile_size))
        if checked_location in self.tilemap:
            if self.tilemap[checked_location]['type'] in COLLIDABLE_TILES:
                return self.tilemap[checked_location]

    def load(self, path):
        file = open(path, 'r')
        loaded_data = json.load(file)
        file.close()
        self.tilemap = loaded_data['tilemap']
        self.tile_size = loaded_data['tile_size']
        self.offgrid_tiles = loaded_data['offgrid']

    def autotile(self):
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            neighbors = set()
            for shift in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
                check_loc = str(tile['pos'][0] + shift[0]) + ';' + str(tile['pos'][1] + shift[1])
                if check_loc in self.tilemap:
                    if self.tilemap[check_loc]['type'] == tile['type']:
                        neighbors.add(shift)
            neighbors = tuple(sorted(neighbors))
            if (tile['type'] in AUTOTILABLE_TILES) and (neighbors in AUTOTILE_MAP):
                tile['variant'] = AUTOTILE_MAP[neighbors]

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
            surface.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))
        
        for x in range(offset[0] // self.tile_size, (offset[0] + surface.get_width()) // self.tile_size + 1):
            for y in range(offset[1] // self.tile_size, (offset[1] + surface.get_height()) // self.tile_size + 1):
                loc = str(x) + ';' + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    surface.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))
