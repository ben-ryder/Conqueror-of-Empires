import random

import constants

import project.game.breadth_search as breadth_first
import project.game.shortest_path as shortest_path

MAP_WALLS = ["s", "l", "m", "o"]

# SPOILERS!!
# By reading this file, you can learn how the computer plays against you. This could make it easier to win against it
# and thus spoil the strategy of the game a bit. You have been warned :)


class Logic:
    def take_go(self, model):
        model.current_player.start_turn()

        self.handle_cities(model)
        self.handle_units(model)

        model.current_player.end_turn()

    def handle_cities(self, model):
        for city in model.current_player.settlements:
            # Spawning Units
            affordable_units = [name for name, values in constants.UNIT_SPECS.items()
                                if model.current_player.get_ap() - values["spawn_cost"] > 0]
            unit_choice = random.choice(affordable_units)
            model.try_spawn(unit_choice, city.get_position())

    def handle_units(self, model):
        for unit in model.current_player.units:
            if False:  # in city conquer it
                pass
            else:
                # breadth_search = breadth_first.BreadthSearch(model.world.get_format())
                #
                # nearest_city = breadth_search.get_nearest(unit.position, "c")
                # path = shortest_path.GridPath(
                #     model.world.get_format(),
                #     unit.position, nearest_city,
                #     walls=MAP_WALLS
                # ).get_path()
                # print(path)

                # See if unit can take a city
                if model.check_conquer(unit):
                    model.conquer(unit.position)
                else:
                    # Make Random Move
                    all_moves = model.get_moves(unit)
                    if len(all_moves) > 0:
                        move = random.choice(all_moves)
                        model.move_unit(move, unit)

                    # Make Random Attack (if possible)
                    all_attacks = model.get_attacks(unit)
                    if len(all_attacks) > 0:
                        all_units = sorted(
                            [model.get_unit(position) for position in all_attacks],
                            key=lambda x: x.health)
                        enemy_unit = all_units[0]  # target the weakest enemy
                        model.make_attack(unit, enemy_unit)


"""
aspects of controlling a player:

- spawning units
- moving units
- attacking units
- conquering units

- upgrade cities


Unit (that is spawned)
if in city, conquer it.

else:

- if can move into city, do so.

shortest path can be used between units and the nearest city, so allways moving towards nearest city.
(prioritise un-populated cities then the enemy).
if can move towards "nearest" city, do it.

- if enemy in range, attack it.

Upgrade and Spawn
keep a record of the players actions (ie. if they spawned units or/and upgraded a city)

try to match the number of units spawned (and type?).
then, try to match city upgrades
if left over ap:
	if big diffrence in ap per turn, apply upgrades only.
	else if big diffrence in units, spawn units.
	else
	randomly pick units, or upgrades
	apply these
	
"""