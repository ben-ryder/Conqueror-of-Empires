# Ben-Ryder 2019

import random
import paths
import constants

import project.game.calculations as calculations


class Model:
    """ holds all the data and interface to manipulate the game """
    def __init__(self, save_data):
        self.game_name = save_data["game_name"]
        self.map_name = save_data["map_name"]
        self.game_end = save_data["game_end"]

        self.players = [Player(self, player_data) for player_data in save_data["players"]]

        self.world = World(self, save_data["world"])  # assigns settlements to players

        # If the game is new set the current player, else just load it in.
        if save_data["current_player"] is None:
            self.current_player_name = self.players[0].get_name()
            self.get_current_player().start_turn()
        else:
            self.current_player_name = save_data["current_player"]

    def get_save_data(self):
        return {
            "game_name": self.game_name,
            "map_name": self.map_name,
            "game_end": self.game_end,
            "current_player": self.current_player_name,  # store name, player data is stored in "players"
            "players": [player.get_save_data() for player in self.players],
            "world": self.world.get_save_data()
        }

    def get_player(self, name):
        for player in self.players:
            if player.get_name() == name:
                return player
        return None

    def all_units(self):
        return [unit for player in self.players for unit in player.units]

    def next_turn(self):
        self.get_current_player().end_turn()

        # Getting new turn
        if not self.is_winner():  # if more than 1 player alive
            self.current_player_name = self.get_next_player()
        else:
            self.game_end = True

        self.get_current_player().start_turn()

    def get_next_player(self):
        valid_choice = False
        player = self.get_current_player()
        while not valid_choice:  # wont be infinite, as to be called at least two players are left.
            if self.players.index(player) < len(self.players) - 1:
                player = self.players[self.players.index(player) + 1]
            else:
                player = self.players[0]
            valid_choice = not player.is_dead()
        return player.get_name()

    def try_spawn(self, unit_type, position):
        if not self.get_unit(position):
            current_player = self.get_current_player()
            if current_player.get_ap() - constants.UNIT_SPECS[unit_type]["spawn_cost"] >= 0:
                current_player.add_unit(Unit(unit_type, position, current_player.get_name()))
                current_player.take_ap(constants.UNIT_SPECS[unit_type]["spawn_cost"])
                return True
        return False

    def make_attack(self, attacker, defender):
        attacker.set_attacked()
        killed_units = calculations.apply_attack(attacker, defender)
        for unit in killed_units:  # could be both units
            self.get_player(unit.owner).units.remove(unit)

    def check_conquer(self, unit):
        if (self.world.get_tile(unit.position).get_type() == "c" and
                self.world.get_tile(unit.position).get_holder() != self.get_current_player().get_name()):
            if not unit.has_moved():  # must stay in settlement for a turn cycle
                return True
        return False

    def conquer(self, position):
        settlement = self.world.get_tile(position)

        if settlement.current_holder is not None:
            self.get_player(settlement.current_holder).remove_settlement(settlement.get_position())

        settlement.change_holder(self.get_current_player().get_name())
        self.get_current_player().add_settlement(settlement.get_position())

    def handle_death(self):
        for player in self.players:
            if self.check_death(player):
                player.kill()

                if self.is_winner():  # here, as otherwise must wait for next_turn call
                    self.game_end = True

                return player.get_name()  # assuming only one player died, return first found.
        return None

    def check_death(self, player):
        return len(player.settlements) == 0 and not player.is_dead()

    def game_ended(self):
        return self.game_end

    def is_winner(self):
        return len([player for player in self.players if not player.is_dead()]) == 1

    def get_winner(self):
        return self.get_current_player().get_name()  # will always end on current player, as they take last city.

    def get_current_player(self):
        return self.get_player(self.current_player_name)

    def unit_selected(self, position):
        for unit in self.all_units():
            if position == unit.position:
                return True
        return False

    def get_unit(self, position):
        for unit in self.all_units():
            if unit.position == position:
                return unit
        return None

    def settlement_selected(self, position):
        tile = self.world.get_tile(position)
        if tile.get_type() == "c" and tile.get_holder() == self.current_player_name:
            return True
        return False

    def get_moves(self, unit):
        moves = []
        if not unit.has_moved():
            for x in range(unit.position[0] - unit.movement, unit.position[0] + unit.movement + 1):
                for y in range(unit.position[1] - unit.movement, unit.position[1] + unit.movement + 1):
                    if ([x, y] != unit.position and
                            x in range(0, constants.MAP_SIZE[0]) and
                            y in range(0, constants.MAP_SIZE[1]) and
                            self.world.get_tile([x, y]).get_type() in unit.allowed_moves and not self.get_unit([x, y])):
                        moves.append([x, y])

        return moves

    def move_unit(self, position, unit):
        unit.move(position)

    def get_attacks(self, unit):
        attacks = []
        if not unit.has_attacked():
            for x in range(unit.position[0] - unit.reach, unit.position[0] + unit.reach + 1):
                for y in range(unit.position[1] - unit.reach, unit.position[1] + unit.reach + 1):
                    if [x, y] != unit.position and self.get_unit([x, y]):
                        if self.get_unit([x, y]).owner != self.current_player_name:
                            attacks.append([x, y])
        return attacks


