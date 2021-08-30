import pygame

import project.game.isometric as isometric
import project.game.surface as surface

import project.background as background
import pygame_gui

import constants
import paths


class PhysicalGame:
    """ heavily linked to the GUI, but responsible for map-level interactions. """
    def __init__(self, display, model, GUI):
        self.display = display
        self.model_link = model
        self.GUI = GUI

        # Background
        self.stars = background.Starscape(self.display.get_rect())

        # General Setup (surface + camera)
        self.game_surface = surface.Surface(constants.GAME_RECT)
        self.game_surface.main_surface.set_colorkey(constants.COLOURS["black"])  # so stars drawn to display first are seen

        # Map Setup
        self.world = VisualWorld(self.model_link)

        # Focuses
        self.tile_focus = None  # record of the current tile clicked
        self.active_unit = None  # record of current unit clicked on

        # Units Image Setup
        self.unit_images = {
            "base-unit": pygame.image.load(paths.unitPath + "base-unit.png").convert_alpha(),
            "unit-counter": pygame.image.load(paths.unitPath + "unit-counter.png").convert_alpha(),

            "blue-scout": pygame.image.load(paths.unitPath + "blue-scout.png").convert_alpha(),
            "blue-swordsman": pygame.image.load(paths.unitPath + "blue-swordsman.png").convert_alpha(),
            "blue-archer": pygame.image.load(paths.unitPath + "blue-archer.png").convert_alpha(),
            "blue-horseman": pygame.image.load(paths.unitPath + "blue-horseman.png").convert_alpha(),
            "blue-catapult": pygame.image.load(paths.unitPath + "blue-catapult.png").convert_alpha(),

            "yellow-scout": pygame.image.load(paths.unitPath + "yellow-scout.png").convert_alpha(),
            "yellow-swordsman": pygame.image.load(paths.unitPath + "yellow-swordsman.png").convert_alpha(),
            "yellow-archer": pygame.image.load(paths.unitPath + "yellow-archer.png").convert_alpha(),
            "yellow-horseman": pygame.image.load(paths.unitPath + "yellow-horseman.png").convert_alpha(),
            "yellow-catapult": pygame.image.load(paths.unitPath + "yellow-catapult.png").convert_alpha(),

            "green-scout": pygame.image.load(paths.unitPath + "green-scout.png").convert_alpha(),
            "green-swordsman": pygame.image.load(paths.unitPath + "green-swordsman.png").convert_alpha(),
            "green-archer": pygame.image.load(paths.unitPath + "green-archer.png").convert_alpha(),
            "green-horseman": pygame.image.load(paths.unitPath + "green-horseman.png").convert_alpha(),
            "green-catapult": pygame.image.load(paths.unitPath + "green-catapult.png").convert_alpha(),

            "red-scout": pygame.image.load(paths.unitPath + "red-scout.png").convert_alpha(),
            "red-swordsman": pygame.image.load(paths.unitPath + "red-swordsman.png").convert_alpha(),
            "red-archer": pygame.image.load(paths.unitPath + "red-archer.png").convert_alpha(),
            "red-horseman": pygame.image.load(paths.unitPath + "red-horseman.png").convert_alpha(),
            "red-catapult": pygame.image.load(paths.unitPath + "red-catapult.png").convert_alpha(),
        }

        self.unit_action_images = {
            "move": pygame.image.load(paths.unitPath + "move-indicator.png"),
            "attack": pygame.image.load(paths.unitPath + "attack-indicator.png"),
            "conquer": pygame.image.load(paths.unitPath + "conquer-indicator.png"),
        }

        self.unit_health_text = pygame_gui.Text("",
            13, constants.FONTS["colour"], constants.FONTS["main"],
            0, 0)  # changed during unit drawing

    def map_clicked(self, mouse_x, mouse_y):
        focus = isometric.getIndex([mouse_x, mouse_y], self.game_surface.get_position())
        if focus[0] in range(0, constants.MAP_SIZE[0]) and focus[1] in range(0, constants.MAP_SIZE[1]):
            self.tile_focus = focus
            return True
        self.tile_focus = None  # deselected everything, clicked off map.
        self.active_unit = None
        return False

    def handled_unit_click(self):
        if self.model_link.unit_selected(self.tile_focus):
            if self.model_link.get_unit(self.tile_focus).owner == self.model_link.current_player_name:
                self.active_unit = self.model_link.get_unit(self.tile_focus)
            return True
        return False

    def handle_unit_actions(self):
        if not self.handle_conquer():
            if not self.handle_movement():
                if not self.handle_attacking():
                    self.active_unit = None
                    return False
        self.active_unit = None  # unit de-selected after action
        return True

    def handle_conquer(self):
        conquered = False

        if self.model_link.check_conquer(self.active_unit) and self.tile_focus == self.active_unit.position:
            self.model_link.conquer(self.active_unit.position)
            self.active_unit.make_inactive()
            conquered = True

            # Death Checking - might have destroyed players last city
            killed_player = self.model_link.handle_death()
            if killed_player is not None:
                self.GUI.send_message("Destroyed!", ["Unlucky %s " % killed_player,
                                                     "You have been destroyed and are",
                                                     "out of the game."])

            self.GUI.send_message("Conquered!", ["You have successfully gained control",
                                                 "of %s" % self.model_link.world.get_tile(self.tile_focus).get_name()])
            self.GUI.player_tracker.update_player()
            self.GUI.mini_map.refresh()
            self.world.get_tile(self.tile_focus).update_owner()

        return conquered

    def handle_movement(self):
        moved = False
        if self.tile_focus in self.model_link.get_moves(self.active_unit):
            self.model_link.move_unit(self.tile_focus, self.active_unit)
            self.GUI.player_tracker.update_player()  # ap and score will have changed

        return moved

    def handle_attacking(self):
        attacked = False
        if self.tile_focus in self.model_link.get_attacks(self.active_unit):
            defending_unit = self.model_link.get_unit(self.tile_focus)
            self.model_link.make_attack(self.active_unit, defending_unit)
            self.GUI.player_tracker.update_player()  # ap and score will have changed
        return attacked

    def handled_settlement_click(self):
        if self.model_link.settlement_selected(self.tile_focus):
            self.GUI.launch_settlement_menu(self.tile_focus, pygame.mouse.get_pos())
            return True
        return False

    def draw(self, display):
        display.fill(constants.COLOURS["black"])
        self.game_surface.main_surface.fill(constants.COLOURS["black"])

        self.stars.draw(display)
        self.world.draw(self.game_surface.main_surface)

        if self.active_unit is not None:
            self.draw_action_overlay(self.active_unit)

        self.draw_units()

        self.game_surface.draw(display)

    def draw_units(self):
        for unit in self.model_link.all_units():
            x, y = isometric.get_iso(unit.position[0], unit.position[1], self.game_surface.get_position())
            # Setting Unit Health Text
            self.unit_health_text.change_text(str(unit.health))
            self.unit_health_text.x = x + constants.TILE_WIDTH / 2 - 6
            self.unit_health_text.y = y + constants.TILE_HEIGHT - 15
            # Drawing Unit
            image_name = self.model_link.get_player(unit.owner).get_colour() + "-" + unit.type
            self.game_surface.main_surface.blit(self.unit_images["base-unit"], [x, y])
            #self.game_surface.main_surface.blit(self.unit_images["unit-counter"], [x, y])
            self.game_surface.main_surface.blit(self.unit_images[image_name], [x, y])
            # Drawing Unit Health Text
            self.unit_health_text.draw(self.game_surface.main_surface)

    def draw_action_overlay(self, unit):
        possible_moves = self.model_link.get_moves(unit)
        possible_attacks = self.model_link.get_attacks(unit)  # both lists of positions [[row,col]...]

        for move in possible_moves:
            x, y = isometric.get_iso(move[0], move[1], self.game_surface.get_position())
            self.game_surface.main_surface.blit(self.unit_action_images["move"], [x, y])

        for attack in possible_attacks:
            x, y = isometric.get_iso(attack[0], attack[1], self.game_surface.get_position())
            self.game_surface.main_surface.blit(self.unit_action_images["attack"], [x, y])

        if self.model_link.check_conquer(unit):
            x, y = isometric.get_iso(unit.position[0], unit.position[1], self.game_surface.get_position())
            self.game_surface.main_surface.blit(self.unit_action_images["conquer"], [x, y])


