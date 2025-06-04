import numpy as np
import random
import heapq
from cell import Cell
import time
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
        self.left_turn_in_progress = False


        start_cell_type = self.grid[self.position[0]][self.position[1]].cell_type
        self.speed = start_cell_type / 2
        self.grid[self.position[0]][self.position[1]].car_enters(0)

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
        curr_cell = self.grid[i][j]
        next_cell = self.grid[ni][nj]
        curr_type = curr_cell.getCellType()
        next_type = next_cell.getCellType()

        dx, dy = ni - i, nj - j

        # Not at an intersection: enforce right-side lanes
        if curr_type != 3 and next_type != 3:
            if i == ni and j != nj:  # horizontal
                i_min = i_max = i
                k = i - 1
                while k >= 0 and self.is_road_cell(k, j):
                    i_min = k
                    k -= 1
                k = i + 1
                while k < self.ROW and self.is_road_cell(k, j):
                    i_max = k
                    k += 1
                return (nj > j and i == i_max) or (nj < j and i == i_min)

            elif j == nj and i != ni:  # vertical
                j_min = j_max = j
                k = j - 1
                while k >= 0 and self.is_road_cell(i, k):
                    j_min = k
                    k -= 1
                k = j + 1
                while k < self.COL and self.is_road_cell(i, k):
                    j_max = k
                    k += 1
                return (ni > i and j == j_min) or (ni < i and j == j_max)

            return False

        # At intersection: allow straight, right, and restricted left
        if curr_type == 3:
            prev_i, prev_j = self.parent_i[i, j], self.parent_j[i, j]
            if prev_i == -1 or prev_j == -1:
                return False  # no incoming direction yet

            dir_in = (i - prev_i, j - prev_j)
            dir_out = (ni - i, nj - j)

            # Define turn options using (dy, dx)
            straight_dirs = {
                (-1, 0): (-1, 0),  # from north
                (1, 0): (1, 0),    # from south
                (0, -1): (0, -1),  # from west
                (0, 1): (0, 1),    # from east
            }

            right_turns = {
                (-1, 0): (0, 1),   # from north → east
                (1, 0): (0, -1),   # from south → west
                (0, -1): (-1, 0),  # from west → north
                (0, 1): (1, 0),    # from east → south
            }

            left_turns = {
                (-1, 0): (0, -1),  # from north → west
                (1, 0): (0, 1),    # from south → east
                (0, -1): (1, 0),   # from west → south
                (0, 1): (-1, 0),   # from east → north
            }

            # Allow straight and right turns freely
            if dir_out == straight_dirs.get(dir_in) or dir_out == right_turns.get(dir_in):
                return True

            # Left turn condition: only if car is in top-right of 2x2 intersection *from its perspective*
            if dir_out == left_turns.get(dir_in):
                if dir_in == (-1, 0):  # From north
                    return (i % 2 == 0 and j % 2 == 1)
                elif dir_in == (1, 0):  # From south
                    return (i % 2 == 1 and j % 2 == 0)
                elif dir_in == (0, -1):  # From west
                    return (i % 2 == 0 and j % 2 == 0)
                elif dir_in == (0, 1):  # From east
                    return (i % 2 == 1 and j % 2 == 1)

            return False

        return True


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
        # t2 = time.perf_counter()
        full_path = self.a_star_search()
        
        if len(full_path) <= 1:
            self.reached = True
            self.path = []
        else:
            self.path = full_path[1:]
            # t3 = time.perf_counter()
            # print(f"Car {self.car_id} took {t3 - t2:.4f} seconds to compute path")
        


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

    def update(self, current_step):
        """
        current_step: integer simulation step (0, 1, 2, …).
        """
        current_y, current_x = self.position
        current_cell = self.grid[current_y][current_x]

        if self.reached:
            # If already reached, still call leaving() to free occupancy, passing current_step
            current_cell.leaving(current_step)
            return

        # Only compute a new path if needed
        if not self.path and not self.reached:
            self.compute_path()
            if self.reached or not self.path:
                # no path → leave occupancy & return
                current_cell.leaving(current_step)
                return

        if self.path_index >= len(self.path):
            current_cell.leaving(current_step)
            return

        for _ in range(int(self.speed)):
            if self.path_index >= len(self.path):
                current_cell.leaving(current_step)
                break

            y, x = self.path[self.path_index]
            if not self.is_within_grid(y, x):
                break

            next_cell = self.grid[y][x]

            # 1) Right‐side driving check
            if not self.is_on_correct_lane(current_y, current_x, y, x):
                break

            # 2) Random hesitation
            if random.random() > self.move_probability:
                break

            # 3) Red‐light check: only if approaching an intersection
            if next_cell.getCellType() == 3:
                if current_cell.getCellType() != 3 and not next_cell.getOnOrOff():
                    break

            # 4) Occupancy‐by‐another‐car check
            if next_cell.occupied_by_car:
                break

            # → Move succeeds: leave the old cell, then enter the new cell, passing current_step
            current_cell.leaving(current_step)
            next_cell.car_enters(current_step)

            self.path_index += 1
            self.position = (y, x)
            current_cell = next_cell
            current_y, current_x = y, x

        self.time_spent += 1

        if self.position == self.destination:
            self.reached = True
            current_cell.leaving(current_step)


