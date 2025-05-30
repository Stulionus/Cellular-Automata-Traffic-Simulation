import numpy as np
import random
import math
import heapq
from cell import Cell

class Car:
    def __init__(self, car_id, start_pos, destination, city_grid):
        self.car_id = car_id
        self.position = (start_pos[1], start_pos[0]) #x and y coordinate of source
        self.destination = destination #x and y coordinate of destination
        self.grid = city_grid
        self.path = []
        self.reached = False
        self.time_spent = 0
        self.move_probability = .90

        #Calls the cell class in order to call cell function
        start_cell = self.grid[self.position[0]][self.position[1]]
        self.speed = start_cell.getCellType() / 2

        rows, cols = len(city_grid), len(city_grid[0])
        self.parent_i = np.full((rows, cols), -1, dtype=int)
        self.parent_j = np.full((rows, cols), -1, dtype=int)
        self.g = np.full((rows, cols), np.inf)
        self.h = np.full((rows, cols), np.inf)
        self.f = np.full((rows, cols), np.inf)

    def spawnCar(self):
        while True:
            row = random.randint(0, len(self.grid) - 1)
            col = random.randint(0, len(self.grid[0]) - 1)
            if getattr(self.grid[row][col], 'is_road', False):
                return (row, col)

    # is_within_grid: checks if a cell is within the grid coordinates and whether the current
    # cell is unblocked. Unblocked is set to 1 and Blocked is set to -1.
    def is_within_grid(self, row, col):
        return (0 <= row < len(self.grid)) and (0 <= col < len(self.grid[0])) and getattr(self.grid[row][col], 'is_road', False)

    def is_destination(self, row, col, destination):
        return row == self.destination[0] and col == self.destination[1]
        
    #heuristic is calculated using euclidean distance to destination
    def calculate_heuristic_value(self, row, col, destination):
        return ((row - self.destination[0]) ** 2 + (col - self.destination[1]) ** 2) ** 0.5
        
    #trace_path: start from destination coordinates and backtrack until you reach the source coordinates.
    #trace the parent_i and parent_j until it reaches the desination row and column, if not source, 
    #add it to the path to keep track.
    def trace_path(self, cell_details, destination):
        print("The Path: ")
        path = []
        row, col = self.destination[0], self.destination[1]

        #essentially backtracks. If the current cell is not the start cell, will keep moving backwards
        #based on the parent pointers given.
        while not (self.parent_i[row, col] == row and self.parent_j[row, col] == col):
            path.append((row, col))
            row, col = self.parent_i[row, col], self.parent_j[row, col]
        path.append((row, col))
        path.reverse()

        for p in path:
            print(p, end=" ")
        print()
        return path

    #compute_path: when called, will call a star search function that includes all helper functions
    # in order to compute the path
    def compute_path(self):
        self.path = self.a_star_search()
        
    #Cell types are going to be in cell class
    def a_star_search(self):
        ROW, COL = len(self.grid), len(self.grid[0])
        source = self.position
        destination = self.destination

        # first checks whether destination or source coordinates are within the grid and valid
        if not self.is_within_grid(source[0], source[1]) or not self.is_within_grid(destination[0], destination[1]):
            print("Car.py: a_star_search: source or destination coordinates are invalid")
            return []

        if self.is_destination(source[0], source[1]):
            print("Car.py: a_star_search: already at destination")
            return [self.position]
        
        # a* algorithm calculation --> f = g + h
        self.g[:, :] = np.inf
        self.h[:, :] = np.inf
        self.f[:, :] = np.inf
        self.parent_i[:, :] = -1
        self.parent_j[:, :] = -1

        i, j = source
        self.g[i, j] = 0
        self.h[i, j] = self.calculate_heuristic_value(i, j)
        self.f[i, j] = self.g[i, j] + self.h[i, j]
        self.parent_i[i, j] = i
        self.parent_j[i, j] = j

        open_list = [(self.f[i, j], i, j)]
        closed = np.full((ROW, COL), False, dtype=bool)

        while open_list:
            _, i, j = heapq.heappop(open_list)
            closed[i, j] = True

            for dir in [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (-1,1), (1,-1), (1,1)]:
                ni, nj = i + dir[0], j + dir[1]

                if self.is_within_grid(ni, nj):
                    if self.is_destination(ni, nj):
                        self.parent_i[ni, nj] = i
                        self.parent_j[ni, nj] = j
                        return self.trace_path()

                    if not closed[ni, nj]:
                        g_new = self.g[i, j] + 1
                        h_new = self.calculate_heuristic_value(ni, nj)
                        f_new = g_new + h_new

                        if self.f[ni, nj] > f_new:
                            self.f[ni, nj] = f_new
                            self.g[ni, nj] = g_new
                            self.h[ni, nj] = h_new
                            self.parent_i[ni, nj] = i
                            self.parent_j[ni, nj] = j
                            heapq.heappush(open_list, (f_new, ni, nj))

        print(f"Car {self.car_id}: Destination not reachable")
        return []

def update(self, traffic_light, occupied_cell, time_step):
    if self.reached:
        return
    if not self.path:
        self.compute()
    current_y, current_x = self.position
    for step in range(self.speed):
        next_index = time_step + step
        if next_index >= len(self.path):
            break

        next_pos = self.path[next_index]
        y, x = next_pos

        if not self.is_within_grid(y, x):
            break
        next_cell = self.grid[y][x]
        
        if random.random() > self.move_probability:
            break  

        if next_cell.getCellType == 3 and not next_cell.getOnOrOff(): #is an intersection and red light is False
            break

        if (y, x) in occupied_cell:
            break

        self.position = next_pos
        occupied_cell.add(self.position)

    self.time_spent += 1
    if self.position == self.destination:
        self.reached = True