class Player:
    """ Each player of the game, which holds their units, key values and links to settlements etc"""
    def __init__(self, model_link, saved_data):
        self.model_link = model_link

        self.name = saved_data["name"]
        self.colour = saved_data["colour"]
        self.camera_focus = saved_data["camera_focus"]
        self.show_minimap = saved_data["show_minimap"]

        # Units have a shared interface for creating and loading interface, so here we satisfy the creation interface
        # with the first 3 parameters, then p[ass all the data which overrules the parameters passed.
        self.units = [Unit(unit_data["type"], unit_data["position"], unit_data["owner"], unit_data) for unit_data in saved_data["units"]]

        self.settlements = [settlement_position for settlement_position in saved_data["settlements"]]

        self.turn = saved_data["turn"]
        self.ap = saved_data["ap"]
        self.dead = saved_data["dead"]
        self.max_score = saved_data["max_score"]

    def get_save_data(self):
        return {
            "name": self.get_name(),
            "colour": self.get_colour(),
            "camera_focus": self.get_camera_focus(),
            "show_minimap": self.get_minimap_status(),

            "units": [unit.get_save_data() for unit in self.units],
            "settlements": [settlement for settlement in self.settlements],

            "turn": self.get_turn(),
            "ap": self.get_ap(),
            "dead": self.is_dead(),
            "max_score": self.get_max_score(),
        }

    def get_name(self):
        return self.name

    def is_dead(self):
        return self.dead

    def kill(self):
        self.dead = True
        self.units.clear()

    def get_colour(self):
        return self.colour

    def get_turn(self):
        return self.turn

    def get_score(self):
        # score workout =  Each city's score +  turn*5 +  each unit's health.
        score = 0
        score += self.turn * 5
        for city_position in self.settlements:
            city = self.model_link.world.get_tile(city_position)
            score += city.get_score()

        for unit in self.units:
            score += unit.health

        if score > self.max_score:
            self.max_score = score
        return score

    def get_max_score(self):
        return self.max_score

    def get_ap(self):
        return self.ap

    def get_turn_ap(self):
        ap = 0
        for city_position in self.settlements:
            city = self.model_link.world.get_tile(city_position)
            ap += city.get_ap_value()  # changed from generate_ap
        return ap

    def take_ap(self, amount):
        self.ap -= amount

    def start_turn(self):
        self.ap += self.get_turn_ap()

        # Resetting all units for new turn
        for unit in self.units:
            unit.reset()

    def end_turn(self):
        self.turn += 1

    def add_settlement(self, city_position):
        self.settlements.append(city_position)

    def remove_settlement(self, city_position):
        self.settlements.remove(city_position)

    def add_unit(self, unit):
        self.units.append(unit)

    def delete_unit(self, unit):
        self.units.remove(unit)

    def get_camera_focus(self):
        return self.camera_focus

    def set_camera_focus(self, camera_focus):
        self.camera_focus = camera_focus

    def get_minimap_status(self):
        return self.show_minimap

    def set_minimap_status(self, show):
        self.show_minimap = show


class Tile:
    def __init__(self, save_data):
        self.type = save_data["type"]
        self.position = save_data["position"]
        # self.wood, self.stone, self.metal = constants.TILE_DATA[tile_type]

    def get_save_data(self):
        return {
            "type": self.type,
            "position": self.position
        }

    def get_type(self):
        return self.type

    def get_position(self):
        return self.position

    # def take_wood(self, amount=1): # defaults, left for future in case decide change.
    #     if self.wood > 0:
    #         self.wood = self.wood - amount
    #         if self.wood < 0:
    #             self.wood = 0  # ensures resource is fully used, but cant go negative.
    #         return True
    #     return False
    #
    # def take_stone(self, amount=1):
    #     if self.stone > 0:
    #         self.stone = self.stone - amount
    #         if self.stone < 0:
    #             self.stone = 0
    #         return True
    #     return False
    #
    # def take_metal(self, amount=1):
    #     if self.metal > 0:
    #         self.metal = self.metal - amount
    #         if self.metal < 0:
    #             self.metal = 0
    #         return True
    #     return False


