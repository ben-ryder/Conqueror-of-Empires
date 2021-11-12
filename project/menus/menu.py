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
        self.gui_manager = pygame_gui.UIManager(display.get_size(), "theme.json")
        self.state = "menu"
        self.game_reference = None

        # Background Setup
        self.background = legacy_gui.Image(paths.uiMenuPath + "background.png", 0, 0)

        # Making panel for title
        title_panel_size = (520, 100)
        self.title_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((constants.DISPLAY_SIZE[0] // 2 - title_panel_size[0] // 2, 150), title_panel_size),
            starting_layer_height=1,
            manager=self.gui_manager)

        # Title / Header setup
        self.title = pygame_gui.elements.UILabel(text=constants.DISPLAY_NAME,
                                                 relative_rect=pygame.Rect((0, 0), (420, 100)),
                                                 manager=self.gui_manager,
                                                 container=self.title_panel,
                                                 object_id="title")
        self.title_logo = pygame.image.load(paths.uiMenuPath + "logo-big.png")
        self.title_logo_element = pygame_gui.elements.UIImage(relative_rect=pygame.Rect((420, 5), (80, 80)),
                                                              image_surface=self.title_logo,
                                                              manager=self.gui_manager,
                                                              container=self.title_panel)

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

        self.run()

    def generate_about_window(self):
        size = (500, 250)
        about_window = pygame_gui.elements.UIWindow(
            rect=pygame.Rect((constants.DISPLAY_SIZE[0] / 2 - size[0] / 2,
                              constants.DISPLAY_SIZE[1] / 2 - size[1] / 2), size),
            manager=self.gui_manager,
            window_display_title="About")

        pygame_gui.elements.UITextBox(
            html_text=f"<b>Project Home:</b>"
                      f"<br><br><a href='https://github.com/Ben-Ryder/Conqueror-of-Empires'>https"
                      f"://github.com/Ben-Ryder/Conqueror-of-Empires</a>"
                      f"<br>(feel free to suggest improvements, "
                      f"raise issues etc)"
                      f"<br><br><b>Developed by Ben Ryder</b>"
                      f"<br><a href='https://benryder.me'>https://benryder.me</a>"
                      f"<br><br>{constants.version.decode()}",
            relative_rect=pygame.Rect((0, 0), (size[0] - 35, size[1] - 60)),
            manager=self.gui_manager,
            container=about_window)

        return about_window

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

            elif event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.newgame_button:
                        self.state = "new_game"
                    elif event.ui_element == self.continue_button:
                        self.state = "load_game"
                    elif event.ui_element == self.leaderboard_button:
                        self.state = "leaderboard"
                    elif event.ui_element == self.about_button:
                        self.generate_about_window()
                if event.user_type == pygame_gui.UI_TEXT_BOX_LINK_CLICKED:
                    webbrowser.open(event.link_target)

            self.gui_manager.process_events(event)

    def draw(self):
        self.background.draw(self.display)

        self.gui_manager.draw_ui(self.display)

        pygame.display.update()
