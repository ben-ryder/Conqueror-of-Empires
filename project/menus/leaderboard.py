# Ben-Ryder 2019
import pygame

import constants
import paths

import pygame_gui


class LeaderboardEditor:
    def __init__(self):
        try:
            with open(paths.dataPath + "leaderboard", "r") as file:  # file formatted as: name,score+name2,score2+...
                self.data = {}
                leaderboard_data = file.read().split("+")
                del leaderboard_data[len(leaderboard_data)-1]  # always a + at end, removes empty player added to end.
                for player_data in leaderboard_data:
                    player_data = player_data.split(",")
                    self.data[player_data[0]] = int(player_data[1])
        except FileNotFoundError:
            self.data = {}
            # data is {name: score,...}

    def add_player(self, name, score):
        if name in self.data:
            self.data[name] += 1
        else:
            self.data[name] = score

        self.save()

    def get_high_scores(self, length):  # return [[name, score], [name2, score2]...] ordered score high to low at length
        return [[name, score] for name, score in sorted(self.data.items(), key=lambda kv: kv[1], reverse=True)][:length]

    def save(self):
        with open(paths.dataPath + "leaderboard", "w") as file:
            for name, data in self.data.items():
                file.write(name + "," + str(data) + "+")  # file formatted as: name,score+name2,score2+...


class LeaderboardSlot:
    def __init__(self, name, score, rank, x, y):
        self.panel = pygame_gui.Panel([x, y, 400, 30], 100, constants.COLOURS["panel"])

        self.rank_text = pygame_gui.Text(
            str(rank),
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            x + 20, y + 5)

        self.name_text = pygame_gui.Text(
            name,
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            x + 80, y + 5)

        self.score_text = pygame_gui.Text(
            "{:,}".format(score),
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            x + 302, y + 5)

    def draw(self, display):
        self.panel.draw(display)
        self.rank_text.draw(display)
        self.name_text.draw(display)
        self.score_text.draw(display)


class Leaderboard:
    def __init__(self, display):
        self.display = display
        self.state = "leaderboard"

        # Background Setup
        self.background = pygame_gui.Image(paths.uiMenuPath + "background.png", 0, 0)
        self.back_panel = pygame_gui.Panel([100, 100, 800, 500], 150, constants.COLOURS["panel"])

        # GUI Setup
        self.back = pygame_gui.Button(paths.uiPath + "backwhite.png", paths.uiPath + "backwhite-hover.png", 5, 5)
        self.title = pygame_gui.Text(
            "Leaderboard: ",
            constants.FONTS["sizes"]["large"], constants.FONTS["colour"], constants.FONTS["main"],
            110, 110)

        self.top_ten = pygame_gui.Text(
            "(top 10)",
            constants.FONTS["sizes"]["large"], constants.FONTS["colour"], constants.FONTS["main"],
            825, 110)

        self.rank_text = pygame_gui.Text(
            "rank",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            310, 150)

        self.name_text = pygame_gui.Text(
            "name",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            380, 150)

        self.score_text = pygame_gui.Text(
            "score",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            605, 150)

        self.leaderboard_reader = LeaderboardEditor()
        self.slots = []
        x, y = [300, 170]
        padding = 40  # between player slots
        rank = 1
        for player in self.leaderboard_reader.get_high_scores(10):
            self.slots.append(LeaderboardSlot(player[0], player[1], rank, x, y))
            y += padding
            rank += 1

        self.run()

    def run(self):
        while self.state == "leaderboard":
            self.handle_events()
            self.draw()

    def get_state(self):
        return self.state

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.state = "quit"

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.back.check_clicked():
                    self.state = "menu"

    def draw(self):
        self.background.draw(self.display)
        self.back_panel.draw(self.display)

        self.title.draw(self.display)
        self.back.draw(self.display)
        self.top_ten.draw(self.display)

        self.rank_text.draw(self.display)
        self.name_text.draw(self.display)
        self.score_text.draw(self.display)

        for slot in self.slots:
            slot.draw(self.display)

        pygame.display.update()