def get_tile_image(tile_type):
    if tile_type == "s":
        return paths.tilePath + "sea.png"
    elif tile_type == "w":
        return paths.tilePath + "water.png"
    elif tile_type == "g":
        return paths.tilePath + "grass.png"
    elif tile_type == "f":
        return paths.tilePath + "forest.png"
    elif tile_type == "m":
        return paths.tilePath + "mountain.png"
    elif tile_type == "o":
        return paths.tilePath + "quarry.png"


def get_tile_offset(tile_type):  # some assets are taller than others, must compensate for this.
    if tile_type == "s":
        return 0
    elif tile_type == "w":
        return -20
    elif tile_type == "m" or tile_type == "o":
        return 10
    elif tile_type == "c":
        return 20
    else:
        return 0


def get_tile_position(row, col):
    isox = isometric.getIsoX(row, col)
    isoy = isometric.getIsoY(row, col)
    return [isox, isoy]


class VisualTile:
    def __init__(self, tile_link):
        self.tile_link = tile_link
        self.image = pygame.image.load(get_tile_image(self.tile_link.get_type())).convert_alpha()
        self.x, self.y = get_tile_position(self.tile_link.get_position()[0], self.tile_link.get_position()[1])
        self.y = self.y - get_tile_offset(self.tile_link.get_type())

    def draw(self, surface):
        surface.blit(self.image, [self.x, self.y])


