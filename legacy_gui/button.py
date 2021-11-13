import pygame
import legacy_gui.image


class Button:
    def __init__(self, rest_image, hover_image, x, y):
        self.rest_image = legacy_gui.Image(rest_image, x, y)
        self.hover_image = legacy_gui.Image(hover_image, x, y)
        self.rect = self.rest_image.image.get_rect()
        self.rect.x = x
        self.rect.y = y
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
            self.hover_image.draw(display)
        else:
            self.rest_image.draw(display)
