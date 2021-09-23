"""
A module holding the pygame_gui Button class.

Classes:
    Button
"""

import pygame
import pygame_gui.image


class Button:
    """ The Button class which changes display when hovered and runs a function when clicked. """
    def __init__(self, rest_image, hover_image, x, y):
        """
        Parameters:
            rest_image - The default image which is used for the button.
            hover_image - The image to use when the button is being hovered over.
            x - The x position to use for the button, in px.
            y - The y position to use for the button, in px
        """

        self.rest_image = pygame_gui.Image(rest_image, x, y)
        self.hover_image = pygame_gui.Image(hover_image, x, y)
        self.rect = self.rest_image.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.function = None

    def set_function(self, function):
        """
        Used to set the function to be run when the button is clicked.

        Parameters:
            function - Should be callable as a function.
        """

        self.function = function

    def mouse_over(self):
        """ Checks if the current mouse position is within the button's area. """
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            return True
        return False

    def check_clicked(self):
        """
        Uses Button.mouse_over to determine if the mouse is within the button's area.
        If the mouse is within the button then Button.function will be ran if set.

        NOTE: It is assumed that this will be run while testing a pygame.MOUSEBUTTONDOWN event.
        """

        if self.mouse_over():
            if self.function is not None:
                self.function()
            return True
        return False

    def draw(self, display):
        """
        Draws the button to the given pygame display.

        Parameters:
            display - A pygame.display instance.
        """

        if self.mouse_over():
            self.hover_image.draw(display)
        else:
            self.rest_image.draw(display)
