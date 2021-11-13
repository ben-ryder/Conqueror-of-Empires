import pygame
import os

import pygame_gui

import paths
import constants

import legacy_gui

import project.data as data


class LoadGame:
    """ Lets user select or delete games from a list of files from paths.GamePath """

    def __init__(self, display):
        self.display = display
        self.gui_manager = pygame_gui.UIManager(display.get_size(), "theme.json")
        self.state = "load_game"
        self.game_reference = None

        # Background Setup
        self.background = legacy_gui.Image(paths.uiMenuPath + "background.png", 0, 0)
        self.back_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((100, 100), (800, 500)),
            starting_layer_height=1,
            manager=self.gui_manager)

        # GUI Setup
        self.back_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((5, 5), (50, 50)),
            text="",
            manager=self.gui_manager,
            object_id="back_button")

        self.title = pygame_gui.elements.UILabel(
            text="Select game: ",
            relative_rect=pygame.Rect((10, 10), (110, 30)),
            manager=self.gui_manager,
            container=self.back_panel)

        self.file_selector = FileSelector(self, (150, 80), self.gui_manager, self.back_panel)

        self.page_back_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((720, 450), (40, 40)),
            text="",
            manager=self.gui_manager,
            container=self.back_panel,
            object_id="page_back_button")

        self.page_forward_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((760, 450), (40, 40)),
            text="",
            manager=self.gui_manager,
            container=self.back_panel,
            object_id="page_forward_button")

        self.confirm_delete_window = None

        self.run()

    def generate_confirm_delete_window(self):
        confirm_box_size = (500, 200)
        return pygame_gui.windows.UIConfirmationDialog(
            rect=pygame.Rect((constants.DISPLAY_SIZE[0] / 2 - confirm_box_size[0] / 2,
                              constants.DISPLAY_SIZE[1] / 2 - confirm_box_size[1] / 2), confirm_box_size),
            manager=self.gui_manager,
            window_title=f'Delete "{self.game_reference}" game',
            action_long_desc="Are you sure?"
                             "<br><br>The game will be permanently deleted, and can't be recovered!",
            action_short_name="Confirm"
        )

    def run(self):
        clock = pygame.time.Clock()
        while self.state == "load_game":
            time_delta = clock.tick(60) / 1000.0
            self.handle_events()
            self.gui_manager.update(time_delta)
            self.draw()

    def get_state(self):
        return self.state

    def get_game(self):
        return self.game_reference

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.state = "quit"

            elif event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.back_button:
                        self.state = "menu"
                    elif event.ui_element == self.page_forward_button:
                        self.file_selector.page_forward()
                    elif event.ui_element == self.page_back_button:
                        self.file_selector.page_back()
                    elif event.ui_element in self.file_selector.game_by_button:
                        self.game_reference = self.file_selector.game_by_button[event.ui_element]
                        if "delete_button" in event.ui_object_id:
                            self.confirm_delete_window = self.generate_confirm_delete_window()
                        elif "load_button" in event.ui_object_id:
                            self.select_game()
                        else:
                            print(f"Error: Unrecognized object id '{event.ui_object_id}'")
                if event.user_type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                    if event.ui_element == self.confirm_delete_window:
                        self.delete_game()

            self.gui_manager.process_events(event)

    def delete_game(self):
        data.delete(paths.gamePath + self.game_reference)
        self.file_selector.refresh_list()

    def select_game(self):
        self.state = "game"  # effectively quits load game

    def draw(self):
        self.background.draw(self.display)

        self.gui_manager.draw_ui(self.display)

        pygame.display.update()


def remove_file_extension(filename):
    return filename.split(".")[0]


def get_game_files():
    valid_game_files = []
    folder_items = [file for file in os.listdir(paths.gamePath)]

    for folder_item in folder_items:
        if os.path.isfile(os.path.join(paths.gamePath, folder_item)) and folder_item.lower().endswith(".json"):
            valid_game_files.append(folder_item)

    return valid_game_files


class FileSelector:
    """ Responsible for the list of files seen on screen """

    def __init__(self, control, origin, gui_manager, back_panel):
        self.control = control  # control being LoadGame Object
        self.origin = origin
        self.gui_manager = gui_manager
        self.back_panel = back_panel
        self.max_amount = 6  # split into lists of amount (pages of so many games)

        # Create game save directory if it doesn't exist.
        os.makedirs(paths.gamePath, exist_ok=True)

        # Load Game Names From Directory
        self.games = sorted([remove_file_extension(file) for file in get_game_files()])
        try:
            self.games.remove(
                ".gitignore")  # .gitignore present to stop data being pushed/pulled but still in directory.
        except ValueError:
            pass
        self.split_games = [self.games[i:i + self.max_amount] for i in range(0, len(self.games), self.max_amount)]
        # ^ splits games list into equal sub-lists of self.max_amount.

        # GUI Setup
        self.current_page_index = 0
        self.game_pages = []
        self.game_by_button = {}
        padding = 70  # space between file slots
        for page in self.split_games:
            panels = []
            self.game_pages.append(panels)
            counter = 0
            for game_name in page:
                game_line = pygame_gui.elements.UIPanel(
                    relative_rect=pygame.Rect((self.origin[0], self.origin[1] + padding * counter), (500, 50)),
                    starting_layer_height=1,
                    manager=self.gui_manager,
                    container=back_panel)

                load_button = pygame_gui.elements.UIButton(
                    text=game_name,
                    relative_rect=pygame.Rect((0, 0), (500, 45)),
                    manager=self.gui_manager,
                    container=game_line,
                    object_id="load_button"
                )

                delete_button = pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect((-50, 0), (40, 40)),
                    text="",
                    manager=self.gui_manager,
                    container=game_line,
                    object_id="delete_button",
                    starting_height=2,
                    anchors={'left': 'right',
                             'right': 'right',
                             'top': 'top',
                             'bottom': 'bottom'}
                )

                panels.append(game_line)
                self.game_by_button[delete_button] = game_name
                self.game_by_button[load_button] = game_name
                counter += 1
        self.update_active_game_lines()

    def get_current_page(self):
        return self.game_pages[self.current_page_index]

    def refresh_list(self):
        for page in self.game_pages:
            for panel in page:
                panel.kill()

        self.__init__(self.control, self.origin, self.gui_manager, self.back_panel)

    def page_forward(self):
        if self.current_page_index < len(self.game_pages) - 1:
            self.current_page_index += 1
        else:
            self.current_page_index = 0
        self.update_active_game_lines()

    def page_back(self):
        if self.current_page_index > 0:
            self.current_page_index -= 1
        else:
            self.current_page_index = len(self.game_pages) - 1
        self.update_active_game_lines()

    def update_active_game_lines(self):
        for page in self.game_pages:
            for panel in page:
                panel.hide()

        for panel in self.get_current_page():
            panel.show()
