# Ben-Ryder 2019

import pygame


class Camera:
    """ scrolls scroll_surface "underneath" a view_surface, by moving mouse to corners of the view_surface """
    def __init__(self, view_surface, scroll_surface, scroll_margin, scroll_speed):
        """ scroll_surface is not pygame.Surface, but a custom Surface class inheriting """
        self.view_surface = view_surface
        self.scroll_surface = scroll_surface
        self.scroll_speed = scroll_speed

        self.scroll_margin = scroll_margin  # px round edge of view_surface
        width = self.view_surface.get_width()
        height = self.view_surface.get_height()

        self.top_margin = pygame.Rect(0, 0, width, self.scroll_margin)
        self.right_margin = pygame.Rect(width-self.scroll_margin, 0, self.scroll_margin, height)
        self.bottom_margin = pygame.Rect(0, height-self.scroll_margin, width, self.scroll_margin)
        self.left_margin = pygame.Rect(0, 0, self.scroll_margin, height)

    def set_position(self, position):
        self.scroll_surface.rect.topleft = position

    def get_position(self):
        return self.scroll_surface.rect.topleft

    def scroll_left(self):
        self.scroll_surface.move(-self.scroll_speed, 0)

    def scroll_right(self):
        self.scroll_surface.move(self.scroll_speed, 0)

    def scroll_up(self):
        self.scroll_surface.move(0, -self.scroll_speed)

    def scroll_down(self):
        self.scroll_surface.move(0, self.scroll_speed)

    def handle_scroll(self, mouseX, mouseY, excluded_areas):
        # exluded_areas is list of rects, in which triggering scrolling should't occur
        if not self.in_excluded(mouseX, mouseY, excluded_areas):
            if self.top_margin.collidepoint(mouseX, mouseY) and not self.at_surface_top():
                self.scroll_down()

            if self.bottom_margin.collidepoint(mouseX, mouseY) and not self.at_surface_bottom():
                self.scroll_up()

            if self.left_margin.collidepoint(mouseX, mouseY) and not self.at_surface_left():
                self.scroll_right()

            if self.right_margin.collidepoint(mouseX, mouseY) and not self.at_surface_right():
                self.scroll_left()
                
    def at_surface_top(self):
        if self.scroll_surface.rect.y >= 0:
            return True
        return False

    def at_surface_bottom(self):
        if self.scroll_surface.rect.bottom <= self.view_surface.get_height():
            return True
        return False

    def at_surface_left(self):
        if self.scroll_surface.rect.left >= 0:
            return True
        return False

    def at_surface_right(self):
        if self.scroll_surface.rect.right <= self.view_surface.get_width():
            return True
        return False

    def in_excluded(self, mouseX, mouseY, excluded_areas):
        for rect in excluded_areas:
            if rect.collidepoint(mouseX, mouseY):
                return True
        return False
