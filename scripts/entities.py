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

        # check if the entity is moving in the right direction in the x axis
        if movement[0] > 0:
            # if so set the flip flag to False
            self.flip = False
        # check if the entity is moving in the left direction in the x axis
        if movement[0] < 0:
            # if so set the flip flag to True
            self.flip = True

        # apply gravity to the entity by increasing the y velocity
        self.velocity[1] = min(5, self.velocity[1] + 0.1)

        # check if the entity is colliding with the ground or the ceiling
        if self.collision_flags['up'] or self.collision_flags['down']:
            # if so set the y velocity to 0 to stop the entity from moving in the y direction
            self.velocity[1] = 0
        self.animation.update()

    # define a method to render the entity
    def render(self, surface, offset=(0, 0)):
        # blit the entity's image to the screen at the entity's position
        # if the entity is facing left, flip the image horizontally else render the image normally
        # blit the entity at the position with the animation offset and the camera offset taken into account
        surface.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))

# define the Player class that inherits from the PhysicsEntity class
class Player(PhysicsEntity):
    # define the constructor with the game, position, and size as parameters
    def __init__(self, game, pos, size):
        # call the constructor of the parent class
        super().__init__(game, 'player', pos, size)
        # set the player's air time to 0
        self.air_time = 0
    
    # define the update method to update the player's position
    def update(self, tilemap, movement=(0, 0)):
        # call the update method of the parent class
        super().update(tilemap, movement=movement)
 
        self.air_time += 1
        # check if the player is on the ground
        if self.collision_flags['down']:
            # if so set the air time to 0
            self.air_time = 0
        # check if the player is in the air
        if self.air_time > 4:
            # if so set the player's action to jump
            self.set_action('jump')
        # if the player is moving in the x direction and is on the ground
        elif movement[0] != 0:
            # set the player's action to run
            self.set_action('run')
        else:
            # if the player is not moving in the x direction and not in the air set the player's action to idle
            self.set_action('idle')
