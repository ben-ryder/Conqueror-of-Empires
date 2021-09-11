import pygame
import time

import paths
import constants

import pygame_gui
import project.game.scroll as scroll
import project.game.view as view


class GameGui:
    """ interface between user and model. handles GUI elements, self.game-view handles map-level interactions."""
    def __init__(self, control, display, model):
        self.control_link = control
        self.display = display
        self.model_link = model
        self.state = "game"

        # Game View Setup
        self.game_view = view.PhysicalGame(self.display, self.model_link, self)
        self.camera = scroll.Camera(self.display, self.game_view.game_surface, 25, 6)
        self.mini_map = MiniMap(self.model_link)

        # GUI Setup
        # Fixed GUI
        # Player Tracking GUI's
        self.player_tracker = PlayerTracker(self.model_link)
        self.player_tracker.update_player()  # current player at startup
        self.update_camera_focus()  # to match start players last position before last save

        self.menu_button = pygame_gui.Button(paths.uiGamePath + "menu.png",
                                             paths.uiGamePath + "menu-hover.png",
                                             self.display.get_width() - 50,
                                             self.display.get_rect()[0] + 5)

        self.leaderboard_button = pygame_gui.Button(paths.uiGamePath + "leaderboard.png",
                                                    paths.uiGamePath + "leaderboard-hover.png",
                                                    self.display.get_width() - 100,
                                                    self.display.get_rect()[0] + 5)

        self.next_turn_button = pygame_gui.Button(paths.uiPath + "forwardwhite.png",
                                                  paths.uiPath + "forwardwhite-hover.png",
                                                  self.display.get_width() - 47,
                                                  self.display.get_height() - 43)

        self.fixed_rects = [self.menu_button.rect, self.leaderboard_button.rect, self.next_turn_button.rect]
        # scrolling will not be triggered if the mouse is in these rects, even if in the scroll space at screen edge.

        # Changeable GUI's
        # Persistent - GUI's that should stay on screen, and have focus until the user closes them.
        self.persistent_guis = []  # simulates a stack, events channeled to top GUI only.

        # Passive - GUI's that should be deleted when the user clicks off them, and has focus until being clicked off
        self.passive_guis = []  # acts as normal list

        # Welcome Message
        if self.model_link.get_current_player().get_turn() == 0:
            self.launch_welcome_message()

    def run(self):
        while self.state == "game":

            if self.model_link.game_ended():
                # game ended at deletion of game over message (called in GameOverMessage on its "ok")
                if GameOverMessage not in [type(obj) for obj in self.persistent_guis]:  # stops recalling when active
                    self.game_over_message()

            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Camera Scroll
            if not self.persistent_guis and not self.passive_guis and pygame.mouse.get_focused():
                self.camera.handle_scroll(mouse_x, mouse_y, self.get_rects())

            # Main Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if QuitMessage not in [type(obj) for obj in self.persistent_guis]:  # stops recalling when active
                        self.quit_message()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or (event.key == pygame.K_F4 and event.mod == pygame.KMOD_ALT):
                        self.state = "quit"
                    elif event.key == pygame.K_m:
                        self.state = "menu"

                    elif event.key == pygame.K_s:  # Screenshot (saves view_surface and game_surface)
                        pygame.image.save(self.game_view.game_surface.main_surface,
                                          self.model_link.game_name + str(time.time()) + ".png")

                        pygame.image.save(self.display,
                                          self.model_link.game_name + str(time.time()) + "display" + ".png")

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(mouse_x, mouse_y)

            # Drawing
            self.draw()
            pygame.display.update()

        # Here has been game quit, returns to controller call, where save and new state are processed.
        return self.state

    def handle_click(self, mouse_x, mouse_y):
        if not self.handled_persistent_gui(mouse_x, mouse_y):
            if not self.handled_passive_gui(mouse_x, mouse_y):
                if not self.handled_fixed_gui(mouse_x, mouse_y):
                    if self.game_view.map_clicked(mouse_x, mouse_y):  # update tile focus, reset active_unit if off map
                        if self.game_view.active_unit is not None:
                            self.game_view.handle_unit_actions()  # if action, reset active_unit
                        elif not self.game_view.handled_unit_click():
                            self.game_view.handled_settlement_click()

    def handled_persistent_gui(self, mouse_x, mouse_y):
        if self.persistent_guis:
            self.persistent_guis[len(self.persistent_guis) - 1].handle_click()  # top GUI on screen (top of stack)
            return True
        return False  # if persistent GUI exists

    def handled_passive_gui(self, mouse_x, mouse_y):
        to_delete = []
        handled = False  # to allow for all to be processed, not instant return
        for item in self.passive_guis:
            if item.check_clicked(mouse_x, mouse_y):
                handled = True
            elif item.allow_delete():
                to_delete.append(item)

        # Deleting unselected GUI's
        for item in to_delete:
            self.passive_guis.remove(item)

        return handled

    def delete_persistent(self):
        self.persistent_guis.pop()  # active GUI will always calls this, and will always be top of stack.

    def delete_passive(self, item):
        self.passive_guis.remove(item)
        # Legacy exception handling? seems to be pointless now
        # try:
        #    self.passive_guis.remove(item)
        #     return True
        # except ValueError:
        #     return False

    def handled_fixed_gui(self, mouse_x, mouse_y):
        if self.menu_button.check_clicked():
            self.game_menu()
        elif self.leaderboard_button.check_clicked():
            self.launch_leaderboard()
        elif self.next_turn_button.check_clicked():
            self.next_turn_message()  # next_turn action triggered at closing of GUI message, in the GUI.
        else:
            self.mini_map.handle_click()

    def launch_settlement_menu(self, tile_reference, position):
        self.passive_guis.append(CityMenu(self.model_link, self, tile_reference, position))

    def launch_upgrade_menu(self, city, position):
        self.passive_guis.append(UpgradeMenu(city, self, position))

    def launch_leaderboard(self):
        self.persistent_guis.append(GameLeaderboard(self, self.model_link))

    def launch_help(self):
        self.persistent_guis.append(Help(self))

    def launch_welcome_message(self):
        self.persistent_guis.append(WelcomeMessage(self))

    def next_turn_message(self):
        next_player = self.model_link.get_player(self.model_link.get_next_player())
        self.persistent_guis.append(NextTurnMessage(self, "Next Turn",
                                                    ["Get ready %s!" % next_player.get_name(),
                                                     "It's your turn up next."]))

    def game_over_message(self):
        self.persistent_guis.clear()  # To remove conquer message caused by taking last settlement
        self.persistent_guis.insert(0, GameOverMessage(self,
                                                       "Game Over!", ["Well Done %s" % self.model_link.get_winner(),
                                                                      "You conquered all the other players",
                                                                      "and won the game!"]))

    def quit_message(self):
        self.save()
        self.persistent_guis.append(QuitMessage(self, "Are you sure you want to quit?",
                                                ["Your game will still be saved."]))

    def game_menu(self):
        self.save()  # in-case quit to menu called
        self.persistent_guis.append(GameMenu(self, self.model_link))

    def next_turn(self):
        self.save()
        self.model_link.next_turn()
        self.player_tracker.update_player()
        self.update_camera_focus()
        self.save()

    def save(self):
        self.model_link.get_current_player().set_camera_focus(self.camera.get_position())
        self.control_link.save()

    def update_camera_focus(self):
        if self.model_link.get_current_player().get_camera_focus() != [None, None]:  # not set until end of first turn.
            # TODO: set initial camera_focus on settlement assignment, so this isn't needed.
            self.camera.set_position(self.model_link.get_current_player().get_camera_focus())

    def end_game(self):  # natural end, with a winner not quit.
        self.state = "ended"

    def send_message(self, msg_type, text):
        self.persistent_guis.append(Message(self, msg_type, text))

    def get_rects(self):
        return self.fixed_rects

    def draw(self):
        # Map Draw
        self.game_view.draw(self.display)

        # GUI Drawing
        # Fixed GUIs
        # Player Tracker
        self.player_tracker.draw(self.display)
        self.menu_button.draw(self.display)
        self.leaderboard_button.draw(self.display)
        self.next_turn_button.draw(self.display)

        self.mini_map.draw(self.display)

        # Passive GUIs
        for item in self.passive_guis:
            item.draw(self.display)

        # Persistent GUIs
        if self.persistent_guis:
            for item in self.persistent_guis:
                item.draw(self.display)


