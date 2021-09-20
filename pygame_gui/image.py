"""
A module holding the pygame_gui Image class.

Classes:
    Image
"""

import pygame


class Image:
    """ An Image class to hold and display a pygame.image instance. """
    def __init__(self, image_ref, x, y):
        """
        Parameters:
            image_ref - A file path to the image to load and use.
            x - The x position to use for the image, in px.
            y - The y position to use for the image, in px.
        """

        self.image = pygame.image.load(image_ref).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self, display):
        """
        Blit the image to the given pygame display.

        Parameters:
            display - A pygame.display instance.
        """

        display.blit(self.image, self.rect.topleft)
