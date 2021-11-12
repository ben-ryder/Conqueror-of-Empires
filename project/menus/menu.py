import webbrowser
import pygame
import pygame_gui

import paths
import constants

import legacy_gui


class Menu:
    """ top section for user to pick state. new_game, leaderboard ..."""

    def __init__(self, display):
        self.display = display
        self.gui_manager = pygame_gui.UIManager(display.get_size())
        self.state = "menu"
        self.game_reference = None

        # Background Setup
        self.background = legacy_gui.Image(paths.uiMenuPath + "background.png", 0, 0)

        # Title / Header setup
        self.title = legacy_gui.Text(
            constants.DISPLAY_NAME,
            50, constants.FONTS["colour"], constants.FONTS["main"],
            250, 150)

        # Making panel around text, with padding.
        title_rect = pygame.Rect(self.title.get_rect())
        title_padding = 5
        title_rect.x -= title_padding
        title_rect.width += title_padding * 2
        self.title_panel = legacy_gui.Panel(title_rect, 150, constants.COLOURS["panel"])

        self.title_logo = pygame.image.load(paths.uiMenuPath + "logo-big.png")
        self.logo_panel = legacy_gui.Panel([title_rect.right, title_rect.y, title_rect.height, title_rect.height],
                                           150, (0, 0, 0))

        # Menu location (New, Load and Leaderboard)
        self.menux = 425
        self.menuy = 370

        # GUI Menu Setup
        self.newgame_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.menux, self.menuy), (150, 40)),
            text="new game",
            manager=self.gui_manager)

        self.continue_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.menux, self.menuy + 40), (150, 40)),
            text="continue",
            manager=self.gui_manager)

        self.leaderboard_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.menux, self.menuy + 80), (150, 40)),
            text="leaderboard",
            manager=self.gui_manager)

        self.about_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((5, self.display.get_height() - 45), (80, 40)),
            text="about",
            manager=self.gui_manager)

        self.show_about = False
        self.about = About(self)

        self.run()

    def run(self):
        clock = pygame.time.Clock()
        while self.state == "menu":
            time_delta = clock.tick(60) / 1000.0
            self.handle_events()
            self.gui_manager.update(time_delta)
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

            elif event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.newgame_button:
                        self.state = "new_game"
                    elif event.ui_element == self.continue_button:
                        self.state = "load_game"
                    elif event.ui_element == self.leaderboard_button:
                        self.state = "leaderboard"
                    elif event.ui_element == self.about_button:
                        self.show_about = True

            self.gui_manager.process_events(event)

    def draw(self):
        self.background.draw(self.display)

        self.title_panel.draw(self.display)
        self.title.draw(self.display)

        self.logo_panel.draw(self.display)
        self.display.blit(self.title_logo, self.logo_panel.rect.topleft)

        self.gui_manager.draw_ui(self.display)

        if self.show_about:
            self.about.draw(self.display)

        pygame.display.update()


class WebLink:
    """ Extension of legacy_gui.Text, when hovered over shows underline. If clicked opens href using webbrowser """

    def __init__(self, text, href, x, y):
        self.href = href

        self.text = legacy_gui.Text(
            text,
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"],
            constants.FONTS["main"],
            x, y)

        self.rect = self.text.get_rect()

        self.hover_text = legacy_gui.Text(
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

        self.background = legacy_gui.Panel([self.rect[0], self.rect[1], self.rect[2], self.rect[3]], 230, (0, 0, 0))

        self.title = legacy_gui.Text(
            "About",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 5, self.rect[1] + 5)

        self.project_title = legacy_gui.Text(
            "Project Home:",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 5, self.rect[1] + 40)

        self.project_github = WebLink("https://github.com/Ben-Ryder/Conqueror-of-Empires",
                                      "https://github.com/Ben-Ryder/Conqueror-of-Empires",
                                      self.rect[0] + 5, self.rect[1] + 60)

        self.project_message = legacy_gui.Text(
            "(feel free to suggest improvements, rasie issues etc)",
            constants.FONTS["sizes"]["small"], (200, 200, 200), constants.FONTS["main"],
            self.rect[0] + 5, self.rect[1] + 77)

        self.personal_title = legacy_gui.Text(
            "Developed by Ben Ryder",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 5, self.rect[1] + 110)

        self.personal_site = WebLink("https://benryder.me",
                                     "https://benryder.me",
                                     self.rect[0] + 5, self.rect[1] + 130)

        self.version = legacy_gui.Text(
            constants.version,
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 5, self.rect[1] + self.rect[3] - 20)

        ok_rect = [self.rect[0] + self.rect[2] - 35, self.rect[1] + self.rect[3] - 30, 35, 30]
        self.ok_button = legacy_gui.TextButton(
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
