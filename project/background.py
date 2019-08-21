# Ben-Ryder 2019

import pygame
import random


class Star:
    def __init__(self, rect, colour=(200, 200, 200)):
        self.rect = pygame.Rect(rect)
        self.colour = colour

    def draw(self, display):
        pygame.draw.rect(display, self.colour, self.rect)


class Starscape:
    def __init__(self, rect):
        self.stars = []
        amount = round(rect[2]*rect[3]*0.001)  # area * % cover of area (approx)
        for i in range(amount):
            size = random.randint(1, 2)
            x, y = random.randint(rect[0], rect[2]), random.randint(rect[1], rect[3])
            self.stars.append(Star([x, y, size, size]))

    def draw(self, display):
        for item in self.stars:
            item.draw(display)
