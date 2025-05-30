import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt

from roads import City
from cell import Cell
from car import car

class Grid:
    def __init__(self, 
                 width, 
                 height, 
                 road_remove_probability = 0.1, 
                 event_chance = 0.1, 
                 cars_prob= 0.1):
        

        self.cells = [[None for _ in range(width)]for _ in range(height)]
        
        self.width = width
        self.height =  height
        block_density = (10, 30)
        base_road_width = 2
        wide_road_width = 4
        highway_width = 6
        self.road_remove_probability = road_remove_probability
        self.even_chance = event_chance
        self.cars = []

        local_coords = np.argwhere(self.city.grid == 2)

        self.city = City(
            width=self.width,
            height=self.height,
            block_size_range=block_density,
            base_road_width=base_road_width,
            wide_road_width=wide_road_width,
            highway_width=highway_width,
            road_remove=self.road_remove_probability
        )

        self.city.generateRoads()

        self.roadsToGrid(self.city)

        for row in self.cells:
            for cell in row:
                if cell and cell.cell_type == "road":
                    if np.random.rand() < cars_prob:
                        cid = len(self.cars)
                        start = (cell.x, cell.y)
                        if len(local_coords) > 0:
                            y, x = local_coords[np.random.choice(len(local_coords))]
                            dest = (x, y)
                        else:
                            dest = start

                        c = car(cid, start, dest, self)
                        self.cars.append(c)

    def roadsToGrid(self, city):
        for y in range(self.height):
            for x in range(self.width):
                if city.grid[y,x] == -1:
                    continue

                c = Cell(x, y, city.grid[y, x])
                c.addPossibleMoves(city,
                                   city.intersections,
                                   city.horizontal_roads,
                                   city.vertical_roads)

                self.cells[y][x] = c

    def add_Random_events(self, event_chance = 0.1):
        for c in self.cells:
            if c.cell_type == "road" and np.random.rand() <  event_chance:
                c.cell_type = "non-road"
                self.city.grid[c.y, c.x] = -1

    def update(self, switch = False):
        self.switch_traffic_light()
        for c in self.cells:
            if c.cell_type == "road":
                c.update()

    def switch_traffic_light(self):
        
        # for c in self.cells:
        #     if c.cell_type == "intersection":
        #         c.switch_traffic_light()