#!/usr/bin/env python
# import the pygame module, so you can use it

import math
import random
import sys
import pygame
from scripts.tilemap import Tilemap
from scripts.entities import PhysicsEntity, Player, Enemy
from scripts.utils import load_img, load_images, Animation
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark

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
            'enemy/idle': Animation(load_images('entities/enemy/idle'), frame_dur=6),
            'enemy/run': Animation(load_images('entities/enemy/run'), frame_dur=4),
            'player/idle': Animation(load_images('entities/player/idle'), frame_dur=6),
            'player/run': Animation(load_images('entities/player/run'), frame_dur=4),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'particles/leaf': Animation(load_images('particles/leaf'), frame_dur=20, loop=False),
            'particles/particle': Animation(load_images('particles/particle'), frame_dur=6, loop=False),
            'gun': load_img('gun.png'),
            'projectile': load_img('projectile.png'),
        }

        # create a list to store if the player's movement in the x direction
        self.movement_x = [False, False]

        # create a player object
        self.player = Player(self, (59, 50), (8, 15))

        self.tilemap = Tilemap(self, 16)
        
        self.load_level(0)


    def load_level(self, map_id):
        self.tilemap.load('data/maps/' + str(map_id) + '.json')
        self.enemies = []
        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], tree['pos'][1], 23, 13))

        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
                self.player.air_time = 0
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))

        self.particles = []
        self.projectiles = []

        self.clouds = Clouds(self.assets['clouds'], count=16)
        self.sparks = []        
        self.scroll = [0, 0]
        self.dead = 0
        self.allowed_hits = 1

    # define a method to run the game
    def run(self):
        # update the players position and render it each frame
        while True:
            # clear the screen each frame
            self.screen.blit(self.assets['background'], (0, 0))

            if self.dead:
                self.dead += 1
                if self.dead > 30:
                    self.load_level(0)
            self.scroll[0] += (self.player.rect().centerx - self.screen.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.screen.get_height() / 2 - self.scroll[1]) / 30

            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            for rect in self.leaf_spawners:
                if random.random() * 49999 < rect.width * rect.height:
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))

            self.clouds.update()
            self.clouds.render(self.screen, offset=render_scroll)
            self.tilemap.render(self.screen, offset=render_scroll)

            for enemy in self.enemies:
                kill = enemy.update(self.tilemap, movement=(0, 0))
                enemy.render(self.screen, offset=render_scroll)
                if kill:
                    self.enemies.remove(enemy)

            if not self.dead:
                # update the player's position depending on the user's input
                self.player.update(self.tilemap, (self.movement_x[1] - self.movement_x[0], 0))
                # render the player's image
                self.player.render(self.screen, offset=render_scroll)

            # projectile object = [[x, y], direction, timer]
            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets['projectile']
                self.screen.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                if self.tilemap.check_solid(projectile[0]):
                    self.projectiles.remove(projectile)
                    for i in range(4):
                        self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))

                elif projectile[2] > 360:
                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing) < 44:
                    if self.player.rect().collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)
                        if not self.allowed_hits:
                            self.dead += 1
                        else:
                            self.allowed_hits -= 1
                        for i in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(Spark(self.player.rect().center, angle=angle, speed=random.random() * 3))
                            self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))

            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.screen, offset=render_scroll)
                if kill:
                    self.sparks.remove(spark)

            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.screen, render_scroll)
                if particle.type == 'leaf':
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.33
                if kill:
                    self.particles.remove(particle)

            
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
                        self.player.jump()
                    if event.key == pygame.K_x:
                        self.player.dash()

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

