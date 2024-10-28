#!/usr/bin/env python
# import the pygame module, so you can use it

import sys
import pygame
from scripts.tilemap import Tilemap
from scripts.utils import load_img, load_images


RENDER_SCALE = 2.0
# define a class for the game
class Game:
    # define the init method
    def __init__(self):
        # initialize the pygame module
        pygame.init()

        # set the window title
        pygame.display.set_caption("Level Editor")

        # create a 640x480 screen object
        self.window = pygame.display.set_mode((640, 480), pygame.HWSURFACE | pygame.DOUBLEBUF)

        self.screen = pygame.Surface((320, 240))
        # create a clock object to help control the frame rate
        self.clock = pygame.time.Clock()

        # load the game assets(sprites)
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
        }


        self.tile_list = list(self.assets.keys())
        self.tile_group = 0
        self.tile_variant = 0
        # create a list to store if the player's movement in the x direction
        self.movement = [False, False, False, False]

        self.tilemap = Tilemap(self, 16)
        try:
            self.tilemap.load('map.json')
        except FileNotFoundError:
            pass

        self.scroll = [0, 0]
        self.left_clicking = False
        self.right_clicking = False
        self.shift = False
        self.ongrid = True 
    # define a method to run the game
    def run(self):
        # update the players position and render it each frame
        while True:
            # clear the screen each frame
            self.screen.fill((0, 0, 0))
            
            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
            current_tile_img.set_alpha(100)
            
            self.scroll[0] += (self.movement[1] - self.movement[0]) * 2
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 2
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            self.tilemap.render(self.screen, render_scroll)
            mouse_pos = pygame.mouse.get_pos()
            mouse_pos = (mouse_pos[0] / RENDER_SCALE, mouse_pos[1] / RENDER_SCALE)

            tile_pos = (int((mouse_pos[0] + self.scroll[0]) // self.tilemap.tile_size), int((mouse_pos[1] + self.scroll[1]) // self.tilemap.tile_size))
            if self.ongrid:
                self.screen.blit(current_tile_img, (tile_pos[0] * self.tilemap.tile_size - self.scroll[0], tile_pos[1] * self.tilemap.tile_size - self.scroll[1]))
            else:
                self.screen.blit(current_tile_img, mouse_pos)


            if self.left_clicking and self.ongrid:
                self.tilemap.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1])] = {'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': tile_pos}
            if self.right_clicking:
                tile_key = str(tile_pos[0]) + ';' + str(tile_pos[1])
                if tile_key in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_key]
                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_img = self.assets[tile['type']][tile['variant']]
                    tile_rect = pygame.Rect(tile['pos'][0] - self.scroll[0], tile['pos'][1] - self.scroll[1], tile_img.get_width(), tile_img.get_height())
                    if tile_rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                        self.tilemap.offgrid_tiles.remove(tile)

            self.screen.blit(current_tile_img, (10, 10))
            # set up an event listening loop
            for event in pygame.event.get():
                # if the QUIT event happens, exit the program
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.left_clicking = True
                        if not self.ongrid:
                            self.tilemap.offgrid_tiles.append({'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': (mouse_pos[0] + self.scroll[0], mouse_pos[1] + self.scroll[1])})
                    if event.button == 3:
                        self.right_clicking = True
                    if self.shift:
                        if event.button == 4:
                            self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                            self.tile_variant = 0
                        if event.button == 5:
                            self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                            self.tile_variant = 0
                    else:
                        if event.button == 4:
                            self.tile_variant = (self.tile_variant - 1) % len(self.assets[self.tile_list[self.tile_group]])
                        if event.button == 5:
                            self.tile_variant = (self.tile_variant + 1) % len(self.assets[self.tile_list[self.tile_group]])
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.left_clicking = False
                    if event.button == 3:
                        self.right_clicking = False

                # if the keydown event is triggered
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.movement[2] = True
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.movement[3] = True
                    if event.key == pygame.K_LSHIFT:
                        self.shift = True
                    if event.key == pygame.K_g:
                        self.ongrid = not self.ongrid
                    if event.key == pygame.K_o:
                        self.tilemap.save('map.json')
                    if event.key == pygame.K_t:
                        self.tilemap.autotile()
                # if the keyup event is triggered
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.movement[2] = False
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.movement[3] = False
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False
            # blit the screen to the window and scale it to the window size
            self.window.blit(pygame.transform.scale(self.screen, self.window.get_size()), (0, 0))
            # update the display each iteration of the loop
            pygame.display.update()
            # control the frame rate
            self.clock.tick(60)

# create a game object
game = Game()
game.run()

