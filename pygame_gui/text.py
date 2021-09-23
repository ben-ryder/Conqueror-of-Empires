"""
A module holding the pygame_gui Text class.

Classes:
    Text
"""

import pygame


class Text:
    """ The Text class which can be used to create a font and display text. """
    def __init__(self, text, size, colour, font, x, y):
        """
        Parameters:
            text - The text to display.
            size - The font size to use.
            colour - The colour to use when rendering the text.
            font - The font to use for the text, supplied as a path to a font file.
            x - The x position for the text, in px.
            y - The y position for the text, in px.
        """

        self.text = text
        self.x = x  # pylint: disable=invalid-name
        self.y = y  # pylint: disable=invalid-name
        self.size = size
        self.colour = colour
        self.font = font
        self._config_font()
        self._config_text()

    def _config_font(self):
        """ Used internally to configure the required font. """

        try:
            self.graphic_font = pygame.font.Font(self.font, self.size)
        except OSError:  # can't read font file.
            self.graphic_font = pygame.font.SysFont(self.font, self.size)

    def _config_text(self):
        """ Used internally to render the required text using the current font. """

        self.graphic_text = self.graphic_font.render(self.text, True, self.colour)
        self.rect = self.graphic_text.get_rect().move(self.x, self.y)

    def get_rect(self):
        """ Return the rect of the current text rendered. """

        return self.rect

    def change_text(self, text):
        """
        Update the displayed text to the new text supplied.

        Parameters:
            text - The new text to display.
        """
        self.text = text
        self._config_text()

    def draw(self, display):
        """
        Blit the text to the given pygame display.

        Parameters:
            display - A pygame.display instance.
        """

        display.blit(self.graphic_text, [self.x, self.y])
