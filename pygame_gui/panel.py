"""
A module holding the pygame_gui Panel class.

Classes:
    Panel
"""

import pygame


class Panel:
    """
    A Panel class used to display a simple rectangle 'panel' element.
    """
    def __init__(self, rect, transparency, colour):
        """
        Parameters:
            rect - A pygame.Rect compatible declaration such as [x, y, width, height].
            transparency - An alpha value 0 to 255 used to set the Panel opacity.
            colour - A valid pygame colour in the form (red, green blue).
        """

        self.rect = pygame.Rect(rect)
        self.colour = colour
        self.transparency = transparency
        self.surface = self.make_surface()

    def reset_rect(self, rect):
        """
        Reset the Panel.rect value using the new rect value supplied.

        Parameters:
            rect - Should be a valid pygame.Rect argument.
        """

        self.rect = pygame.Rect(rect)
        self.surface = self.make_surface()

    def reset_width(self, width):
        """
        Reset the Panel.rect.width value using the new width value supplied.

        Parameters:
            width - The new width as an integer.
        """

        self.rect.width = width
        self.surface = self.make_surface()

    def make_surface(self):
        """ Create a surface that is used when displaying the Panel itself. """
        surface = pygame.Surface([self.rect[2], self.rect[3]])
        surface.set_alpha(self.transparency)
        return surface

    def draw(self, display):
        """
        Blit the panel surface to the given pygame display.

        Arguments:
            display - A pygame.display instance.
        """

        self.surface.fill(self.colour)
        display.blit(self.surface, [self.rect[0], self.rect[1]])
