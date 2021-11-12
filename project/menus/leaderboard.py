import pygame
import pygame_gui

import constants
import paths

import legacy_gui


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
        self.panel = legacy_gui.Panel([x, y, 400, 30], 100, constants.COLOURS["panel"])

        self.rank_text = legacy_gui.Text(
            str(rank),
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            x + 20, y + 5)

        self.name_text = legacy_gui.Text(
            name,
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            x + 80, y + 5)

        self.score_text = legacy_gui.Text(
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
        self.gui_manager = pygame_gui.UIManager(display.get_size(), "theme.json")
        self.state = "leaderboard"

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
            object_id="return_button")

        self.title = pygame_gui.elements.UILabel(
            text="Leaderboard: ",
            relative_rect=pygame.Rect((10, 10), (110, 30)),
            manager=self.gui_manager,
            container=self.back_panel)

        self.top_ten = pygame_gui.elements.UILabel(
            text="(top 10)",
            relative_rect=pygame.Rect((-100, 10), (100, 30)),
            manager=self.gui_manager,
            container=self.back_panel,
            anchors={'left': 'right',
                   'right': 'right',
                   'top': 'top',
                   'bottom': 'bottom'})

        self.rank_text = pygame_gui.elements.UILabel(
            text="rank",
            relative_rect=pygame.Rect((190, 40), (60, 30)),
            manager=self.gui_manager,
            container=self.back_panel)

        self.name_text = pygame_gui.elements.UILabel(
            text="name",
            relative_rect=pygame.Rect((260, 40), (100, 30)),
            manager=self.gui_manager,
            container=self.back_panel)

        self.score_text = pygame_gui.elements.UILabel(
            text="score",
            relative_rect=pygame.Rect((460, 40), (100, 30)),
            manager=self.gui_manager,
            container=self.back_panel)

        self.leaderboard_reader = LeaderboardEditor()
        x, y = [190, 80]
        padding = 40  # between player slots
        rank = 1
        for player in self.leaderboard_reader.get_high_scores(10):
            panel_line = pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect((x, y), (500, 35)),
                starting_layer_height=1,
                manager=self.gui_manager,
                container=self.back_panel)

            pygame_gui.elements.UILabel(
                text=str(rank),
                relative_rect=pygame.Rect((0, 0), (60, 30)),
                manager=self.gui_manager,
                container=panel_line
            )

            pygame_gui.elements.UILabel(
                text=player[0],
                relative_rect=pygame.Rect((70, 0), (100, 30)),
                manager=self.gui_manager,
                container=panel_line
            )

            pygame_gui.elements.UILabel(
                text=f"{player[1]:,}",
                relative_rect=pygame.Rect((270, 0), (100, 30)),
                manager=self.gui_manager,
                container=panel_line
            )

            y += padding
            rank += 1

        self.run()

    def run(self):
        clock = pygame.time.Clock()
        while self.state == "leaderboard":
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
                    if event.ui_element == self.back_button:
                        self.state = "menu"

            self.gui_manager.process_events(event)

    def draw(self):
        self.background.draw(self.display)

        self.gui_manager.draw_ui(self.display)

        pygame.display.update()
