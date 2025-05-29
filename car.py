import numpy as np
import random
import math
import heapq
from grid import Grid
from cell import Cell

class Car:
    def __init__(self, car_id, start_pos, destination, city_grid, speed=1):
        self.car_id = car_id
        self.position = (start_pos[1], start_pos[0]) #x and y coordinate
        self.destination = self._select_random_destination()
        self.path_to_destination
        self.reached = False
        self.grid = city_grid
        self.speed = speed
        self.path = []

        self.parent_i = 0
        self.parent_j = 0
        self.cost = float('inf') #cost
        self.heuristic_cost = 0 #heuristic
        self.total_estimated_cost = float('inf') #cost + heuristic

    def compute_path(self):
        self.path = [self.position]
        curr_y, curr_x = self.position
        dest_y, dest_x = self.destination

        #add logic later

    #Moves car based on speed limit, traffic light, occupied cells, and road structure.
    def update(self, traffic_light_A, traffic_light_B, occupied_cells, time_step):
        if self.reached:
            return

        if not self.path:
            self.compute_path()

        current_y, current_x = self.position
        cell = self.grid.grid[current_y][current_x]
        speed = getattr(cell, 'speed_limit', self.default_speed)

        # Grid is 2D array. Grid[x][y].
        # Cell to get all cell attributes.
        for step in range(speed):  # move up to `speed` steps along path 1-3.
            next_index = time_step + step
            if next_index >= len(self.path):
                break
            next_pos = self.path[next_index]
            next_cell = self.grid.grid[y][x]
            y, x = next_pos

            # Only proceed if road & not occupied
            # Check 1. intersection 2. on or off boolean value for traffic lights
            # Check if the next grid/move is at an intersection because it will have to check at the light if it can move
            if self.cell.get_cell_type() == 'road' and (y, x) not in occupied_cells and self.cell.get_cell_type() != 'intersection':
                if self.grid.grid() == 'Off':
                    break
                else:
                    self.position = next_pos
                    occupied_cells.add(self.position)

        self.time_spent += 1
        if self.position == self.destination:
            self.reached = True

    
    # is_within_grid: checks if a cell is within the grid coordinates and whether the current
    # cell is unblocked. Unblocked is set to 1 and Blocked is set to -1.
    # A* Search Starts Below
    def is_within_grid(row, col):
        return (row >= 0) and (row <= ROW) and (col >= 0) and (col < COLUMN) and grid[row][col] == 1
    
    def is_destination(row, col, destination):
        return row == destination[0] and col == destination[1]
    
    #heuristic is calculated using euclidean distance to destination
    def calculate_heuristic_value(row, col, destination):
        return ((row - destination[0]) ** 2 + (col - destination[1]) ** 2) ** 0.5

    # helper function. returns path from destination back to source
    def trace_path(self, cell_details, destination):
    path = []
    row, col = destination
    while not (cell_details[row][col].parent_i == row and cell_details[row][col].parent_j == col):
        path.append((row, col))
        row, col = cell_details[row][col].parent_i, cell_details[row][col].parent_j
    path.append((row, col))
    path.reverse()
    return path

    
    def a_star_search(grid, source, destination):
        # first checks whether destination or source coordinates are within the grid and valid
        if not is_within_grid(source[0], source[1]) or not is_within_grid(destination[0], destination[1]):
            print("Cell.py: a_star_search: source or desination coordinates is invalid")
            return
        if is_destination(source[0], source[1], destination):
            print("Cell.py: a_star_search: destination has already been arrived")
            return
        
        #Closed: all nodes that has been visited and no longer will be revisited
        #Cell Details: details of parent info, cost, heuristics, 
        closed_list = [[False for _ in range(COLUMN)] for _ in range (ROW)]
        cell_details = [[Cell() for _ in range(COLUMN)] for _ in range (ROW)]

        i = source[0]
        j = source[1]
        cell_details[i][j].total_estimated_cost = 0
        cell_details[i][j].cost = 0
        cell_details[i][j].heuristic_cost = 0
        cell_details[i][j].parent_i = i
        cell_details[i][j].parent_j = j

        to_be_visited = []
        heapq.heappush(to_be_visited, (0.0, i , j))
        found_destination = False

        #Marks cells as visited
        while len(to_be_visited) > 0:
            to_remove = heapq.heappop(to_be_visited)
            i = to_remove[1]
            j = to_remove[2]
            closed_list[i][j] = True

        #Check if it is a road type.
