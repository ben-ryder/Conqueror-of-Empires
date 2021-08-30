import os
import pygame
import random

import paths
import constants

import pygame_gui

import project.game.new as new
import project.data as data


class NewGame:
    """ allows the user to setup and start a new game """
    def __init__(self, display):
        self.display = display
        self.state = "new_game"
        self.game_reference = None

        # Background Setup
        self.background = pygame_gui.Image(paths.uiMenuPath + "background.png", 0, 0)
        self.back_panel = pygame_gui.Panel([100, 100, 800, 500], 150, constants.COLOURS["panel"])

        # GUI Setup
        self.origin = [150, 30]
        # General
        self.back_button = pygame_gui.Button(paths.uiPath + "backwhite.png",
                                             paths.uiPath + "backwhite-hover.png", 5, 5)

        self.title_text = pygame_gui.Text(
            "Create Game:",
            constants.FONTS["sizes"]["large"], constants.FONTS["colour"], constants.FONTS["main"],
            110, 110)

        self.play_button = pygame_gui.Button(paths.uiPath + "forwardwhite.png",
                                             paths.uiPath + "forwardwhite-hover.png",
                                             self.origin[0] + 700, self.origin[1] + 525)

        # Game Input Setup
        self.game_name_prompt = pygame_gui.Text(
            "Game Name:",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.origin[0] + 100, self.origin[1] + 150)

        self.game_name_input = pygame_gui.Entry(paths.uiMenuPath + "input-large.png",
                                                paths.uiMenuPath + "input-large-hover.png",
                                                paths.uiMenuPath + "input-large-focused.png",
                                                paths.uiMenuPath + "input-large-hover-focused.png",
                                                "", constants.FONTS["sizes"]["medium"], constants.FONTS["colour"],
                                                constants.FONTS["main"], 10, 5, True,
                                                self.origin[0] + 250, self.origin[1] + 145)

        self.game_name_error_text = pygame_gui.Text(
            "",
            constants.FONTS["sizes"]["small"], constants.COLOURS["red"], constants.FONTS["main-bold-italic"],
            self.origin[0] + 250, self.origin[1] + 180)

        # Map Input Setup
        self.map_select_prompt = pygame_gui.Text(
            "Select Map:",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.origin[0] + 100, self.origin[1] + 200)

        self.map_selector = MapSelector(self.origin[0] + 250, self.origin[1] + 200)

        # Player Input Setup
        self.players_prompt = pygame_gui.Text(
            "Players:",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.origin[0] + 100, self.origin[1] + 250)

        self.player_slots_error = pygame_gui.Text(
            "",
            constants.FONTS["sizes"]["small"], constants.COLOURS["red"], constants.FONTS["main-bold-italic"],
            self.origin[0] + 200, self.origin[1] + 255)

        self.player_manager = PlayerManager(4, [self.origin[0] + 100, self.origin[1] + 290])

        self.run()

    def run(self):
        while self.state == "new_game":
            self.handle_events()
            self.draw()

    def create_game(self):
        self.player_slots_error.change_text("")
        self.game_name_error_text.change_text("")  # reset errors, might be resolved, while new ones occur.

        if self.game_valid():
            # Making New Game
            self.game_reference = self.game_name_input.get_text()
            new.make(self.game_reference, self.map_selector.get_selection(), self.player_manager.get_player_dicts())
        else:
            self.state = "new_game"  # cancels game launch, continue with inputting game.

    def game_valid(self):
        # Game Name is empty
        if self.game_name_input.get_text() == "":
            self.game_name_error_text.change_text("Please enter a game name!")
            return False

        # Valid Game/File Name (letter, number or space. to ensure valid filename on every os)
        if not all(char.isalnum() or char.isspace() for char in self.game_name_input.get_text()):
            self.game_name_error_text.change_text("Sorry name should only be letters and numbers!")
            return False

        # Game/File name doesn't exist
        if data.check_exists(paths.gamePath + self.game_name_input.get_text()):
            self.game_name_error_text.change_text("Sorry this name is already taken!")
            return False

        # More than 1 player
        if not self.player_manager.enough_players():
            self.player_slots_error.change_text("There must be more than 1 player to play!")
            return False

        # All Player names valid (ie not blank)
        if not self.player_manager.player_names_valid():
            self.player_slots_error.change_text("Make sure everyone's got a name!")
            return False

        # All player names unique
        if not self.player_manager.player_names_unique():
            self.player_slots_error.change_text("Make sure everyone's name is different!")
            return False

        return True

    def get_state(self):
        return self.state

    def get_game(self):
        return self.game_reference

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.state = "quit"

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.back_button.check_clicked():
                    self.state = "menu"

                elif self.play_button.check_clicked():
                    self.state = "game"
                    self.create_game()

                else:
                    if not self.map_selector.check_clicked():
                        if not self.game_name_input.check_clicked():
                            self.player_manager.handle_click()

            elif event.type == pygame.KEYDOWN:
                self.game_name_input.handle_event(event)
                self.player_manager.handle_event(event)

            elif event.type == pygame.KEYUP:
                self.game_name_input.handle_event_up(event)
                self.player_manager.handle_event_up(event)

    def draw(self):
        self.background.draw(self.display)
        self.back_panel.draw(self.display)

        self.title_text.draw(self.display)
        self.back_button.draw(self.display)
        self.play_button.draw(self.display)

        self.game_name_prompt.draw(self.display)
        self.game_name_input.draw(self.display)
        self.game_name_error_text.draw(self.display)

        self.map_select_prompt.draw(self.display)
        self.map_selector.draw(self.display)

        self.players_prompt.draw(self.display)
        self.player_manager.draw(self.display)
        self.player_slots_error.draw(self.display)
        pygame.display.update()


