"""
A module holding the pygame_gui Checkbox class.

Classes:
    Checkbox
"""

import pygame
import pygame_gui.image


class Checkbox:
    """ The Checkbox class which when clicked will toggle a Checkbox.active property. """
    def __init__(self, rest_image, hover_image, active_image, active_hover_image, x, y):
        """
        Parameters:
            rest_image - The default image which is used for an in-active checkbox.
            hover_image - The hover image to use for an in-active checkbox.
            active_image - The image to use when the checkbox is active (checked).
            active_hover_image - The hover image to show when the checkbox is active (checked).
            x - The x position to use for the checkbox, in px.
            y - The y position to use for the checkbox, in px
        """

        self.rest_image = pygame_gui.Image(rest_image, x, y)
        self.hover_image = pygame_gui.Image(hover_image, x, y)
        self.active_image = pygame_gui.Image(active_image, x, y)
        self.active_hover_image = pygame_gui.Image(active_hover_image, x, y)
        self.rect = self.rest_image.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.active = False

    def mouse_over(self):
        """ Checks if the current mouse position is within the checkboxes area. """

        if self.rect.collidepoint(pygame.mouse.get_pos()):
            return True
        return False

    def check_clicked(self):
        """
        Uses Checkbox.mouse_over to determine if the mouse is within the checkboxes area.
        If the mouse is within the checkbox then Checkbox.active will be set to not Checkbox.active.

        NOTE: It is assumed that this will be run while testing a pygame.MOUSEBUTTONDOWN event.
        """

        if self.mouse_over():
            self.active = not self.active
            return True
        return False

    def draw(self, display):
        """
        Draws the checkbox to the given pygame display.

        Parameters:
            display - A pygame.display instance.
        """

        if self.mouse_over():
            if self.active:
                self.active_hover_image.draw(display)
            else:
                self.hover_image.draw(display)
        else:
            if self.active:
                self.active_image.draw(display)
            else:
                self.rest_image.draw(display)