class VisualCityTile:
    def __init__(self, city_link, model_link):
        self.model_link = model_link
        self.city_link = city_link
        self.image = self.get_image()
        self.x, self.y = get_tile_position(self.city_link.get_position()[0], self.city_link.get_position()[1])
        self.y = self.y - get_tile_offset(self.city_link.get_type())

        self.ownership_indicator = self.get_indicator_image()

    def get_image(self):
        tile = paths.tilePath + "city-l" + str(self.city_link.get_level()) + ".png"  # ie: city-l1.png, city-l2.png...
        return pygame.image.load(tile).convert_alpha()

    def get_indicator_image(self):
        if self.city_link.current_holder is not None:
            player = self.model_link.get_player(self.city_link.current_holder)

            indicator = paths.tilePath + "l%s-%s.png" % (self.city_link.get_level(), player.get_colour())  # ie: l1-blue...
            return pygame.image.load(indicator).convert_alpha()

    # returns none to self.ownership_indicator, but wont be drawn at this point anyway.

    def update_image(self):
        self.image = self.get_image()
        self.update_owner()

    def update_owner(self):
        self.ownership_indicator = self.get_indicator_image()

    def draw(self, surface):
        surface.blit(self.image, [self.x, self.y])
        if self.city_link.current_holder is not None:
            surface.blit(self.ownership_indicator, [self.x, self.y + get_tile_offset("c")])


class VisualWorld:
    def __init__(self, model):
        self.model_link = model
        model_tiles = self.model_link.world.tiles

        self.tiles = []
        self.settlement_names = []
        for row in model_tiles:
            self.tiles.append([])
            for tile in row:
                if tile.get_type() == "c":
                    new_tile = VisualCityTile(tile, self.model_link)
                    # Create City Text
                    settlement_text = pygame_gui.Text(new_tile.city_link.get_name(), constants.FONTS["sizes"]["small"],
                                                      (255, 255, 255), constants.FONTS["main"],
                                                      new_tile.x,
                                                      new_tile.y + constants.TILE_HEIGHT + get_tile_offset("c"))
                    settlement_text.x += (constants.TILE_WIDTH / 2) - settlement_text.get_rect()[2] / 2
                    self.settlement_names.append(settlement_text)
                else:
                    new_tile = VisualTile(tile)
                self.tiles[len(self.tiles) - 1].append(new_tile)

    def get_tile(self, position):
        return self.tiles[position[0]][position[1]]

    def draw(self, surface):
        for row in self.tiles:
            for t in row:
                t.draw(surface)

        for name in self.settlement_names:
            name.draw(surface)
