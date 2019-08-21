# Ben-Ryder 2019

import constants
import paths

import pygame
import project.menus as menus
import project.game.controller as game


class ApplicationController:
    """ runs the whole application, changing section running based on state """
    def __init__(self):
        pygame.init()

        # Icon Setup
        icon = pygame.image.load(paths.uiMenuPath + "logo.png")
        icon.set_colorkey((0, 0, 0))
        pygame.display.set_icon(icon)  # before set_mode as suggested in pygame docs

        # Display Setup
        self.display = pygame.display.set_mode(constants.DISPLAY_SIZE)
        pygame.display.set_caption(constants.DISPLAY_NAME)

        # General Setup
        self.state = "menu"
        self.game_reference = None

    def run(self):
        while self.state != "quit":
            if self.state == "menu":
                self.run_menu()

            elif self.state == "load_game":
                self.run_loadgame()

            elif self.state == "new_game":
                self.run_newgame()

            elif self.state == "leaderboard":
                self.run_leaderboard()

            elif self.state == "game":
                self.run_game()

            else:
                raise Exception("Invalid Game State: %s" % self.state)

        self.quit()

    def run_menu(self):
        menu = menus.Menu(self.display)  # takes control while section running, control returns here after.
        self.state = menu.get_state()

    def run_loadgame(self):
        load_game = menus.LoadGame(self.display)
        self.state = load_game.get_state()
        self.game_reference = load_game.get_game()

    def run_newgame(self):
        new_game = menus.NewGame(self.display)
        self.state = new_game.get_state()
        self.game_reference = new_game.get_game()

    def run_leaderboard(self):
        leaderboard = menus.Leaderboard(self.display)
        self.state = leaderboard.get_state()

    def run_game(self):
        if self.game_reference is None:
            raise Exception("No Game Selected")

        running_game = game.Controller(self.display, self.game_reference)
        self.state = running_game.play()  # takes control, returns when game is complete.
        self.game_reference = None

    def quit(self):
        pygame.quit()
        quit()
        