class PlayerManager:
    """ manages the player slots seen at bottom of new_game panel"""
    def __init__(self, max_amount, origin):
        self.max_amount = max_amount
        self.origin = origin
        self.players = []

        self.colour_manager = ColourPicker()

        # pygame_gui.Button not designed to be moved once defined, inherited to SlotButton to allow for this.
        self.add_button = SlotButton(paths.uiMenuPath + "addslot.png",
                                     paths.uiMenuPath + "addslot-hover.png",
                                     self.origin[0], self.origin[1])
        self.slot_size = [200, 30]
        self.slot_padding = 40

    def enough_players(self):
        if len(self.players) > 1:
            return True
        return False

    def player_names_valid(self):
        return all(player.name_entry.get_text() != "" for player in self.players)

    def player_names_unique(self):
        names = [player.name_entry.get_text() for player in self.players]
        return not len(names) > len(set(names))

    def get_player_dicts(self):
        return [player.get_dict() for player in self.players]

    def get_slot_bottom(self):
        return self.get_slot_position(len(self.players))

    def get_slot_position(self, slot_number):
        return [self.origin[0], self.origin[1] + ((self.slot_size[1] + self.slot_padding) * slot_number)]

    def add_player(self):
        self.players.append(PlayerSlot(self, self.get_slot_bottom(), self.colour_manager.get_colour(), ""))

    def delete_player(self, player):
        self.colour_manager.add_colour(player.colour)  # so the colour can be re-used again.
        self.players.remove(player)
        self.refresh_slots()

    def refresh_slots(self):
        old_slots = self.players.copy()
        self.players = []
        for player_slot in old_slots:  # allows slots to auto move up if an above slot is deleted.
            self.players.append(PlayerSlot(self, self.get_slot_bottom(),
                                           player_slot.colour, player_slot.name_entry.text.text))

    def handle_click(self):
        added = False
        if len(self.players) < self.max_amount:  # add button overlaps last slot, so must check there is no slot first.
            if self.add_button.check_clicked():
                self.add_player()
                added = True

        if not added:
            for player in self.players:
                player.handle_click()

    def handle_event(self, event):
        for player in self.players:
            player.handle_event(event)

    def handle_event_up(self, event):
        for player in self.players:
            player.handle_event_up(event)

    def draw(self, display):
        for player in self.players:
            player.draw(display)

        if len(self.players) < self.max_amount:
            self.add_button.change_position(self.get_slot_bottom())

            self.add_button.draw(display)


