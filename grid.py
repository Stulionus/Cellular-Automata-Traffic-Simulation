import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt

from roads import City
from cell import Cell
from car import Car

class Grid:
    def __init__(self, 
                 width, 
                 height, 
                 road_remove_probability=0.1, 
                 event_chance=0.1, 
                 cars_prob=0.01):

        self.cells = [[None for _ in range(width)] for _ in range(height)]

        self.width = width
        self.height = height
        block_density = (10, 30)
        base_road_width = 2
        wide_road_width = 4
        highway_width = 6
        self.road_remove_probability = road_remove_probability
        self.even_chance = event_chance
        self.cars = []

        self.city = City(
            width=self.width,
            height=self.height,
            block_size_range=block_density,
            base_road_width=base_road_width,
            wide_road_width=wide_road_width,
            highway_width=highway_width,
            road_remove=self.road_remove_probability
        )

        local_coords = np.argwhere(self.city.grid == 2)

        self.city.generateRoads()
        self.roadsToGrid()

        #-------------------------------------------------------------------------------
        # Keep this here please this will be the final version
        # the one with num_cars is only being used for testing
        #-------------------------------------------------------------------------------
        # for row in self.cells:
        #     for cell in row:Add commentMore actions
        #         if cell and cell.cell_type == 2:
        #             if np.random.rand() < cars_prob:
        #                 cid = len(self.cars)
        #                 start = (cell.x, cell.y)
        #                 if len(local_coords) > 0:
        #                     y, x = local_coords[np.random.choice(len(local_coords))]
        #                     dest = (x, y)
        #                 else:
        #                     dest = start
        #                 c = Car(cid, start, dest, self.cells)
        #                 self.cells[start[1]][start[0]].car_enters()
        #                 self.cars.append(c)

        num_cars = 1

        local_road_coords = [(cell.x, cell.y) for row in self.cells for cell in row
                     if cell is not None and isinstance(cell, Cell) and cell.getCellType() == 2]

        if num_cars > 0 and len(local_road_coords) >= 2:
            for cid in range(num_cars):
                start = local_road_coords[np.random.choice(len(local_road_coords))]
                dest = local_road_coords[np.random.choice(len(local_road_coords))]
                while dest == start:
                    dest = local_road_coords[np.random.choice(len(local_road_coords))]

                c = Car(cid, start, dest, self.cells)
                start_cell = self.cells[start[1]][start[0]]
                if start_cell is not None:
                    start_cell.car_enters()
                else:
                    print(f"Warning: Start cell at {start} is None.")

                c.compute_path() 
                #c.trace_path()
                self.cars.append(c)


    def roadsToGrid(self):
        for y in range(self.height):
            for x in range(self.width):
                value = self.city.grid[y, x]

                if value is None:
                    continue  # Not a valid road or intersection

                if self.city.intersections[y, x]:
                    cell_type = 3
                elif value in(2,4,6):
                    cell_type = value
                else:
                    cell_type = -1

                c = Cell(y, x, cell_type, self.city.intersections)
                c.addPossibleMoves(
                    self.city,
                    self.city.intersections,
                    self.city.horizontal_roads,
                    self.city.vertical_roads
                )
                if self.city.light_A[y,x]:
                    c.OnOrOff = True
                else:
                    c.OnOrOff = False

                c.occupied_by_car= False
                c.occupied = False

                self.cells[y][x] = c
                    

    def add_Random_events(self, event_chance=0.1):
        for row in self.cells:
            for c in row:
                if c and c.cell_type == 2 and np.random.rand() < event_chance:
                    c.cell_type = -1
                    self.city.grid[c.y, c.x] = -1

    def update(self, switch=False):
        self.switch_traffic_light()

    def switch_traffic_light(self):
        mask = np.ma.mask_or(self.city.light_A, self.city.light_B)
        for y, x in zip(*np.where(mask)):
            cell = self.cells[y][x]
            if cell:
                cell.switch_traffic_light()

    def plot(self):
        img = np.ones((self.height, self.width, 3), dtype=np.uint8) * 255

        for y in range(self.height):
            for x in range(self.width):
                cell = self.cells[y][x]
                if cell:
                    if cell.cell_type == 2:
                        img[y, x] = [200, 200, 200]
                    elif cell.cell_type == 4:
                        img[y, x] = [100, 100, 100]
                    elif cell.cell_type == 6:
                        img[y, x] = [0, 0, 0]
                    elif cell.cell_type == 3:
                        img[y, x] = [0, 255, 0] if cell.getOnOrOff() else [255, 0, 0]

        plt.figure(figsize=(10, 10))
        plt.imshow(img, origin='upper')
        plt.title("Grid View: Road Classes")
        plt.axis('off')
        plt.show()

    def plot_cars(self):
        img = np.ones((self.height, self.width, 3), dtype=np.uint8) * 255

        for y in range(self.height):
            for x in range(self.width):
                cell = self.cells[y][x]
                if cell:
                    if cell.cell_type == 2:
                        img[y, x] = [200, 200, 200]
                    elif cell.cell_type == 4:
                        img[y, x] = [100, 100, 100]
                    elif cell.cell_type == 6:
                        img[y, x] = [0, 0, 0]
                    elif cell.cell_type == 3:
                        img[y, x] = [0, 255, 0] if cell.getOnOrOff() else [255, 0, 0]

        for car in self.cars:
            if not car.path:
                car.compute_path()

            for (y, x) in car.path:
                img[y, x] = [173, 216, 230]

            dy, dx = car.destination
            img[dy, dx] = [128, 0, 128]

            py, px = car.position
            img[py, px] = [255, 165, 0]

        plt.figure(figsize=(10, 10))
        plt.imshow(img, origin='upper')
        plt.title("Grid with Cars and Paths")
        plt.axis('off')
        plt.show()

    def get_image(self):
        img = np.ones((self.height, self.width, 3), dtype=np.uint8) * 255

        for y in range(self.height):
            for x in range(self.width):
                cell = self.cells[y][x]
                if cell:
                    if cell.cell_type == 2:
                        img[y, x] = [200, 200, 200]
                    elif cell.cell_type == 4:
                        img[y, x] = [100, 100, 100]
                    elif cell.cell_type == 6:
                        img[y, x] = [0, 0, 0]
                    elif cell.cell_type == 3:
                        img[y, x] = [0, 255, 0] if cell.getOnOrOff() else [255, 0, 0]
        return img

    def plot_occupied(self):
        img = np.ones((self.height, self.width, 3), dtype=np.uint8) * 255

        for y in range(self.height):
            for x in range(self.width):
                cell = self.cells[y][x]
                if cell:
                    if cell.cell_type in (2, 3, 4, 6):
                        if cell.occupied:
                            img[y, x] = [255, 0, 0]
                        else:
                            img[y, x] = [169, 169, 169]

        plt.figure(figsize=(10, 10))
        plt.imshow(img, origin='upper')
        plt.title("Occupied Cells (Red)")
        plt.axis('off')
        plt.show()
