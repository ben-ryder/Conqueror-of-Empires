# Ben-Ryder 2019

"""
Currently not true Breadth First Search Algorithm. It will not return a path to the target. Currently it can use a
breadth first style search to find the nearest occurrence of a value in a 2d-array grid based on a start position.
"""


class BreadthSearch:
    def __init__(self, grid):
        self.grid = grid
        self.size = [len(self.grid), len(self.grid[0])]

    def get_value(self, location):
        return self.grid[location[0]][location[1]]

    def get_nearest(self, position, target_value):
        open_queue = [position]
        closed_queue = []

        while len(open_queue) > 0:
            current_location = open_queue[0]

            # See if current location is equal to the target value
            if self.get_value(current_location) == target_value and current_location != position:
                return current_location

            # Add remaining neighbours to queue
            neighbours = self.get_neighbours(current_location)
            for location in neighbours:
                if location not in closed_queue and location not in open_queue and \
                        location[0] in range(0, self.size[0]) and \
                        location[1] in range(0, self.size[1]):  # stops infinite expansion
                    open_queue.append(location)

            closed_queue.append(open_queue.pop(0))  # close the current location

        return None  # no occurrences of the value

    def get_all(self, position, target_value):
        open_queue = [position]
        closed_queue = []
        occurrences = []

        while len(open_queue) > 0:
            current_location = open_queue[0]

            # See if current location is equal to the target value
            if self.get_value(current_location) == target_value:
                occurrences.append(current_location)

            # Add remaining neighbours to queue
            neighbours = self.get_neighbours(current_location)
            for location in neighbours:
                if location not in closed_queue and location not in open_queue and \
                        location[0] in range(0, self.size[0]) and \
                        location[1] in range(0, self.size[1]):  # stops infinite expansion
                    open_queue.append(location)

            closed_queue.append(open_queue.pop(0))  # close the current location

        return occurrences

    def get_neighbours(self, location):  # CAN RETURN LOCATIONS OUT OF RANGE.
        neighbours = []
        for x in range(location[0] - 1, location[0] + 2):
            for y in range(location[1] - 1, location[1] + 2):
                neighbours.append([x, y])
        return neighbours
