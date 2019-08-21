# Ben-Ryder 2019

import webbrowser
import pygame

import paths
import constants

import pygame_gui


class Menu:
    """ top section for user to pick state. new_game, leaderboard ..."""
    def __init__(self, display):
        self.display = display
        self.state = "menu"
        self.game_reference = None

        # Background Setup
        self.background = pygame_gui.Image(paths.uiMenuPath + "background.png", 0, 0)

        # Title / Header setup
        self.title = pygame_gui.Text(
            constants.DISPLAY_NAME,
            50, constants.FONTS["colour"], constants.FONTS["main"],
            250, 150)

        # Making panel around text, with padding.
        title_rect = pygame.Rect(self.title.get_rect())
        title_padding = 5
        title_rect.x -= title_padding
        title_rect.width += title_padding*2
        self.title_panel = pygame_gui.Panel(title_rect, 150, constants.COLOURS["panel"])

        self.title_logo = pygame.image.load(paths.uiMenuPath + "logo-big.png")
        self.logo_panel = pygame_gui.Panel([title_rect.right, title_rect.y, title_rect.height, title_rect.height],
                                           150, (0, 0, 0))

        # Menu location (New, Load and Leaderboard)
        self.menux = 425
        self.menuy = 370

        # GUI Menu Setup
        self.newgame_button = pygame_gui.TextButton(
            [self.menux, self.menuy, 150, 40],
            220, 200,
            "new game",
            constants.FONTS["sizes"]["large"], constants.FONTS["colour"], constants.FONTS["main"])

        self.continue_button = pygame_gui.TextButton(
            [self.menux, self.menuy + 40, 150, 40],
            220, 200,
            "continue",
            constants.FONTS["sizes"]["large"], constants.FONTS["colour"], constants.FONTS["main"])

        self.leaderboard_button = pygame_gui.TextButton(
            [self.menux, self.menuy + 80, 150, 40],
            220, 200,
            "leaderboard",
            constants.FONTS["sizes"]["large"], constants.FONTS["colour"], constants.FONTS["main"])

        self.about_button = pygame_gui.TextButton(
            [5, self.display.get_height() - 45, 80, 40],
            220, 200,
            "about",
            constants.FONTS["sizes"]["large"], constants.FONTS["colour"], constants.FONTS["main"])

        self.show_about = False
        self.about = About(self)

        self.run()

    def run(self):
        while self.state == "menu":
            self.handle_events()
            self.draw()

    def get_state(self):
        return self.state

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.state = "quit"

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.show_about:  # chanel inputs to about message only.
                    self.about.handle_click()

                elif self.newgame_button.check_clicked():
                    self.state = "new_game"
                elif self.continue_button.check_clicked():
                    self.state = "load_game"
                elif self.leaderboard_button.check_clicked():
                    self.state = "leaderboard"

                elif self.about_button.check_clicked():
                    self.show_about = True

    def draw(self):
        self.background.draw(self.display)

        self.title_panel.draw(self.display)
        self.title.draw(self.display)

        self.logo_panel.draw(self.display)
        self.display.blit(self.title_logo, self.logo_panel.rect.topleft)

        self.newgame_button.draw(self.display)
        self.continue_button.draw(self.display)
        self.leaderboard_button.draw(self.display)

        self.about_button.draw(self.display)

        if self.show_about:
            self.about.draw(self.display)

        pygame.display.update()


class WebLink:
    """ Extension of pygame_gui.Text, when hovered over shows underline. If clicked opens href using webbrowser """
    def __init__(self, text, href, x, y):
        self.href = href

        self.text = pygame_gui.Text(
            text,
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"],
            constants.FONTS["main"],
            x, y)

        self.rect = self.text.get_rect()

        self.hover_text = pygame_gui.Text(
            text,
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            x, y)
        self.hover_text.graphic_font.set_underline(True)
        self.hover_text.change_text(self.hover_text.text)  # acts as update, font must be re-rendered to show underline.

    def mouse_over(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def check_clicked(self):
        if self.mouse_over():
            webbrowser.open(self.href)
            return True
        return False

    def draw(self, display):
        if self.mouse_over():
            self.hover_text.draw(display)
        else:
            self.text.draw(display)


# TODO: extract MenuAbout + WebLink to separate modules? error in importing currently.
class About:
    """ GUI popup with ok. Gives version number, author info and external links etc """
    def __init__(self, GUI):
        self.GUI = GUI

        size = [350, 200]
        self.rect = [constants.DISPLAY_SIZE[0] / 2 - size[0] / 2,  # center of screen
                     constants.DISPLAY_SIZE[1] / 2 - size[1] / 2,
                     size[0],
                     size[1]]

        self.background = pygame_gui.Panel([self.rect[0], self.rect[1], self.rect[2], self.rect[3]], 230, (0, 0, 0))

        self.title = pygame_gui.Text(
            "About",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 5, self.rect[1] + 5)

        self.project_title = pygame_gui.Text(
            "Project Home:",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 5, self.rect[1] + 40)

        self.project_github = WebLink("https://github.com/Ben-Ryder/Conqueror-of-Empires",
                                      "https://github.com/Ben-Ryder/Conqueror-of-Empires",
                                      self.rect[0] + 5, self.rect[1] + 60)

        self.project_message = pygame_gui.Text(
            "(feel free to suggest improvements, rasie issues etc)",
            constants.FONTS["sizes"]["small"], (200, 200, 200), constants.FONTS["main"],
            self.rect[0] + 5, self.rect[1] + 77)

        self.personal_title = pygame_gui.Text(
            "Developed by Ben Ryder",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 5, self.rect[1] + 110)

        self.personal_site = WebLink("https://benryder.me",
                                     "https://benryder.me",
                                     self.rect[0] + 5, self.rect[1] + 130)

        self.version = pygame_gui.Text(
            constants.version,
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 5, self.rect[1] + self.rect[3] - 20)

        ok_rect = [self.rect[0] + self.rect[2] - 35, self.rect[1] + self.rect[3] - 30, 35, 30]
        self.ok_button = pygame_gui.TextButton(
            ok_rect,
            0, 100,
            "ok",
            constants.FONTS["sizes"]["large"], constants.FONTS["colour"], constants.FONTS["main"])

    def handle_click(self):
        if self.ok_button.check_clicked():
            self.GUI.show_about = False
        else:
            self.personal_site.check_clicked()
            self.project_github.check_clicked()

    def draw(self, display):
        self.background.draw(display)
        self.title.draw(display)

        self.personal_title.draw(display)
        self.personal_site.draw(display)

        self.project_title.draw(display)
        self.project_github.draw(display)
        self.project_message.draw(display)

        self.version.draw(display)
        self.ok_button.draw(display)