class PlayerSlot:
    """ a single slot seen in the PlayerManager """
    def __init__(self, player_manager,  origin, colour, name=""):
        self.player_manager = player_manager
        self.origin = origin
        self.colour = colour

        # Background
        self.back_panel = pygame_gui.Panel([self.origin[0], self.origin[1], 500, 50], 100, constants.COLOURS["black"])

        self.name_entry = pygame_gui.Entry(paths.uiMenuPath + "input-normal.png",
                                           paths.uiMenuPath + "input-normal-hover.png",
                                           paths.uiMenuPath + "input-normal-focused.png",
                                           paths.uiMenuPath + "input-normal-hover-focused.png",
                                           name, constants.FONTS["sizes"]["medium"], constants.FONTS["colour"],
                                           constants.FONTS["main"], 10, 5, True, self.origin[0]+60, self.origin[1]+10)

        self.delete_self = pygame_gui.Button(paths.uiPath + "cross.png", paths.uiPath + "cross-hover.png",
                                             self.origin[0]+430, self.origin[1]+8)

    def get_dict(self):
        return {"name": self.name_entry.get_text(), "colour": self.colour}

    def handle_click(self):
        if self.name_entry.check_clicked():
            return True

        elif self.delete_self.check_clicked():
            self.player_manager.delete_player(self)
            return True
        return False

    def handle_event(self, event):
        self.name_entry.handle_event(event)

    def handle_event_up(self, event):
        self.name_entry.handle_event_up(event)

    def change_colour(self, colour):
        self.colour = colour

    def draw(self, display):
        self.back_panel.draw(display)
        self.name_entry.draw(display)
        pygame.draw.ellipse(display, constants.COLOURS[self.colour], [self.origin[0]+330, self.origin[1]+10, 28, 28])
        self.delete_self.draw(display)


class ColourPicker:
    """ assigns a random colour when needed, used to manage player colour generation"""
    def __init__(self):
        self.colours = ["blue", "yellow", "green", "red"]

    def get_colour(self):
        colour = random.choice(self.colours)
        self.colours.remove(colour)
        return colour

    def add_colour(self, colour):
        self.colours.append(colour)


class MapSelector:
    """ manages map choice select """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.path = paths.mapPath
        self.maps = [filename.replace(".csv", "") for filename in os.listdir(self.path)]  # all files are .csv

        self.back_button = pygame_gui.Button(paths.uiPath + "pageback.png",
                                             paths.uiPath + "pageback-hover.png",
                                             self.x, self.y)
        self.map_text = pygame_gui.Text(
            "",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.x + 40, self.y + 5)

        self.forward_button = pygame_gui.Button(paths.uiPath + "pageforward.png",
                                                paths.uiPath + "pageforward-hover.png",
                                                self.x + 230, self.y)

        self.map_number = 0  # index of self.maps, the current selection.

        self.update()

    def get_selection(self):
        return self.maps[self.map_number]

    def forward(self):
        if self.map_number < len(self.maps) - 1:
            self.map_number += 1
        else:
            self.map_number = 0
        self.update()

    def back(self):
        if self.map_number > 0:
            self.map_number -= 1
        else:
            self.map_number = len(self.maps) - 1
        self.update()

    def check_clicked(self):
        if self.forward_button.check_clicked():
            self.forward()
            return True
        elif self.back_button.check_clicked():
            self.back()
            return True
        return False

    def update(self):
        self.map_text.change_text(self.maps[self.map_number])
        # Centering new text
        padding = round((170 - self.map_text.get_rect()[2])/2)  # equal space on left and right of text
        self.map_text.x = self.x + 30 + padding

    def draw(self, display):
        self.back_button.draw(display)
        self.map_text.draw(display)
        self.forward_button.draw(display)


class SlotButton(pygame_gui.Button):
    """ Specific to PlayerManager, button must change position depending on number of slots """
    def change_position(self, position):
        self.rect.topleft = position
        self.rest_image.rect.topleft = position
        self.hover_image.rect.topleft = position
