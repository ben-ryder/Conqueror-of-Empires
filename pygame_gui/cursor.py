# Ben-Ryder 2019

import pygame


class Cursor:
    def __init__(self, imageref):
        pygame.mouse.set_visible(False)
        self.image = pygame.image.load(imageref).convert_alpha()
        
    def draw(self, surface):
        surface.blit(self.image, pygame.mouse.get_pos())
