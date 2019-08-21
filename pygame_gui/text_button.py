# Ben-Ryder 2019


import pygame
import pygame_gui.text


class TextButton:
    def __init__(self, rect, start_transparency, hover_transparancy,
                 text, text_size, text_color, text_font):
        self.rect = pygame.Rect(rect)

        self.text = pygame_gui.Text(text, text_size, text_color, text_font, self.rect.x, self.rect.y)
        # Moving text to center in button
        padding_x = (self.rect.width - self.text.rect.width) / 2
        padding_y = (self.rect.height - self.text.rect.height) / 2
        self.text.x += padding_x
        self.text.y += padding_y

        self.panel = pygame_gui.Panel(self.rect, start_transparency, (0, 0, 0))
        self.hover_panel = pygame_gui.Panel(self.rect, hover_transparancy, (0, 0, 0))
        self.function = None

    def set_function(self, function):
        self.function = function

    def mouse_over(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            return True
        return False

    def check_clicked(self):
        if self.mouse_over():
            if self.function is not None:
                self.function()
            return True
        return False
    
    def draw(self, display):
        if self.mouse_over():
            self.hover_panel.draw(display)
        else:
            self.panel.draw(display)
        self.text.draw(display)
