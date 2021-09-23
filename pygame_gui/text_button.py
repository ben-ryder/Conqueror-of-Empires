"""
A module holding the pygame_gui TextButton class.

Classes:
    TextButton
"""

import pygame
import pygame_gui.text


class TextButton:
    """ The TextButton which acts like the Button class but doesn't use image assets. """
    def __init__(self, rect, start_transparency, hover_transparency,
                 text, text_size, text_color, text_font):
        """
        Parameters:
            rect - A valid parameter for pygame.Rect. Determines the size & position of the button.
            start_transparency - The initial transparency for the button.
            hover_transparency - The transparency to give the button on hover.
            text - The text to display within the button.
            text_size - The size of the text.
            text_color - The text colour to use. Given as an rgb tuple.
            text_font - The font to use for the text, supplied as a path to a font file.
        """

        self.rect = pygame.Rect(rect)

        self.text = pygame_gui.Text(
            text, text_size, text_color, text_font,
            self.rect.x, self.rect.y
        )
        # Moving text to center in button
        padding_x = (self.rect.width - self.text.rect.width) / 2
        padding_y = (self.rect.height - self.text.rect.height) / 2
        self.text.x += padding_x
        self.text.y += padding_y

        self.panel = pygame_gui.Panel(self.rect, start_transparency, (0, 0, 0))
        self.hover_panel = pygame_gui.Panel(self.rect, hover_transparency, (0, 0, 0))
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
        Uses TextButton.mouse_over to determine if the mouse is within the button's area.
        If the mouse is within the button then TextButton.function will be ran if set.

        NOTE: It is assumed that this will be run while testing a pygame.MOUSEBUTTONDOWN event.
        """

        if self.mouse_over():
            if self.function is not None:
                self.function()
            return True
        return False

    def draw(self, display):
        """
        Draw the text button to the given pygame display.

        Parameters:
            display - A pygame.display instance.
        """

        if self.mouse_over():
            self.hover_panel.draw(display)
        else:
            self.panel.draw(display)
        self.text.draw(display)
