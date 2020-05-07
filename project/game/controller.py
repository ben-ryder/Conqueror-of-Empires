# Ben-Ryder 2019

import pygame

import project.game.model as model
import project.game.gui as gui
import project.menus.leaderboard as leaderboard
import project.data as data
import paths


class Controller:
    """ the game creator object, Holds the model and view object, and runs the game."""
    def __init__(self, display, game_reference):
        self.state = "game"
        self.display = display
        self.game_reference = game_reference

        # Game Model Setup
        save_data = data.load(paths.gamePath + self.game_reference)
        self.game_model = model.Model(save_data)

        # View + GUI Setup
        self.GUI = gui.GameGui(self, self.display, self.game_model)

    def play(self):
        self.state = self.GUI.run()  # at finish, return new state wanted, either menu, quit or ended (game finished)
        if self.state != "ended":
            self.quit()
            return self.state  # focus ends, back to main program controller to deal with new state
        else:
            # game has been won
            leaderboard_editor = leaderboard.LeaderboardEditor()
            for player in self.game_model.players:
                leaderboard_editor.add_player(player.get_name(), player.max_score)

            data.delete(paths.gamePath + self.game_reference)
            return "menu"

    def quit(self):
        self.save()

    def save(self):
        data.save(self.game_model.get_save_data(), paths.gamePath + self.game_reference)

    def get_state(self):
        return self.state
