# Ben-Ryder 2019

import pygame
import pygame_gui.text
import pygame_gui.image


class Entry:
    def __init__(self, rest_image, hover_image,
                 rest_focused_image, hover_focused_image,
                 initial_text, text_size, text_colour, text_font, text_padx, text_pady,
                 sticky, x, y):

        self.rest_image = pygame_gui.Image(rest_image, x, y)
        self.hover_image = pygame_gui.Image(hover_image, x, y)
        self.rest_focused_image = pygame_gui.Image(rest_focused_image, x, y)
        self.hover_focused_image = pygame_gui.Image(hover_focused_image, x, y)

        self.rect = self.rest_image.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.text_padx = text_padx
        self.text_pady = text_pady
        self.active = False
        self.sticky = sticky  # sticky if text should remain when entry re-clicked on.
        self.text = pygame_gui.Text(initial_text, text_size, text_colour, text_font,
                                    self.rect.x+self.text_padx, self.rect.y+self.text_pady)
        self.backspace = False  # allows for continuous backspace. (as long as handle_event_up() is also called)
        self.backspace_delay = 7  # READ ME!! - works as delayed by x frames, for higher frame rates increase delay.
        self.backspace_counter = 0

    def get_text(self):
        return self.text.text

    def mouse_over(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            return True
        return False

    def check_clicked(self):
        if self.mouse_over():
            self.active = True
            if not self.sticky:
                self.text.change_text("")
        else:
            self.active = False
            self.backspace = False

    def handle_event(self, event):
        if self.active:
            key_uni = event.unicode
            key_str = pygame.key.name(event.key)

            if key_str == "backspace":
                self.backspace = True  # deletes characters in draw()
            elif key_str == "space" and self.text.graphic_text.get_width() < self.rect[2] - self.text_padx*3:
                self.text.change_text(self.text.text + " ")
            else:
                if self.text.graphic_text.get_width() < self.rect[2]-self.text_padx*3 and key_uni.isprintable():
                    if pygame.key.get_mods() & pygame.KMOD_CAPS or pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        self.text.change_text(self.text.text+key_uni.upper())
                    else:
                        self.text.change_text(self.text.text+key_uni.lower())

    def handle_event_up(self, event):
        if self.active:
            key_str = pygame.key.name(event.key)

            if key_str == "backspace":
                self.backspace = False

    def draw(self, display):
        # Delete character if suppose to. (done here as definitely called every game loop)
        if self.backspace:
            if self.backspace_counter >= self.backspace_delay:
                self.text.change_text(self.text.text[:-1])
                self.backspace_counter = 0
            else:
                self.backspace_counter += 1

        # Drawing
        if self.mouse_over() and self.active:
            self.hover_focused_image.draw(display)
        elif self.active:
            self.rest_focused_image.draw(display)
        elif self.mouse_over():
            self.hover_image.draw(display)
        else:
            self.rest_image.draw(display)
        self.text.draw(display)
