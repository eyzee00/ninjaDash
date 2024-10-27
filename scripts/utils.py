# utils module is a collection of functions that are used throughout the game.

# necessary imports
import pygame
import os

# define the base path for the images
BASE_PATH = 'data/images/'

# define a function to load an image
def load_img(path):
    # load the image from the path and convert it to a pygame image object
    img = pygame.image.load(BASE_PATH + path).convert()
    # set the colorkey of the image to (0, 0, 0) to make the black background transparent
    img.set_colorkey((0, 0, 0))
    return img

# define a function to load a list of images
def load_images(path):
    # create an empty list to store the images
    images = []

    # loop through the files in the specified path
    for image_name in os.listdir(BASE_PATH + path):
        # load each image and append it to the list
        images.append(load_img(path + '/' + image_name))
    
    return images

class Animation:
    def __init__(self, frames, frame_dur=5, loop=True):
        self.frames = frames
        self.frame_duration = frame_dur
        self.loop = loop
        self.done = False
        self.current_frame = 0

    def copy(self):
        return Animation(self.frames, self.frame_duration, self.loop)

    def update(self):
        if self.loop:
            self.current_frame = (self.current_frame + 1) % (self.frame_duration * len(self.frames))
        else:
            self.current_frame = min(self.current_frame + 1, self.frame_duration * len(self.frames) - 1)
        if self.current_frame >= (self.frame_duration * len(self.frames) - 1):
            self.done = True

    def img(self):
        return self.frames[int(self.current_frame / self.frame_duration)]