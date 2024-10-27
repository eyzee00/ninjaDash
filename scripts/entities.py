# Description: This file contains the PhysicsEntity class,
# which is a class that represents a physics entity in the game.
# It is a base class for all entities that have physics in the game.
# the update method of the PhysicsEntity class is used to update the entity's position,
# while checking for collisions with the tilemap.

import pygame
from scripts.utils import Animation

# define the PhysicsEntity class
class PhysicsEntity:
    # define the constructor with the game, entity type, position, and size as parameters
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        # create a velocity vector for the entity
        self.velocity = [0, 0]
        # create a dictionary to store the collision flags to keep track of the collisions
        self.collision_flags = {'up': False, 'down': False, 'right': False, 'left': False}

        self.action = ''
        self.anim_offset = (-3, -3)
        self.flip = False
        self.set_action('idle')

    # define a method to get the rect of the entity needed for collision detection
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()

    # define a method to update the entity's position while checking for collisions
    def update(self, tilemap, movement=(0, 0)):
        # set the collision flags to false at the start of the frame
        self.collision_flags = {'up': False, 'down': False, 'right': False, 'left': False}
        # add the movement vector to the velocity vector to move the entity
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

        # move the entity in the x direction
        self.pos[0] += frame_movement[0]

        # get the rect of the entity
        entity_rect = self.rect()
        # loop through the neighboring tiles to check for collisions
        for tile_rect in tilemap.neighboring_tiles_physics(self.pos):
            # check if the entity rect collides with the current tile rect
            if entity_rect.colliderect(tile_rect):

                # draw the tile rect for debugging and seeing collisions in real-time
                # pygame.draw.rect(self.game.screen, (255, 0, 0), tile_rect, 1)

                # check the direction of the movement and adjust the entity's position accordingly
                if frame_movement[0] > 0:
                    entity_rect.right = tile_rect.left
                    self.collision_flags['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = tile_rect.right
                    self.collision_flags['left'] = True
                # set the entity's position to the adjusted position of the entity's rect
                self.pos[0] = entity_rect.x
        
        # apply gravity to the entity (move the entity in the y direction downwards)
        self.pos[1] += frame_movement[1]
        # get the rect of the entity
        entity_rect = self.rect()
        # loop through the neighboring tiles to check for collisions
        for tile_rect in tilemap.neighboring_tiles_physics(self.pos):
            # check if the entity rect collides with the current tile rect
            if entity_rect.colliderect(tile_rect):
                
                # draw the tile rect for debugging and seeing collisions in real-time
                # pygame.draw.rect(self.game.screen, (255, 0, 0), tile_rect, 1)

                # check the direction of the movement and adjust the entity's position accordingly
                if frame_movement[1] > 0:
                    entity_rect.bottom = tile_rect.top
                    self.collision_flags['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = tile_rect.bottom
                    self.collision_flags['up'] = True
                # set the entity's position to the adjusted position of the entity's rect
                self.pos[1] = entity_rect.y

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        # apply gravity to the entity by increasing the y velocity
        self.velocity[1] = min(5, self.velocity[1] + 0.1)

        # check if the entity is colliding with the ground or the ceiling
        if self.collision_flags['up'] or self.collision_flags['down']:
            # if so set the y velocity to 0 to stop the entity from moving in the y direction
            self.velocity[1] = 0
        self.animation.update()

    def render(self, surface, offset=(0, 0)):
        surface.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))
        #surface.blit(self.game.assets['player'], (self.pos[0] - offset[0], self.pos[1] - offset[1]))

class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0
    
    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)

        self.air_time += 1
        if self.collision_flags['down']:
            self.air_time = 0
        if self.air_time > 4:
            self.set_action('jump')
        elif movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')