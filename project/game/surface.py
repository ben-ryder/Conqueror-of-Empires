# Ben-Ryder 2019

import pygame


class Surface:
    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.main_surface = pygame.Surface([self.rect.width, self.rect.height])

    def move(self, dx, dy):
        self.rect = self.rect.move(dx, dy)

    def get_position(self):
        return self.rect.topleft

    def draw(self, display):
        display.blit(self.main_surface, [self.rect.x, self.rect.y])
