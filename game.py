#!/usr/bin/env python
# import the pygame module, so you can use it

import sys
import pygame
from scripts.tilemap import Tilemap
from scripts.entities import PhysicsEntity, Player
from scripts.utils import load_img, load_images, Animation
from scripts.clouds import Clouds

# define a class for the game
class Game:

    # define the init method
    def __init__(self):
        # initialize the pygame module
        pygame.init()

        # set the window title
        pygame.display.set_caption("Ninja Dash")

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
            'player': load_img('entities/player.png'),
            'background': load_img('background.png'),
            'clouds': load_images('clouds'),
            'player/idle': Animation(load_images('entities/player/idle'), frame_dur=6),
            'player/run': Animation(load_images('entities/player/run'), frame_dur=4),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
        }

        # create a list to store if the player's movement in the x direction
        self.movement_x = [False, False]

        # create a player object
        self.player = Player(self, (50, 50), (8, 15))

        self.tilemap = Tilemap(self, 16)

        self.tilemap.load('map.json')
        self.clouds = Clouds(self.assets['clouds'], count=16)

        self.scroll = [0, 0]

    # define a method to run the game
    def run(self):
        # update the players position and render it each frame
        while True:
            # clear the screen each frame
            self.screen.blit(self.assets['background'], (0, 0))

            self.scroll[0] += (self.player.rect().centerx - self.screen.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.screen.get_height() / 2 - self.scroll[1]) / 30

            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            self.clouds.update()
            self.clouds.render(self.screen, offset=render_scroll)
            self.tilemap.render(self.screen, offset=render_scroll)
            # update the player's position depending on the user's input
            self.player.update(self.tilemap, (self.movement_x[1] - self.movement_x[0], 0))
            # render the player's image
            self.player.render(self.screen, offset=render_scroll)

            # set up an event listening loop
            for event in pygame.event.get():
                # if the QUIT event happens, exit the program
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # if the keydown event is triggered
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement_x[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement_x[1] = True
                    if event.key == pygame.K_UP:
                        self.player.velocity[1] = -3

                # if the keyup event is triggered
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement_x[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement_x[1] = False


            # blit the screen to the window and scale it to the window size
            self.window.blit(pygame.transform.scale(self.screen, self.window.get_size()), (0, 0))
            # update the display each iteration of the loop
            pygame.display.update()
            # control the frame rate
            self.clock.tick(60)

# create a game object
game = Game()
game.run()

