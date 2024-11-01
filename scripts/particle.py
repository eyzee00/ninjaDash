import pygame

class Particle:
    def __init__(self, game, particle_type, pos, velocity=[0, 0], frame=0):
        self.game = game
        self.type = particle_type
        self.pos = list(pos)
        self.velocity = list(velocity)
        self.animation = self.game.assets['particles/' + particle_type].copy()
        self.animation.frame = frame

    def update(self):
        kill = False
        if self.animation.done:
            kill = True

        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        self.animation.update()

        return kill

    def render(self, surface, offset=(0, 0)):
        particle_img = self.animation.img()
        surface.blit(particle_img, (self.pos[0] - offset[0] - particle_img.get_width() // 2, self.pos[1] - offset[1] - particle_img.get_height() // 2))