class City:
    def __init__(self, model_link, save_data):
        self.model_link = model_link

        self.type = save_data["type"]
        self.name = save_data["name"]
        self.position = save_data["position"]
        self.current_holder = save_data["current_holder"]
        self.level = save_data["level"]
        self.sub_level = save_data["sub_level"]
        self.max_level = save_data["max_level"]

    def get_save_data(self):
        save_data = {
          "type": self.type,
          "name": self.name,
          "position": self.position,

          "level": self.level,
          "sub_level": self.sub_level,
          "max_level": self.max_level,
        }
        if self.current_holder is not None:
            save_data["current_holder"] = self.current_holder
        else:
            save_data["current_holder"] = None

        return save_data

    def get_name(self):
        return self.name

    def get_position(self):
        return self.position

    def get_holder(self):
        return self.current_holder

    def get_type(self):
        return self.type

    def get_holder_colour(self):
        if self.current_holder is not None:
            current_holder = self.model_link.get_player(self.current_holder)
            return current_holder.get_colour()
        return None

    def get_ap_value(self, level=None):
        if level is not None:
            return level * 2
        return self.level * 2

    def get_score(self):
        return self.level * 1000

    def get_level(self):
        return self.level

    def add_level(self):  # not to be used directly, add level via add sub_level.
        self.level += 1

    def add_sub_level(self):
        current_holder = self.model_link.get_player(self.current_holder)

        current_holder.take_ap(self.get_upgrade_cost())
        self.sub_level += 1
        if not self.at_max():
            if self.sub_level == len(constants.LEVELS[self.level - 1]):
                self.add_level()
                self.sub_level = 0

    def get_upgrade_cost(self):
        return constants.LEVELS[self.level - 1][self.sub_level]

    def afford_upgrade(self):
        current_holder = self.model_link.get_player(self.current_holder)

        if current_holder.get_ap() - self.get_upgrade_cost() >= 0:
            return True
        return False

    def at_max(self):
        return self.level == self.max_level

    def change_holder(self, new_holder):
        self.current_holder = new_holder


def get_world(map_name):
    # Reading in the map from a .csv file, convert to list of strings.
    with open(paths.mapPath + map_name + ".csv", "r") as file:
        grid = file.read().split("\n")
        grid = [i.replace(",", "") for i in grid]

    # Converting for referencing as [row][col] as split by "/n" gives [col][row]
    new_grid = []
    for row in range(constants.MAP_SIZE[0]):
        new_grid.append([])
        for col in grid:
            new_grid[len(new_grid) - 1].append(col[row])

    return new_grid


class World:
    """ holds all the map tiles, be that a Tile or City, in a 2d-array """
    def __init__(self, model_link, save_data):  # __init__ creates new world or loads from save_data
        self.model_link = model_link

        self.format = save_data["format"]

        # Load Tiles
        self.tiles = []
        for row in save_data["tiles"]:  # assumes col 0, is same len as all others.
            self.tiles.append([])

            for tile_data in row:
                if tile_data["type"] == "c":
                    self.tiles[-1].append(City(self.model_link, tile_data))
                else:
                    self.tiles[-1].append(Tile(tile_data))  # tile has no additional save data

    def get_save_data(self):
        return {
            "format": self.format,
            "tiles": [[tile.get_save_data() for tile in row] for row in self.tiles]
        }

    def get_tile(self, position):
        return self.tiles[position[0]][position[1]]

    def get_format(self):
        return self.format


class Unit:
    def __init__(self, unit_type, position, owner, save_data=None):
        # UNits might be made during the game, or be loaded in.
        if save_data is None:
            self.type = unit_type
            self.position = position

            # Unit Specs
            self.max_health = constants.UNIT_SPECS[unit_type]["max_health"]
            self.health = self.max_health
            self.attack = constants.UNIT_SPECS[unit_type]["attack"]
            self.defence = constants.UNIT_SPECS[unit_type]["defence"]
            self.movement = constants.UNIT_SPECS[unit_type]["movement"]
            self.reach = constants.UNIT_SPECS[unit_type]["reach"]

            self.allowed_moves = constants.UNIT_SPECS[unit_type]["moves"]

            #  all set to True, so unit cannot act when it is spawned, must wait till next go (EFFECTIVELY BLOCKS SPAWN)
            self.moved = True
            self.attacked = True

            self.owner = owner  # TODO: getters for attributes?

        else:
            self.type = save_data["type"]
            self.position = save_data["position"]

            # Unit Specs
            self.max_health = save_data["max_health"]
            self.health = save_data["health"]
            self.attack = save_data["attack"]
            self.defence = save_data["defence"]
            self.movement = save_data["movement"]
            self.reach = save_data["reach"]

            self.allowed_moves = save_data["allowed_moves"]

            #  all set to True, so unit cannot act when it is spawned, must wait till next go (EFFECTIVELY BLOCKS SPAWN)
            self.moved = save_data["moved"]
            self.attacked = save_data["attacked"]

            self.owner = owner  # TODO: getters for attributes?

    def get_save_data(self):
        return {
            "type": self.type,
            "position": self.position,

            "max_health": self.max_health,
            "health": self.health,
            "attack": self.attack,
            "defence": self.defence,
            "movement": self.movement,
            "reach": self.reach,

            "allowed_moves": self.allowed_moves,

            "moved": self.moved,
            "attacked": self.attacked,

            "owner": self.owner,
        }

    def move(self, position):
        self.position = position
        self.moved = True

    def has_moved(self):
        return self.moved

    def has_attacked(self):
        return self.attacked

    def set_attacked(self):
        self.attacked = True

    def make_inactive(self):
        self.set_attacked()
        self.moved = True

    def reset(self):
        self.moved = False
        self.attacked = False
