import numpy as np
import random
import heapq
from cell import Cell

class Car:
    def __init__(self, car_id, start_pos, destination, city_grid):
        self.car_id = car_id
        self.source = start_pos
        self.position = (start_pos[0], start_pos[1])
        self.destination = (destination[0], destination[1])
        self.grid = city_grid
        self.path = []
        self.reached = False
        self.time_spent = 0
        self.move_probability = 0.90
        self.path_index = 0

        start_cell_type = self.grid[self.position[0]][self.position[1]].cell_type
        self.speed = start_cell_type / 2
        self.grid[self.position[0]][self.position[1]].car_enters()

        rows, cols = len(city_grid), len(city_grid[0])
        self.ROW = rows
        self.COL = cols
        self.parent_i = np.full((rows, cols), -1, dtype=int)
        self.parent_j = np.full((rows, cols), -1, dtype=int)
        self.g = np.full((rows, cols), np.inf)
        self.h = np.full((rows, cols), np.inf)
        self.f = np.full((rows, cols), np.inf)

    def spawnCar(self):
        while True:
            row = random.randint(0, self.ROW - 1)
            col = random.randint(0, self.COL - 1)
            if getattr(self.grid[row][col], 'is_road', False):
                return (row, col)

    def is_within_grid(self, row, col):
        if not (0 <= row < self.ROW and 0 <= col < self.COL):
            return False
        cell = self.grid[row][col]
        if cell is None:
            return False
        return cell.getCellType() in (2, 3, 4, 6)

    def is_destination(self, row, col):
        return row == self.destination[0] and col == self.destination[1]

    def calculate_heuristic_value(self, row, col):
        return ((row - self.destination[0]) ** 2 + (col - self.destination[1]) ** 2) ** 0.5

    def is_road_cell(self, row, col):
        cell = self.grid[row][col]
        return cell is not None and cell.getCellType() in (2, 3, 4, 6)

    def is_on_correct_lane(self, i, j, ni, nj):
        # Allow any move if current or next is an intersection
        curr_type = self.grid[i][j].getCellType()
        next_type = self.grid[ni][nj].getCellType()
        if curr_type == 3 or next_type == 3:
            return True

        # Horizontal move
        if i == ni and j != nj:
            # Find vertical extent of contiguous road cells at column j
            i_min = i_max = i
            # upward
            k = i - 1
            while k >= 0 and self.is_road_cell(k, j):
                i_min = k
                k -= 1
            # downward
            k = i + 1
            while k < self.ROW and self.is_road_cell(k, j):
                i_max = k
                k += 1

            if nj > j:
                # moving east → use bottom lane (largest row index)
                return i == i_max
            else:
                # moving west → use top lane (smallest row index)
                return i == i_min

        # Vertical move
        if j == nj and i != ni:
            # Find horizontal extent of contiguous road cells at row i
            j_min = j_max = j
            # left
            k = j - 1
            while k >= 0 and self.is_road_cell(i, k):
                j_min = k
                k -= 1
            # right
            k = j + 1
            while k < self.COL and self.is_road_cell(i, k):
                j_max = k
                k += 1

            if ni > i:
                # moving south → use left lane (smallest col index)
                return j == j_min
            else:
                # moving north → use right lane (largest col index)
                return j == j_max

        return False

    def trace_path(self):
        path = []
        row, col = self.destination
        while not (self.parent_i[row, col] == row and self.parent_j[row, col] == col):
            path.append((int(row), int(col)))
            row, col = self.parent_i[row, col], self.parent_j[row, col]
        path.append((int(row), int(col))) #change to int to output coordinates correctly
        path.reverse()
        self.path = path[1:]
        return path

    def compute_path(self):
        self.path = self.a_star_search()
        self.path = self.path[1:]

    def a_star_search(self):
        self.g[:, :] = np.inf
        self.h[:, :] = np.inf
        self.f[:, :] = np.inf
        self.parent_i[:, :] = -1
        self.parent_j[:, :] = -1

        i, j = self.position
        self.g[i, j] = 0
        self.h[i, j] = self.calculate_heuristic_value(i, j)
        self.f[i, j] = self.h[i, j]
        self.parent_i[i, j] = i
        self.parent_j[i, j] = j

        open_list = [(self.f[i, j], i, j)]
        closed = np.full((self.ROW, self.COL), False, dtype=bool)

        # Only orthogonal moves
        neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        while open_list:
            _, i, j = heapq.heappop(open_list)
            if closed[i, j]:
                continue
            closed[i, j] = True

            for di, dj in neighbors:
                ni, nj = i + di, j + dj
                if not self.is_within_grid(ni, nj):
                    continue

                # Enforce right-side driving
                if not self.is_on_correct_lane(i, j, ni, nj):
                    continue

                if self.is_destination(ni, nj):
                    self.parent_i[ni, nj] = i
                    self.parent_j[ni, nj] = j
                    return self.trace_path()

                if closed[ni, nj]:
                    continue

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

        return [self.position] if not self.reached else []

    def update(self):
        print("Current Path Length: ", len(self.path), "Current Index: ", self.path_index)
        print("Current Speed: " , self.speed)

        current_y, current_x = self.position
        current_cell = self.grid[current_y][current_x]
        
        if self.reached:
            current_cell.leaving()
            return
        if not self.path:
            self.compute_path()
            print(len(self.path))
        if self.path_index >= len(self.path):
            current_cell.leaving()
            return
        
        for _ in range(int(self.speed)):
            if self.path_index >= len(self.path):
                current_cell.leaving()
                break

            y, x = self.path[self.path_index]
            if not self.is_within_grid(y, x):
                print(f"Car {self.car_id} blocked: cell {(y, x)} out of bounds.")
                break

            next_cell = self.grid[y][x]

            # Enforce right-side driving at movement time as well
            #if not self.is_on_correct_lane(current_y, current_x, y, x):
            #    print(f"Car {self.car_id} blocked: wrong lane from {(current_y, current_x)} → {(y, x)}.")
            #    break

            if random.random() > self.move_probability:
                print(f"Car {self.car_id} hesitated due to move_probability.")
                break

            if next_cell.getCellType() == 3 and not next_cell.getOnOrOff():
                print(f"Car {self.car_id} blocked at red light at {(y, x)}.")
                break

            if next_cell.isOccupied():
                print(f"Car {self.car_id} blocked: cell {(y, x)} is occupied.")
                break

            current_cell.leaving()
            next_cell.car_enters()

            self.path_index += 1   
            self.position = self.path[self.path_index]         
                    

            current_cell = next_cell
            current_y, current_x = y, x

        self.time_spent += 1
        if self.position == self.destination:
            self.reached = True
            current_cell.leaving()
        self.position = self.path[self.path_index]
