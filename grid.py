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

        # Generate random car positions and assign them to the grid
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
        """
        Convert the City's numeric grid into Cell objects and store them in self.cells.

        For each position (y, x) in City.grid:
          1. Determine the cell_type based on road value or intersection mask.
          2. Instantiate a Cell with the correct type.
          3. Add possible moves (neighbors) based on City’s road topology.
          4. Set the traffic light state on intersection cells.
          5. Initialize occupancy flags for each cell.
        """
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
        """
        Randomly convert some road cells into blocked cells based on event chance.

        Parameters:
            event_chance (float): Probability that any given road cell (cell_type == 2)
                                  becomes blocked (cell_type = -1) in this update.

        Iterates over each cell:
         - If cell_type == 2 (standard road) and a random draw < event_chance,
           set cell_type to -1 and update the corresponding entry in City.grid.
        """
        for row in self.cells:
            for c in row:
                if c and c.cell_type == 2 and np.random.rand() < event_chance:
                    c.cell_type = -1
                    self.city.grid[c.y, c.x] = -1

    def update(self, switch=False, current_step=1):
        """
        Advance simulation by one time step: possibly toggle lights, then move all cars.

        Parameters:
            switch (bool): If True, toggle all traffic lights before moving cars.
            current_step (int): The current simulation time step (used by Car.update).

        Behavior:
          1. If switch is True, call switch_traffic_light() to flip all light states.
          2. For each car:
             a. Remember whether it had already reached its destination.
             b. Call car.update(current_step) to attempt a move or wait.
             c. If the car reaches destination in this step and was not previously reached,
                record its final path index and time spent.
        """
        if switch:
            self.switch_traffic_light()
        
        for car in self.cars:
            previous_reached = car.reached
            car.update(current_step)
            if car.reached and not previous_reached:
                self.car_dist[car.car_id] = car.path_index
                self.car_time[car.car_id] = car.time_spent

    def switch_traffic_light(self):
        """
        Toggle the state of all intersection traffic lights on the grid.

        Finds all positions where either light_A or light_B is True (masked).
        For each such position, retrieve the corresponding Cell and
        call its switch_traffic_light() method to flip its light state.
        """
        mask = np.ma.mask_or(self.city.light_A, self.city.light_B)
        for y, x in zip(*np.where(mask)):
            cell = self.cells[y][x]
            if cell:
                cell.switch_traffic_light()

    def plot(self):
        """
        Render a static image of the grid with road classes and intersection states.

        Creates an RGB image of shape (height, width, 3) with:
          - Light gray [200, 200, 200] for standard roads (cell_type == 2)
          - Medium gray [100, 100, 100] for medium roads (cell_type == 4)
          - Black [0, 0, 0] for highways (cell_type == 6)
          - Green [0, 255, 0] or Red [255, 0, 0] for intersection lights (cell_type == 3)
        Displays the image with matplotlib, hides axes, and adds a title.
        """
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
        """
        Render a static image showing all cars’ paths and positions on the grid.

        Steps:
          1. Create base image coloring roads and intersections exactly as in plot().
          2. For each car:
             a. Ensure its path is computed.
             b. Mark each cell in car.path with light-blue [173, 216, 230].
             c. Mark the car’s destination with purple [128, 0, 128].
             d. Mark the car’s current position with orange [255, 165, 0].
          3. Display the resulting image with matplotlib, hide axes, and add a title.
        """
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
        """
        Generate and return an RGB image of the current grid state (no cars).

        Returns:
            np.ndarray: An array of shape (height, width, 3) with:
              - White [255, 255, 255] for empty cells.
              - Light gray [200, 200, 200] for standard roads (cell_type == 2).
              - Medium gray [100, 100, 100] for medium roads (cell_type == 4).
              - Black [0, 0, 0] for highways (cell_type == 6).
              - Green [0, 255, 0] or Red [255, 0, 0] for intersections (cell_type == 3).
        """
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
        """
        Render a static image showing which cells are currently occupied by cars.

        Creates an RGB image:
          - White [255, 255, 255] for non-road or non-intersection empty cells.
          - Dark gray [169, 169, 169] for road/intersection cells that are not occupied.
          - Red [255, 0, 0] for any occupied road/intersection cell.

        Displays the image with matplotlib, hides axes, and adds a title.
        """
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
        """
        Remove all existing cars and reinitialize them at random road positions.

        Steps:
          1. Clear the self.cars list.
          2. Recompute the list of all road cell coordinates (cell_type == 2).
          3. For each car index from 0 to num_cars-1:
             a. Randomly select a start and destination road cell (ensuring they differ).
             b. Instantiate a new Car with that start/destination and compute its path.
             c. Mark the starting cell as occupied and append the car to self.cars.
          4. Reset self.car_dist and self.car_time lists to track each new car’s progress.
        """
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