####################################################################################################################


class CityMenu:
    """ menu called when city clicked on. Gives key info and allows for upgrade and spawn options """
    def __init__(self, model, GUI, city_reference, position):
        self.model_link = model
        self.city_link = self.model_link.world.get_tile(city_reference)
        self.GUI = GUI
        self.stuck = False  # should keep on click off

        self.size = [120, 175]
        spawn_menu_size = [200, 60]

        # Adjusting and Setting x position
        if position[0] + spawn_menu_size[0] > constants.DISPLAY_SIZE[0]:
            self.x = constants.DISPLAY_SIZE[0] - spawn_menu_size[0]
        else:
            self.x = position[0]

        # Adjusting and setting y position
        if position[1] + self.size[1] + spawn_menu_size[1] > constants.DISPLAY_SIZE[1]:
            self.y = constants.DISPLAY_SIZE[1] - self.size[1] - spawn_menu_size[1]
        else:
            self.y = position[1]
        # adjusting keeps GUI's on screen at all times. position is top-left so only have to deal with right and bottom
        # clips as cant click off screen. ADJUSTING MENU ALSO STOPS spawn and upgrade menu overlapping, as max width
        # includes the spawn_menu width, and upgrade menu is within this max rect size.

        self.background_panel = pygame_gui.Panel([self.x, self.y, self.size[0], self.size[1]],
                                                 200,
                                                 constants.COLOURS["panel"])

        # GUI Setup
        self.city_name_text = pygame_gui.Text(
            self.city_link.get_name(),
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.x + 40, self.y + 3)

        self.level_text = pygame_gui.Text(
            "Level " + str(self.city_link.get_level()),
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.x + 40, self.y + 30)

        self.score_icon = pygame_gui.Image(paths.uiGamePath + "score-icon.png", self.x + 5, self.y + 60)
        self.score_text = pygame_gui.Text(
            "{:,}".format(self.city_link.get_score()),
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.x + 40, self.y + 60)

        self.ap_icon = pygame_gui.Image(paths.uiGamePath + "ap-icon.png", self.x + 5, self.y + 90)
        self.ap_text = pygame_gui.Text(
            "+" + str(self.city_link.get_ap_value()) + " per turn",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.x + 40, self.y + 90)

        # Interaction
        self.upgrade_button = pygame_gui.TextButton(
            [self.x, self.y + self.size[1] - 60, 120, 30],
            0, 100,
            "upgrade",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"])

        self.spawn_button = pygame_gui.TextButton(
            [self.x, self.y + self.size[1] - 30, 120, 30],
            0, 100,
            "spawn unit",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"])

        self.show_spawn = False
        self.spawn_menu = SpawnMenu(self.model_link, self.GUI, self.city_link,
                                    self.x, self.y + self.size[1], spawn_menu_size)

    def allow_delete(self):
        return not self.stuck

    def check_clicked(self, mouse_x, mouse_y):
        clicked = False  # to allow for combined click in main settlement menu, or spawn.

        if self.show_spawn:  # first, as otherwise will close regardless, even if spawn button pressed
            if self.spawn_menu.spawn_made(mouse_x, mouse_y):  # like handle_click. but bool is if unit spawned instead
                self.GUI.delete_passive(self)
                clicked = True
            else:
                self.show_spawn = False

        if self.background_panel.rect.collidepoint(mouse_x, mouse_y):
            clicked = True

            if self.spawn_button.check_clicked():
                self.show_spawn = True

            elif self.upgrade_button.check_clicked():
                self.GUI.delete_passive(self)
                self.GUI.launch_upgrade_menu(self.city_link, [self.x, self.y])

        return clicked

    def draw(self, display):
        self.background_panel.draw(display)

        pygame.draw.ellipse(display, constants.COLOURS[self.model_link.get_current_player().get_colour()],
                            [self.x + 10, self.y + 5, 15, 15])
        self.city_name_text.draw(display)

        self.level_text.draw(display)

        self.ap_icon.draw(display)
        self.ap_text.draw(display)
        self.score_icon.draw(display)
        self.score_text.draw(display)

        self.upgrade_button.draw(display)
        self.spawn_button.draw(display)

        if self.show_spawn:
            self.spawn_menu.draw(display)


class SpawnButton:
    """ the individual unit button for the SpawnMenu"""
    def __init__(self, unit_type, cost, x, y):
        if unit_type == "scout":
            self.button = pygame_gui.Button(paths.uiGamePath + "scouticon.png",
                                                  paths.uiGamePath + "scouticon-hover.png", x, y)
        elif unit_type == "swordsman":
            self.button = pygame_gui.Button(paths.uiGamePath + "swordsmanicon.png",
                                                  paths.uiGamePath + "swordsmanicon-hover.png", x, y)
        elif unit_type == "archer":
            self.button = pygame_gui.Button(paths.uiGamePath + "archericon.png",
                                                   paths.uiGamePath + "archericon-hover.png", x, y)
        elif unit_type == "horseman":
            self.button = pygame_gui.Button(paths.uiGamePath + "horsemanicon.png",
                                                     paths.uiGamePath + "horsemanicon-hover.png", x, y)
        elif unit_type == "catapult":
            self.button = pygame_gui.Button(paths.uiGamePath + "catapulticon.png",
                                                     paths.uiGamePath + "catapulticon-hover.png", x, y)

        self.button_overlay = pygame_gui.Panel(self.button.rect, 50, constants.COLOURS["panel"])

        self.cost_panel = pygame_gui.Panel([x, self.button.rect.bottom, self.button.rect.width, 20],
                                           0,
                                           constants.COLOURS["panel"])
        self.cost_panel_hover = pygame_gui.Panel([x, self.button.rect.bottom, self.button.rect.width, 20],
                                                 50,
                                                 constants.COLOURS["panel"])

        self.cost_text = pygame_gui.Text(
            "- " + str(cost),
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            x + 10, self.button.rect.bottom)

    def check_clicked(self):
        return self.button.check_clicked() or self.cost_panel.rect.collidepoint(pygame.mouse.get_pos())

    def draw(self, display):
        if self.button.mouse_over() or self.cost_panel_hover.rect.collidepoint(pygame.mouse.get_pos()):
            self.cost_panel_hover.draw(display)
        else:
            self.cost_panel.draw(display)

        if self.cost_panel_hover.rect.collidepoint(pygame.mouse.get_pos()):
            self.button_overlay.draw(display)

        self.button.draw(display)
        self.cost_text.draw(display)


class SpawnMenu:
    """ managed by the CityMenu, allows for the spawning of units to the city."""
    def __init__(self, model, GUI, city_link, x, y, size):
        self.model_link = model
        self.GUI = GUI
        self.city_reference = city_link.get_position()
        self.x = x
        self.y = y

        self.size = size
        self.background = pygame_gui.Panel([self.x, self.y, self.size[0], self.size[1]], 200,
                                           constants.COLOURS["panel"])

        # units
        self.scout_button = SpawnButton("scout",
                                        constants.UNIT_SPECS["scout"]["spawn_cost"],
                                        self.x, self.y)
        self.swordsman_button = SpawnButton("swordsman",
                                            constants.UNIT_SPECS["swordsman"]["spawn_cost"],
                                            self.x + 40, self.y)
        self.archer_button = SpawnButton("archer",
                                         constants.UNIT_SPECS["archer"]["spawn_cost"],
                                         self.x + 80, self.y)
        self.horseman_button = SpawnButton("horseman",
                                           constants.UNIT_SPECS["horseman"]["spawn_cost"],
                                           self.x + 120, self.y)
        self.catapult_button = SpawnButton("catapult",
                                           constants.UNIT_SPECS["catapult"]["spawn_cost"],
                                           self.x + 160, self.y)

    def spawn_made(self, mouse_x, mouse_y):
        if self.background.rect.collidepoint(mouse_x, mouse_y):
            spawned = None
            if self.scout_button.check_clicked():
                spawned = self.model_link.try_spawn("scout", self.city_reference)
            elif self.swordsman_button.check_clicked():
                spawned = self.model_link.try_spawn("swordsman", self.city_reference)
            elif self.archer_button.check_clicked():
                spawned = self.model_link.try_spawn("archer", self.city_reference)
            elif self.horseman_button.check_clicked():
                spawned = self.model_link.try_spawn("horseman", self.city_reference)
            elif self.catapult_button.check_clicked():
                spawned = self.model_link.try_spawn("catapult", self.city_reference)

            if not spawned:
                self.GUI.send_message("Not Enough!", ["Sorry you don't have enough ap left", "to spawn this unit here."])
            else:
                self.GUI.player_tracker.update_player()  # ap and score will have changed
                return True

        return False  # acts different! will even close on direct click, bool is for if unit spawned.

    def draw(self, display):
        self.background.draw(display)
        self.scout_button.draw(display)
        self.swordsman_button.draw(display)
        self.archer_button.draw(display)
        self.horseman_button.draw(display)
        self.catapult_button.draw(display)


class SubLevelSection:
    """ one of the rect sections displaying the sub-level progress"""
    def __init__(self, rect, outline, fill=None):
        self.rect = rect
        self.outline = outline
        self.fill = fill

    def draw(self, display):
        if self.fill is not None:
            pygame.draw.rect(display, self.fill, self.rect)
        pygame.draw.rect(display, self.outline, self.rect, 1)


class SubLevelInspector:
    """ the bar displaying the number of sub-levels achieved and still to go"""
    def __init__(self, city_link, rect):
        self.city_link = city_link
        self.rect = rect

        self.sections = []
        self.update()

    def update(self):
        self.sections = []
        if not self.city_link.at_max():  # can still upgrade further (not at max level)
            sub_level_steps = constants.LEVELS[self.city_link.get_level() - 1]
            width = round(self.rect[2]/len(sub_level_steps))
            height = self.rect[3]

            # sections done
            x = self.rect[0]
            for section in sub_level_steps[:self.city_link.sub_level]:
                self.sections.append(
                    SubLevelSection([x, self.rect[1], width, height], (20, 20, 20), constants.FONTS["colour"]))
                x += width

            # sections left
            for section in sub_level_steps[self.city_link.sub_level:len(sub_level_steps)]:
                self.sections.append(SubLevelSection([x, self.rect[1], width, height], (20, 20, 20)))
                x += width
        # do not draw inspector if level is at max

    def draw(self, display):
        for section in self.sections:
            section.draw(display)


class UpgradeMenu:
    def __init__(self, city_link, GUI, position):
        self.stuck = False
        self.city_link = city_link
        self.GUI = GUI
        self.x, self.y = position

        self.panel = pygame_gui.Panel([self.x, self.y, 200, 100], 150, constants.COLOURS["panel"])

        self.back_button = pygame_gui.Button(paths.uiPath + "backwhite-small.png",
                                             paths.uiPath + "backwhite-small-hover.png",
                                             self.x + 5, self.y + 5)

        self.sub_level_inspector = SubLevelInspector(self.city_link, [self.x + 25, self.y + 52, 150, 5])

        self.upgrade_option = pygame_gui.TextButton(
            [self.x + 125, self.y + 70, 70, 25],
            0, 100,
            "upgrade",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"])

        if not self.city_link.at_max():
            title_text = "- Level Up -"
            upgrade_text = "(-" + str(self.city_link.get_upgrade_cost()) + ")"
            current_level_text = "l" + str(self.city_link.get_level())
            target_level_text = "l" + str(self.city_link.get_level() + 1)
            
        else:
            title_text = "- Max Level -"
            upgrade_text = "(n/a)"
            current_level_text = ""
            target_level_text = ""

        self.level_title = pygame_gui.Text(
            title_text,
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"],  constants.FONTS["main"],
            self.x + 65, self.y + 20)

        self.current_level = pygame_gui.Text(
            current_level_text,
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.x + 5, self.y + 45)

        self.target_level = pygame_gui.Text(
            target_level_text,
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.panel.rect.right - 15, self.y + 45)
        
        self.target_level_info = pygame_gui.Text(
            upgrade_text,
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.x + 100, self.y + 72)

    def check_clicked(self, mouse_x, mouse_y):
        if self.panel.rect.collidepoint(mouse_x, mouse_y):

            if self.back_button.check_clicked():
                self.GUI.delete_passive(self)
                self.GUI.launch_settlement_menu(self.city_link.get_position(), [self.x, self.y])

            elif self.upgrade_option.check_clicked():
                if not self.city_link.at_max():
                    level = self.city_link.get_level()  # must save level to detect change and display message
                    if self.city_link.afford_upgrade():
                        self.city_link.add_sub_level()

                        if self.city_link.get_level() != level:
                            self.GUI.send_message("Level Up!", [
                                "%s has reached Level %s" % (self.city_link.get_name(), self.city_link.get_level()),
                                "It now earns %s ap per turn" % self.city_link.get_ap_value()])

                        self.update()
                    else:
                        self.GUI.send_message("Not Enough!", ["Sorry, you don't have enough ap to", 
                                                              "upgrade this city."])

            return True
        return False

    def update(self):
        self.sub_level_inspector.update()
        self.GUI.game_view.world.get_tile(self.city_link.get_position()).update_image()
        self.GUI.player_tracker.update_player()

        self.__init__(self.city_link, self.GUI, [self.x, self.y])

    def allow_delete(self):
        return not self.stuck

    def draw(self, display):
        self.panel.draw(display)
        self.back_button.draw(display)

        self.level_title.draw(display)
        self.current_level.draw(display)
        self.target_level.draw(display)
        self.sub_level_inspector.draw(display)
        self.target_level_info.draw(display)
        self.upgrade_option.draw(display)


class MessageBase:
    """ The panel and text sections of a message, no functionality """
    def __init__(self, GUI, msg_title, text):
        self.GUI = GUI
        size = [250, 100]
        self.rect = [constants.DISPLAY_SIZE[0] / 2 - size[0] / 2,
                     constants.DISPLAY_SIZE[1] / 2 - size[1] / 2,
                     size[0],
                     size[1]]
        self.background = pygame_gui.Panel([self.rect[0], self.rect[1], self.rect[2], self.rect[3]],
                                           200,
                                           constants.COLOURS["panel"])

        if msg_title == "warning":
            self.title = pygame_gui.Text(
                "WARNING!",
                constants.FONTS["sizes"]["medium"], constants.COLOURS["red"], constants.FONTS["main"],
                self.rect[0] + 5, self.rect[1] + 5)
        else:
            self.title = pygame_gui.Text(
                msg_title,
                constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
                self.rect[0] + 5, self.rect[1] + 5)

        self.text = []
        counter = 0
        for line in text:
            self.text.append(pygame_gui.Text(
                line,
                constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
                self.rect[0] + 5, self.rect[1] + 30 + 18 * counter))
            counter += 1

    def draw(self, display):
        self.background.draw(display)
        self.title.draw(display)
        for line in self.text:
            line.draw(display)


class Message(MessageBase):
    """ Message with a single "ok" button, message closes when ok pressed """
    def __init__(self, GUI, msg_title, text):
        super().__init__(GUI, msg_title, text)

        ok_rect = [self.rect[0] + self.rect[2] - 35, self.rect[1] + self.rect[3] - 30, 35, 30]
        self.ok_button = pygame_gui.TextButton(
            ok_rect,
            0, 100,
            "ok",
            constants.FONTS["sizes"]["large"], constants.FONTS["colour"], constants.FONTS["main"])

    def handle_click(self):
        if self.ok_button.check_clicked():
            self.GUI.delete_persistent()  # GUI is interface of project.gui.GameGui

    def draw(self, display):
        super().draw(display)
        self.ok_button.draw(display)


class CheckMessage(MessageBase):
    """ Yes/No style check message, doesn't automatically close! relies on checking of self.result to be handled """
    def __init__(self, GUI, msg_title, text):
        super().__init__(GUI, msg_title, text)

        self.yes_button = pygame_gui.TextButton(
            [self.rect[0] + self.rect[2] - 35, self.rect[1] + self.rect[3] - 30, 35, 30],
            0, 100,
            "yes",
            constants.FONTS["sizes"]["large"], constants.FONTS["colour"], constants.FONTS["main"])

        self.no_button = pygame_gui.TextButton(
            [self.rect[0], self.rect[1] + self.rect[3] - 30, 35, 30],
            0, 100,
            "no",
            constants.FONTS["sizes"]["large"], constants.FONTS["colour"], constants.FONTS["main"])

        self.result = None

    def handle_click(self):  # added to depending on use in game or elsewhere (for type of deletion and exiting)
        if self.yes_button.check_clicked():
            self.result = True
        elif self.no_button.check_clicked():
            self.result = False

    def get_result(self):
        return self.result

    def draw(self, display):
        super().draw(display)
        self.yes_button.draw(display)
        self.no_button.draw(display)


class GameCheckMessage(CheckMessage):
    def __init__(self, GUI, msg_title, text):
        super().__init__(GUI, msg_title, text)

    def handle_click(self):
        super().handle_click()
        self.GUI.delete_persistent()


class GameOverMessage(Message):
    def handle_click(self):
        if self.ok_button.check_clicked():
            self.GUI.end_game()


class NextTurnMessage(Message):
    def handle_click(self):
        if self.ok_button.check_clicked():
            self.GUI.delete_persistent()
            self.GUI.next_turn()


class QuitMessage(GameCheckMessage):
    def handle_click(self):
        if self.yes_button.check_clicked():
            self.GUI.delete_persistent()
            self.GUI.state = "quit"
        elif self.no_button.check_clicked():
            self.GUI.delete_persistent()


class PlayerTracker:
    """ displays current player infomation in top panel"""
    def __init__(self, model):
        self.model_link = model

        # GUI Setup
        self.current_player_name_text = pygame_gui.Text(
            "",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"],constants.FONTS["main"],
            25, 2)
        self.topleft_panel = pygame_gui.Panel([0, 0, 200, 25], 150, constants.COLOURS["panel"])  # made to fit each players name width
        self.name_padding = 30

        self.player_values_panel = pygame_gui.Panel(
            [constants.DISPLAY_SIZE[0] / 2 - 100, 0, 230, 25],
            150,
            constants.COLOURS["panel"])

        # 30x30px for each icon
        self.current_turn_icon = pygame_gui.Image(paths.uiGamePath + "turn-icon.png",
                                                  self.player_values_panel.rect[0] + 10, 2)
        self.current_turn_text = pygame_gui.Text(
            "",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.player_values_panel.rect[0] + 35, 2)

        self.current_ap_icon = pygame_gui.Image(paths.uiGamePath + "ap-icon.png",
                                                self.player_values_panel.rect[0] + 65, 2)
        self.current_ap_text = pygame_gui.Text(
            "",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.player_values_panel.rect[0] + 90, 2)

        self.current_score_icon = pygame_gui.Image(paths.uiGamePath + "score-icon.png",
                                                   self.player_values_panel.rect[0] + 155, 2)
        self.current_score_text = pygame_gui.Text(
            "",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.player_values_panel.rect[0] + 180, 2)

    def update_player(self):
        current_player = self.model_link.get_current_player()
        self.current_player_name_text.change_text(current_player.get_name() + "'s turn")
        self.topleft_panel.reset_width(self.name_padding + self.current_player_name_text.get_rect()[2])
        self.current_turn_text.change_text(str(current_player.get_turn()))

        self.update_player_score(current_player)
        self.update_player_ap(current_player)

    def update_player_score(self, player):
        self.current_score_text.change_text("{:,}".format(player.get_score()))

    def update_player_ap(self, player):
        ap_gain = " (+" + str(player.get_turn_ap()) + ")"
        self.current_ap_text.change_text(str(player.get_ap()) + ap_gain)

    def draw(self, display):
        self.topleft_panel.draw(display)
        pygame.draw.circle(display, constants.COLOURS[self.model_link.get_current_player().get_colour()], [10, 12], 7)
        self.current_player_name_text.draw(display)

        self.player_values_panel.draw(display)

        self.current_turn_icon.draw(display)
        self.current_turn_text.draw(display)

        self.current_score_icon.draw(display)
        self.current_score_text.draw(display)

        self.current_ap_icon.draw(display)
        self.current_ap_text.draw(display)

# LEGACY - kept as might re-instate at future point
# class TileInspector:
#     def __init__(self, model):
#         self.model_link = model
#
#         self.tile_link = None
#         size = [265, 25]
#         self.rect = [round(constants.DISPLAY_SIZE[0]/2-size[0]/2), constants.DISPLAY_SIZE[1]-size[1], size[0], size[1]]
#         self.background = pygame_gui.Panel(self.rect, 200, constants.COLOURS["panel"])
#
#     def set_focus(self, tile_position):
#         self.tile_link = self.model_link.world.get_tile(tile_position)
#         self.tile_link.position = tile_position
#         self.update()
#
#     def update(self):
#         terrain = self.tile_link.get_type()
#         if terrain not in ["c", "s", "g", "w"]:  # w and g have nothing, s not on map, c resources can't be gathered
#
#             if self.tile_link.get_type() == "f":
#                     name = "forest"
#             elif self.tile_link.get_type() == "m":
#                 name = "mountain"
#             elif self.tile_link.get_type() == "o":
#                 name = "ore"
#
#             position = str(self.tile_link.position[0] + 1) + "," + str(self.tile_link.position[1] + 1 )
#             self.tile_text = pygame_gui.Text(name + " " + position, constants.FONTS["sizes"]["medium"],
#                                              constants.FONTS["colour"], constants.FONTS["main"], self.rect[0] + 5, self.rect[1] + 2)
#
#             self.wood_icon = pygame_gui.Image(paths.uiPath + "wood-icon-small.png", self.rect[0] + 100, self.rect[1] + 2)
#             self.wood_text = pygame_gui.Text(str(self.tile_link.wood), constants.FONTS["sizes"]["medium"],
#                                              constants.FONTS["colour"], constants.FONTS["main"], self.rect[0] + 125,
#                                              self.rect[1] + 2)
#
#             self.stone_icon = pygame_gui.Image(paths.uiPath + "stone-icon-small.png", self.rect[0] + 155, self.rect[1] + 2)
#             self.stone_text = pygame_gui.Text(str(self.tile_link.stone), constants.FONTS["sizes"]["medium"],
#                                               constants.FONTS["colour"], constants.FONTS["main"], self.rect[0] + 180,
#                                               self.rect[1] + 2)
#
#             self.metal_icon = pygame_gui.Image(paths.uiPath + "metal-icon-small.png", self.rect[0] + 210, self.rect[1] + 2)
#             self.metal_text = pygame_gui.Text(str(self.tile_link.metal), constants.FONTS["sizes"]["medium"],
#                                               constants.FONTS["colour"], constants.FONTS["main"], self.rect[0] + 235,
#                                               self.rect[1] + 2)
#         else:
#             self.tile_link = None
#
#     def reset_focus(self):
#         self.tile_link = None
#
#     def draw(self, display):
#         if self.tile_link is not None:
#             self.background.draw(display)
#             self.tile_text.draw(display)
#
#             self.wood_icon.draw(display)
#             self.wood_text.draw(display)
#
#             self.stone_icon.draw(display)
#             self.stone_text.draw(display)
#
#             self.metal_icon.draw(display)
#             self.metal_text.draw(display)


class MiniMapTile:
    def __init__(self, rect, colour):
        self.background = pygame_gui.Panel(rect, 200, colour)

    def update_colour(self, colour):
        self.background.colour = colour

    def draw(self, display):
        self.background.draw(display)


class MiniMapCircle(MiniMapTile):
    def draw(self, display):
        pygame.draw.ellipse(display, self.background.colour, self.background.rect)


class MiniMap:
    def __init__(self, model):
        self.model_link = model

        # Map Setup
        self.tiles = []
        self.tile_size = 6
        self.border = self.tile_size
        self.padding = 1  # between each squares
        self.panel_size = [self.tile_size*constants.MAP_SIZE[0] + self.padding*constants.MAP_SIZE[0] + self.border*2,
                           self.tile_size*constants.MAP_SIZE[1] + self.padding*constants.MAP_SIZE[1] + self.border*2]
        self.panel_position = [0, constants.DISPLAY_SIZE[1] - self.panel_size[1]]

        self.background = pygame_gui.Panel(
            [self.panel_position[0], self.panel_position[1], self.panel_size[0], self.panel_size[1]],
            200,
            constants.COLOURS["panel"])
        self.tiles = []
        x = self.panel_position[0] + self.border
        y = self.panel_position[1] + self.border
        for row in self.model_link.world.tiles:
            for tile in row:
                if tile.type == "s":
                    pass
                elif tile.type == "w":
                    self.tiles.append(MiniMapTile([x, y, self.tile_size, self.tile_size], (0, 100, 255)))
                elif tile.type == "g":
                    self.tiles.append(MiniMapTile([x, y, self.tile_size, self.tile_size], (0, 200, 0)))
                elif tile.type == "f":
                    self.tiles.append(MiniMapTile([x, y, self.tile_size, self.tile_size], (0, 100, 0)))
                elif tile.type == "m":
                    self.tiles.append(MiniMapTile([x, y, self.tile_size, self.tile_size], (100, 100, 100)))
                elif tile.type == "o":
                    self.tiles.append(MiniMapTile([x, y, self.tile_size, self.tile_size], (60, 60, 60)))
                elif tile.type == "c":
                    rect = [x + self.padding, y + self.padding,
                            self.tile_size - self.padding*2, self.tile_size - self.padding*2]
                    if tile.current_holder is not None:
                        player = self.model_link.get_player(tile.current_holder)
                        colour = player.get_colour()
                        self.tiles.append(MiniMapTile(rect, constants.COLOURS[colour]))
                    else:
                        self.tiles.append(MiniMapTile(rect, (200, 200, 200)))

                y += self.tile_size + self.padding
            y = self.panel_position[1] + self.border
            x += self.tile_size + self.padding

        # GUI Interaction
        self.hide_button = pygame_gui.TextButton(
            [0, self.background.rect[1] - 20, 100, 20],
            220, 240,
            "hide minimap", constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"])

        self.show_button = pygame_gui.TextButton(
            [0, constants.DISPLAY_SIZE[1] - 20, 100, 20],
            200, 220,
            "show minimap", constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"])

    def refresh(self):
        self.__init__(self.model_link)

    def is_visible(self):
        return self.model_link.get_current_player().get_minimap_status()

    def handle_click(self):
        if self.is_visible():
            if self.hide_button.check_clicked():
                self.model_link.get_current_player().set_minimap_status(False)
        else:
            if self.show_button.check_clicked():
                self.model_link.get_current_player().set_minimap_status(True)

    def draw(self, display):
        if self.is_visible():
            self.hide_button.draw(display)

            self.background.draw(display)

            for tile in self.tiles:
                tile.draw(display)

        else:
            self.show_button.draw(display)


class GameMenu:
    def __init__(self, GUI, model):
        self.GUI = GUI
        self.model_link = model

        size = [350, 100]
        self.rect = [constants.DISPLAY_SIZE[0] / 2 - size[0] / 2,
                     constants.DISPLAY_SIZE[1] / 2 - size[1] / 2,
                     size[0],
                     size[1]]
        self.background = pygame_gui.Panel([self.rect[0], self.rect[1], self.rect[2], self.rect[3]],
                                           200,
                                           constants.COLOURS["panel"])

        self.game_name = pygame_gui.Text(
            self.model_link.game_name,
            constants.FONTS["sizes"]["large"], constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 5, self.rect[1] + 5)

        self.map_name = pygame_gui.Text(
            self.model_link.map_name,
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 5, self.rect[1] + 30)

        self.exit_button = pygame_gui.Button(paths.uiPath + "smallcross.png", paths.uiPath + "smallcross-hover.png",
                                             self.rect[0] + self.rect[2] - 30, self.rect[1] + 5)

        self.menu_exit_button = pygame_gui.TextButton(
            [self.rect[0], self.rect[1] + self.rect[3] - 30, 100, 30],
            0, 50,
            "exit to menu",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"])

        self.help_button = pygame_gui.TextButton(
            [self.rect[0] + self.rect[2] - 60, self.rect[1] + self.rect[3] - 30, 60, 30],
            0, 50,
            "help",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"])

    def handle_click(self):
        if self.exit_button.check_clicked():
            self.GUI.delete_persistent()  # reaction in game, with gui layering. overwritten in subclass for others

        elif self.menu_exit_button.check_clicked():
            self.GUI.delete_persistent()
            self.GUI.state = "menu"

        elif self.help_button.check_clicked():
            self.GUI.delete_persistent()
            self.GUI.launch_help()

    def draw(self, display):
        self.background.draw(display)
        self.game_name.draw(display)
        self.map_name.draw(display)
        self.exit_button.draw(display)
        self.menu_exit_button.draw(display)
        self.help_button.draw(display)


class GameLeaderboard:
    def __init__(self, GUI, model):
        self.GUI = GUI
        self.model_link = model

        size = [600, 300]
        self.rect = [constants.DISPLAY_SIZE[0] / 2 - size[0] / 2, constants.DISPLAY_SIZE[1] / 2 - size[1] / 2, size[0],
                     size[1]]
        self.background = pygame_gui.Panel(self.rect, 200, constants.COLOURS["panel"])

        self.game_name = pygame_gui.Text(
            "Leaderboard",
            constants.FONTS["sizes"]["large"], constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 10, self.rect[1] + 10)

        self.exit_button = pygame_gui.Button(paths.uiPath + "smallcross.png", paths.uiPath + "smallcross-hover.png",
                                             self.rect[0] + self.rect[2] - 30, self.rect[1] + 5)

        # Leaderboard Headings
        self.rank = pygame_gui.Text(
            "No.",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 45, self.rect[1] + 50)

        self.name = pygame_gui.Text(
            "Name",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 130, self.rect[1] + 50)

        self.cities = pygame_gui.Text(
            "Cities",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 360, self.rect[1] + 50)

        self.score = pygame_gui.Text(
            "Score (max)",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 460, self.rect[1] + 50)

        # Leaderboard Setup (constant, wont change while leaderboard open)
        self.ordered_players = sorted(self.model_link.players, key=lambda x: x.get_score(), reverse=True)

        slot_rect = [self.rect[0] + 40, self.rect[1] + 90, 520, 35]
        spacing = 50
        self.player_slots = []
        rank_count = 1
        for player in self.ordered_players:
            self.player_slots.append(LeaderboardSlot(slot_rect.copy(), player, rank_count))
            slot_rect[1] += spacing
            rank_count += 1

    def handle_click(self):
        if self.exit_button.check_clicked():
            self.GUI.delete_persistent()  # reaction in game, with gui layering. overwritten in subclass for others

    def draw(self, display):
        self.background.draw(display)
        self.game_name.draw(display)
        self.exit_button.draw(display)

        self.rank.draw(display)
        self.name.draw(display)
        self.cities.draw(display)
        self.score.draw(display)

        for player in self.player_slots:
            player.draw(display)


class LeaderboardSlot:
    def __init__(self, rect, player, rank):
        self.rect = rect
        self.player_link = player

        self.panel = pygame_gui.Panel(self.rect,  100, constants.COLOURS["panel"])

        self.rank = pygame_gui.Text(
            str(rank) + ".",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 15, self.rect[1] + 8)

        self.name = pygame_gui.Text(
            self.player_link.get_name(),
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 90, self.rect[1] + 8)

        self.cities = pygame_gui.Text(
            str(len(self.player_link.settlements)),
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 330, self.rect[1] + 8)

        self.score = pygame_gui.Text(
            "{:,}".format(self.player_link.get_max_score()),
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 425, self.rect[1] + 8)

    def draw(self, display):
        self.panel.draw(display)
        self.rank.draw(display)
        pygame.draw.circle(display,
                           constants.COLOURS[self.player_link.get_colour()],
                           [int(self.rect[0] + 55), int(self.rect[1] + self.rect[3]/2)], 10)
        self.name.draw(display)
        self.cities.draw(display)
        self.score.draw(display)


class Paragraph:
    def __init__(self, x, y, text):
        self.text = []
        counter = 0
        for line in text:
            self.text.append(pygame_gui.Text(
                line,
                constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
                x, y + 30 + 18 * counter))
            counter += 1

    def draw(self, display):
        for line in self.text:
            line.draw(display)


class Help:
    def __init__(self, GUI):
        self.GUI = GUI

        # Base Setup
        size = [800, 500]
        self.rect = [constants.DISPLAY_SIZE[0] / 2 - size[0] / 2,
                     constants.DISPLAY_SIZE[1] / 2 - size[1] / 2,
                     size[0],
                     size[1]]

        self.background = pygame_gui.Panel([self.rect[0], self.rect[1], self.rect[2], self.rect[3]],
                                           200,
                                           constants.COLOURS["panel"])

        self.title = pygame_gui.Text(
            "Help",
            constants.FONTS["sizes"]["large"], constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 5, self.rect[1] + 5)

        self.exit_button = pygame_gui.Button(paths.uiPath + "smallcross.png", paths.uiPath + "smallcross-hover.png",
                                             self.rect[0] + self.rect[2] - 30, self.rect[1] + 5)

        # Content Setup
        self.main_instructions_heading = pygame_gui.Text(
            "-- How to Play --",
            constants.FONTS["sizes"]["large"] - 2, constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 140, self.rect[1] + 30)

        self.instructions = Paragraph(self.rect[0] + 5, self.rect[1] + 40, [
            "The aim is simple, expand your empire and become the last",
            "player standing to win the game. A player is defeated once they",
            "have no cities left under their control.",
            "",
            "Cities",
            "These are central to your success. It is by taking cities you grow",
            "your army, as through cities you can spawn units.",
            "Be sure to upgrade your cities too! Each city you own produces",
            "so many action points per turn. By upgrading cities they will",
            "earn you more ap per turn, allowing you to spawn more and",
            "more powerful units.",
            "A city's menu can be opened by clicking on the city, if no unit is",
            "occupying its square.",
            "",
            "Units",
            "Your units are used to battle with other players, to attack, defend,",
            "and capture cities. They can be spawned through the city menu.",
            "A unit has a maximum of one attack, and one move per turn, and",
            "is in-active after being spawned until the next turn begins.",
            "A units actions can be triggered by clicking on the unit, then",
            "clicking on one of the crosses, blue to move, red to attack.",
            "For a city to be conquered, a unit must occupy it for one turn",
            "cycle, then you can open the unit actions and click on the city."
        ])

        self.reference_heading = pygame_gui.Text(
            "-- Reference --",
            constants.FONTS["sizes"]["large"] - 2, constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 550, self.rect[1] + 30)

        self.unit_spec_heading = pygame_gui.Text(
            "Unit Specs",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 405, self.rect[1] + 55)

        self.unit_spec_table_heading = pygame_gui.Text(
            "( Health | Attack | Defense | Reach | Movement | Cost )",
            constants.FONTS["sizes"]["small"], constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 540, self.rect[1] + 65)

        # Unit Table Setup
        # Scout
        self.scout_image = pygame_gui.Image(paths.uiGamePath + "scouticon.png", self.rect[0] + 405, self.rect[1] + 85)
        self.scout_text = pygame_gui.Text(
            "Scout",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 470, self.rect[1] + 90)

        self.scout_specs = pygame_gui.Text(
            "|  %s  |   %s  |   %s  |   %s  |   %s  |   -%sap  |" % (
                constants.UNIT_SPECS["scout"]["max_health"],
                constants.UNIT_SPECS["scout"]["attack"],
                constants.UNIT_SPECS["scout"]["defence"],
                constants.UNIT_SPECS["scout"]["reach"],
                constants.UNIT_SPECS["scout"]["movement"],
                constants.UNIT_SPECS["scout"]["spawn_cost"],
            ),
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 575, self.scout_text.rect.y)

        # Swordsman
        self.swordsman_image = pygame_gui.Image(paths.uiGamePath + "swordsmanicon.png", self.rect[0] + 405,
                                                self.rect[1] + 110)
        self.swordsman_text = pygame_gui.Text(
            "Swordsman", constants.FONTS["sizes"]["medium"],
            constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 470, self.rect[1] + 125)

        self.swordsman_specs = pygame_gui.Text(
            "|  %s  |   %s  |   %s  |   %s  |   %s  |   -%sap  |" % (
                constants.UNIT_SPECS["swordsman"]["max_health"],
                constants.UNIT_SPECS["swordsman"]["attack"],
                constants.UNIT_SPECS["swordsman"]["defence"],
                constants.UNIT_SPECS["swordsman"]["reach"],
                constants.UNIT_SPECS["swordsman"]["movement"],
                constants.UNIT_SPECS["swordsman"]["spawn_cost"],
            ),
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 575, self.swordsman_text.rect.y)

        # Archer
        self.archer_image = pygame_gui.Image(paths.uiGamePath + "archericon.png", self.rect[0] + 405,
                                             self.rect[1] + 145)
        self.archer_text = pygame_gui.Text(
            "Archer",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 470, self.rect[1] + 160)

        self.archer_specs = pygame_gui.Text(
            "|  %s  |   %s  |   %s  |   %s  |   %s  |   -%sap  |" % (
                constants.UNIT_SPECS["archer"]["max_health"],
                constants.UNIT_SPECS["archer"]["attack"],
                constants.UNIT_SPECS["archer"]["defence"],
                constants.UNIT_SPECS["archer"]["reach"],
                constants.UNIT_SPECS["archer"]["movement"],
                constants.UNIT_SPECS["archer"]["spawn_cost"],
            ),
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 575, self.archer_text.rect.y)

        # Horseman
        self.horseman_image = pygame_gui.Image(paths.uiGamePath + "horsemanicon.png", self.rect[0] + 405,
                                               self.rect[1] + 187)
        self.horseman_text = pygame_gui.Text(
            "Horseman",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 470, self.rect[1] + 195)

        self.horseman_specs = pygame_gui.Text(
            "|  %s  |   %s  |   %s  |   %s  |   %s  |   -%sap  |" % (
                constants.UNIT_SPECS["horseman"]["max_health"],
                constants.UNIT_SPECS["horseman"]["attack"],
                constants.UNIT_SPECS["horseman"]["defence"],
                constants.UNIT_SPECS["horseman"]["reach"],
                constants.UNIT_SPECS["horseman"]["movement"],
                constants.UNIT_SPECS["horseman"]["spawn_cost"],
            ),
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 575, self.horseman_text.rect.y)

        # Catapult
        self.catapult_image = pygame_gui.Image(paths.uiGamePath + "catapulticon.png", self.rect[0] + 405,
                                               self.rect[1] + 222)
        self.catapult_text = pygame_gui.Text(
            "Catapult",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 470, self.rect[1] + 230)

        self.catapult_specs = pygame_gui.Text(
            "|  %s  |   %s  |   %s  |   %s  |   %s  |   -%sap  |" % (
                constants.UNIT_SPECS["catapult"]["max_health"],
                constants.UNIT_SPECS["catapult"]["attack"],
                constants.UNIT_SPECS["catapult"]["defence"],
                constants.UNIT_SPECS["catapult"]["reach"],
                constants.UNIT_SPECS["catapult"]["movement"],
                constants.UNIT_SPECS["catapult"]["spawn_cost"],
            ),
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 575, self.catapult_text.rect.y)

        self.icon_heading = pygame_gui.Text(
            "Other Icons",
            constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
            self.rect[0] + 405, self.rect[1] + 270)

        self.score_image = pygame_gui.Image(paths.uiGamePath + "score-icon.png", self.rect[0] + 405, self.rect[1] + 300)
        self.score_explanation = Paragraph(self.rect[0] + 430, self.rect[1] + 270, [
            "Score",
            "This is how players are ranked, and you know whose wining.",
            "You get points from you cities, units, and how long you can",
            "survive."
        ])
        self.ap_image = pygame_gui.Image(paths.uiGamePath + "ap-icon.png", self.rect[0] + 405, self.rect[1] + 380)
        self.ap_explanation = Paragraph(self.rect[0] + 430, self.rect[1] + 350, [
            "AP",
            "Action Points (ap) are spent to spawn units and upgrade",
            "cities.",
            "-2 or (-2)  -  This shows the action will cost 2 action points.",
            "+2 or (+2)  -  This shows the action points you will gain.",
        ])

    def handle_click(self):
        if self.exit_button.check_clicked():
            self.GUI.delete_persistent()  # reaction in game, with gui layering. overwritten in subclass for others

    def draw(self, display):
        self.background.draw(display)
        self.title.draw(display)
        self.exit_button.draw(display)

        self.main_instructions_heading.draw(display)
        self.instructions.draw(display)

        pygame.draw.line(display, (220, 220, 220), self.background.rect.midtop, self.background.rect.midbottom)

        self.reference_heading.draw(display)
        self.unit_spec_heading.draw(display)
        self.unit_spec_table_heading.draw(display)

        self.scout_image.draw(display)
        self.scout_text.draw(display)
        self.scout_specs.draw(display)

        self.swordsman_image.draw(display)
        self.swordsman_text.draw(display)
        self.swordsman_specs.draw(display)

        self.archer_image.draw(display)
        self.archer_text.draw(display)
        self.archer_specs.draw(display)

        self.horseman_image.draw(display)
        self.horseman_text.draw(display)
        self.horseman_specs.draw(display)

        self.catapult_image.draw(display)
        self.catapult_text.draw(display)
        self.catapult_specs.draw(display)

        self.icon_heading.draw(display)
        self.score_image.draw(display)
        self.score_explanation.draw(display)

        self.ap_image.draw(display)
        self.ap_explanation.draw(display)


class WelcomeMessage:
    def __init__(self, GUI):
        self.GUI = GUI

        msg_title = "Game On!"

        text = ["Have a look round the map to find your spawn", "city and get battling!"]

        sub_text = ["First time? If you get stuck try checking out the help section", "from the menu in the top right."]

        size = [300, 120]
        self.rect = [constants.DISPLAY_SIZE[0] / 2 - size[0] / 2,
                     constants.DISPLAY_SIZE[1] / 2 - size[1] / 2,
                     size[0],
                     size[1]]
        self.background = pygame_gui.Panel([self.rect[0], self.rect[1], self.rect[2], self.rect[3]],
                                           200,
                                           constants.COLOURS["panel"])

        if msg_title == "warning":
            self.title = pygame_gui.Text(
                "WARNING!",
                constants.FONTS["sizes"]["medium"], constants.COLOURS["red"], constants.FONTS["main"],
                self.rect[0] + 5, self.rect[1] + 5)
        else:
            self.title = pygame_gui.Text(
                msg_title,
                constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
                self.rect[0] + 5, self.rect[1] + 5)

        # Main Text
        self.text = []
        counter = 0
        for line in text:
            self.text.append(pygame_gui.Text(
                line,
                constants.FONTS["sizes"]["medium"], constants.FONTS["colour"], constants.FONTS["main"],
                self.rect[0] + 5, self.rect[1] + 30 + 18 * counter))
            counter += 1

        # Sub Text
        counter = 0
        for line in sub_text:
            self.text.append(pygame_gui.Text(
                line, constants.FONTS["sizes"]["small"], constants.FONTS["colour"], constants.FONTS["main"],
                self.rect[0] + 5, self.rect[1] + 70 + 18 * counter))
            counter += 1

        ok_rect = [self.rect[0] + self.rect[2] - 30, self.rect[1] + self.rect[3] - 30, 30, 30]
        self.ok_button = pygame_gui.TextButton(
            ok_rect,
            0, 50,
            "ok",
            constants.FONTS["sizes"]["large"], constants.FONTS["colour"], constants.FONTS["main"])

    def handle_click(self):
        if self.ok_button.check_clicked():
            self.GUI.delete_persistent()  # reaction in game, with gui layering. overwritten in subclass for others

    def draw(self, display):
        self.background.draw(display)
        self.title.draw(display)
        for line in self.text:
            line.draw(display)
        self.ok_button.draw(display)
