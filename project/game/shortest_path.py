# Ben-Ryder 2019

import math

"""
A* Search Algorithm Implementation 

Adjacency list structures as:
{
"node-id": {"f": 0, "g": int, "h": int, "n": [node-id, node-id, node-id ...], 
"node-id": {"g": int, "h": int, "n": [node-id, node-id, node-id ...], 
...
}

WHERE:
g = cost to travel to node
h = heuristic to target
f = combined cost and heuristic (can be left out at declaration)
n = list of connections to other nodes.
"""


# wrapper of findPath, for the scenario of a grid map (ie 2d array, where contents denote wall or path).
# ASSUMES 0=path, 1=wall. Any extra items to act as a wall are passed in the walls list
class GridPath:
    def __init__(self, grid, start, target, walls=None):
        """ grid is 2d array. start/end are grid positions. walls is list of obstacles formats (as well as "1") """
        self.grid = grid
        self.start = start
        self.target = target
        if walls is None:
            self.walls = ["1"]
        else:
            self.walls = ["1"] + walls

        self.adjacency_list = self.construct_adjacency_list(self.grid, self.target)

    def construct_adjacency_list(self, grid, target):
        adjacency_list = {}
        for row in range(len(grid)):
            for col in range(len(grid[0])):
                if grid[row][col] not in self.walls:
                    adjacency_list[str([row, col])] = {
                        "f": 0,
                        "g": 1,
                        "h": self.get_heuristic([row, col], self.target),
                        "n": self.get_adjacent([row, col], self.grid),
                    }

        return adjacency_list

    def get_adjacent(self, point, grid):
        all_neighbours = [
            [point[0], point[1] - 1],  # above tile
            [point[0] + 1, point[1]],  # right tile
            [point[0], point[1] + 1],  # below tile
            [point[0] - 1, point[1]],  # left tile
        ]  # no diagonal movement allowed

        # remove neighbours if position is off grid edge, or can't move into it.
        filtered_neighbours = [str([row, col]) for row, col in all_neighbours
                               if row in range(0, len(grid))
                               if col in range(0, len(grid[0]))
                               if grid[row][col] not in self.walls]
        return filtered_neighbours

    def get_heuristic(self, start, end):
        """ start and end = [int, int] """
        x_distance = abs(start[0] - end[0])
        y_distance = abs(start[1] - end[1])
        return round(math.sqrt(x_distance ** 2 + y_distance ** 2))

    def get_path(self):
        return FindPath(self.adjacency_list, self.start, self.target).get_path()


class FindPath:
    def __init__(self, adjacency_list, start, target):
        self.adjacency_list = adjacency_list  # used to look up neighbours

        self.start = str(start)
        self.target = str(target)

        self.current_node = None
        self.closed_nodes = []
        self.open_nodes = []
        self.path = None

        self.run()

    def run(self):
        self.open_nodes.append(self.start)

        while len(self.open_nodes) > 0:

            self.current_node = self.open_nodes[0]
            self.open_nodes.remove(self.current_node)
            self.closed_nodes.append(self.current_node)

            if self.current_node == self.target:
                self.construct_path()

            children = self.adjacency_list[self.current_node]["n"]
            for child in children:
                if child not in self.closed_nodes:
                    self.adjacency_list[child]["g"] += self.adjacency_list[self.current_node]["g"]
                    self.adjacency_list[child]["f"] = self.adjacency_list[child]["g"] + self.adjacency_list[child]["h"]
                    self.adjacency_list[child]["next_step"] = self.current_node

                    if child not in self.open_nodes:
                        if self.adjacency_list[child]["g"] > self.adjacency_list[self.current_node]["g"]:
                            self.open_nodes.append(child)

    def construct_path(self):
        self.path = []
        current = self.current_node
        while current != self.start:
            self.path.append(eval(current))
            current = self.adjacency_list[current]["next_step"]

        self.path = self.path[::-1]

    def get_path(self):
        return self.path  # returns None if path doesnt exist
