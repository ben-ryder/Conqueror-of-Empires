# Ben-Ryder 2019

import random
import paths
import constants

import project.game.calculations as calculations


class Model:
    """ holds all the data and interface to manipulate the game """
    def __init__(self, game_name, map_name, players):  # only when creating new game
        self.game_name = game_name
        self.map_name = map_name
        self.game_end = False

        self.players = [Player(p["name"], p["colour"]) for p in players]
        self.current_player = self.players[0]

        self.world = World(self.map_name, self.players)  # assigns settlements to players

        self.current_player.start_turn()

    def all_units(self):
        return [unit for player in self.players for unit in player.units]

    def next_turn(self):
        self.current_player.end_turn()

        # Getting new turn
        if not self.is_winner():  # if more than 1 player alive
            self.current_player = self.get_next_player()
        else:
            self.game_end = True

        self.current_player.start_turn()

    def get_next_player(self):
        valid_choice = False
        player = self.current_player
        while not valid_choice:  # wont be infinite, as to be called at least two players are left.
            if self.players.index(player) < len(self.players) - 1:
                player = self.players[self.players.index(player) + 1]
            else:
                player = self.players[0]
            valid_choice = not player.is_dead()
        return player

    def try_spawn(self, unit_type, position):
        if not self.get_unit(position):
            if self.current_player.get_ap() - constants.UNIT_SPECS[unit_type]["spawn_cost"] >= 0:
                self.current_player.add_unit(Unit(unit_type, position, self.get_current_player()))
                self.current_player.take_ap(constants.UNIT_SPECS[unit_type]["spawn_cost"])
                return True
        return False

    def make_attack(self, attacker, defender):
        attacker.set_attacked()
        killed_units = calculations.apply_attack(attacker, defender)
        for unit in killed_units:  # could be both units
            unit.owner.units.remove(unit)

    def check_conquer(self, unit):
        if (self.world.get_tile(unit.position).get_type() == "c" and
                self.world.get_tile(unit.position).get_holder() != self.get_current_player()):
            if not unit.has_moved():  # must stay in settlement for a turn cycle
                return True
        return False

    def conquer(self, position):
        settlement = self.world.get_tile(position)
        if settlement.current_holder is not None:
            settlement.current_holder.remove_settlement(settlement)

        settlement.change_holder(self.get_current_player())
        self.current_player.add_settlement(settlement)

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
        return self.current_player.get_name()  # will always end on current player, as they take last city.

    def get_current_player(self):
        return self.current_player

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
        if tile.get_type() == "c" and tile.get_holder() == self.get_current_player():
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
                        if self.get_unit([x, y]).owner != self.get_current_player():
                            attacks.append([x, y])
        return attacks


class Player:
    """ Each player of the game, which holds their units, key values and links to settlements etc"""
    def __init__(self, name, colour):
        self.name = name
        self.colour = colour
        self.camera_focus = [None, None]  # TODO: system to auto-scroll to spawn
        self.show_minimap = False

        self.units = []
        self.settlements = []

        self.turn = 0
        self.ap = 3  # initial ap, not per turn. (first turn ap = self.ap + self.get_turn_ap()
        self.dead = False
        self.max_score = self.ap

        # self.wood = 0
        # self.stone = 0
        # self.metal = 0

    # def add_wood(self, amount):
    #     self.wood += amount
    #
    # def add_stone(self, amount):
    #     self.stone += amount
    #
    # def add_metal(self, amount):
    #     self.metal += amount

    def get_name(self):
        return self.name

    def is_dead(self):
        return self.dead

    def kill(self):
        self.dead = True

    def get_colour(self):
        return self.colour

    def get_turn(self):
        return self.turn

    def get_score(self):
        # score workout =  Each city's score +  turn*5 +  each unit's health.
        score = 0
        score += self.turn * 5
        for city in self.settlements:
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
        for city in self.settlements:
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

    def add_settlement(self, reference):
        self.settlements.append(reference)

    def remove_settlement(self, reference):
        self.settlements.remove(reference)

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
    def __init__(self, tile_type, position):
        self.type = tile_type
        self.position = position
        # self.wood, self.stone, self.metal = constants.TILE_DATA[tile_type]

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
    def __init__(self, name, position):
        self.type = "c"
        self.name = name
        self.position = position
        self.current_holder = None
        self.level = 1  # score and ap generated from level
        self.sub_level = 0  # SUB LEVEL STARTS FROM 0
        self.max_level = len(constants.LEVELS)

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
            return self.current_holder.get_colour()
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
        self.current_holder.take_ap(self.get_upgrade_cost())
        self.sub_level += 1
        if not self.at_max():
            if self.sub_level == len(constants.LEVELS[self.level - 1]):
                self.add_level()
                self.sub_level = 0

    def get_upgrade_cost(self):
        return constants.LEVELS[self.level - 1][self.sub_level]

    def afford_upgrade(self):
        if self.current_holder.get_ap() - self.get_upgrade_cost() >= 0:
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
    def __init__(self, map_name, players):  # __init__ creates new world
        self.format = get_world(map_name)

        self.city_names = CityPicker()

        # Make Tiles
        self.tiles = []
        for row in range(len(self.format[0])):  # assumes col 0, is same len as all others.
            self.tiles.append([])

            for col in range(len(self.format)):
                if self.format[row][col] == "c":
                    name = self.city_names.get_new()
                    self.tiles[-1].append(City(name, [row, col]))
                else:
                    self.tiles[-1].append(Tile(self.format[row][col], [row, col]))

        # Set player spawns
        self.set_spawns(players)

    def get_tile(self, position):
        return self.tiles[position[0]][position[1]]

    def get_format(self):
        return self.format

    def set_spawns(self, players):  # only time world needs player knowledge, no link made.
        spawn_choices = [tile for row in self.tiles for tile in row if tile.type == "c"]
        for player in players:
            city = random.choice(spawn_choices)
            spawn_choices.remove(city)

            # There is a two way relationship, so both must know of each other.
            player.add_settlement(city)
            city.change_holder(player)


class CityPicker:
    """ used to randomly assign names to cities """
    def __init__(self):
        # Load Name Choices
        with open(paths.dataPath + "city_names") as file:
            self.name_choices = file.read().split("\n")

    def get_new(self):
        choice = random.choice(self.name_choices)
        self.name_choices.remove(choice)
        return choice


class Unit:
    def __init__(self, unit_type, position, owner):
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
