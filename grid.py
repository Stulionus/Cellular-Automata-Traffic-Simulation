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
                 num_cars,
                 highway_amount,
                 medium_road_amount,
                 road_remove_probability=0.1, 
                 event_chance=0.1, 
                 block_size_range=(10,30),
                 move_chance=0.9,
                 ):

        self.cells = [[None for _ in range(width)] for _ in range(height)]

        self.width = width
        self.height = height
        block_density = block_size_range
        base_road_width = 2
        self.road_remove_probability = road_remove_probability
        self.even_chance = event_chance
        self.cars = []
        self.highway_amount = highway_amount
        self.medium_road_amount = medium_road_amount
        self.num_cars = num_cars
        self.move_chance = move_chance

        self.city = City(
            width=self.width,
            height=self.height,
            highway_amount=self.highway_amount,
            medium_road_amount=self.medium_road_amount,
            block_size_range=block_density,
            road_remove=self.road_remove_probability
        )

        local_coords = np.argwhere(self.city.grid == 2)

        self.city.generateRoads()
        self.roadsToGrid()


        local_road_coords = [(cell.x, cell.y) for row in self.cells for cell in row
                    if cell is not None and isinstance(cell, Cell) and cell.getCellType() == 2]

        if self.num_cars > 0 and len(local_road_coords) >= 2:
            for cid in range(self.num_cars):

                while True:
                    start = local_road_coords[np.random.choice(len(local_road_coords))]
                    dest = local_road_coords[np.random.choice(len(local_road_coords))]
                    if dest == start:
                        continue

                    c = Car(cid, start, dest, self.cells, move_chance=self.move_chance)
                    c.compute_path()

                    if c.path:
                        break

                start_cell = self.cells[start[1]][start[0]]
                if start_cell is not None:
                    start_cell.car_enters(0)
                self.cars.append(c)

        self.car_dist = [None] * len(self.cars)
        self.car_time = [None] * len(self.cars)



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

    def update(self, switch=False, current_step=1):
        if switch:
            self.switch_traffic_light()
        
        for car in self.cars:
            previous_reached = car.reached
            car.update(current_step)
            if car.reached and not previous_reached:
                self.car_dist[car.car_id] = car.path_index
                self.car_time[car.car_id] = car.time_spent

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

    def reset_cars(self):
        self.cars = []
        local_road_coords = [
            (cell.x, cell.y)
            for row in self.cells
            for cell in row
            if cell is not None and isinstance(cell, Cell) and cell.getCellType() == 2
        ]

        if self.num_cars > 0 and len(local_road_coords) >= 2:
            for cid in range(self.num_cars):
                start = local_road_coords[np.random.choice(len(local_road_coords))]
                dest = local_road_coords[np.random.choice(len(local_road_coords))]
                while dest == start:
                    dest = local_road_coords[np.random.choice(len(local_road_coords))]

                c = Car(cid, start, dest, self.cells, move_chance=self.move_chance)
                start_cell = self.cells[start[1]][start[0]]
                if start_cell is not None:
                    start_cell.car_enters(0)
                c.compute_path()
                self.cars.append(c)

        self.car_dist = [None] * len(self.cars)
        self.car_time = [None] * len(self.cars)
