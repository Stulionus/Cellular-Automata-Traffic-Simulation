import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt

from roads import City
from cell import Cell
#from cars import car

class Grid:
    def __init__(self):
        self.cells = []
        width = 200
        height = 200
        block_density = (10, 30)
        base_road_width = 2
        wide_road_width = 4
        highway_width = 6
        road_remove_probability = 0.2

        self.city = City(
            width=width,
            height=height,
            block_size_range=block_density,
            base_road_width=base_road_width,
            wide_road_width=wide_road_width,
            highway_width=highway_width,
            road_remove=road_remove_probability
        )

        self.city.generateRoads()

        self.roadsToGrid(self.city)

        cars = []
        for cell in self.cells:
            if cell.cell_type == "road":
                #add slight chance of spawning car
                cars.append(spawnCar(cell.x, cell.y))

    def roadsToGrid(self, city):
        currentGrid = city.grid
        intersections = city.intersections
        horizontal = city.horizontal_roads
        vertical = city.vertical_roads

        for y in range(currentGrid.shape[0]):
            for x in range(currentGrid.shape[1]):
                if currentGrid[y, x] == -1:
                    continue  # Not a road

                c = Cell(x, y, currentGrid[y, x])
                c.addPossibleMoves(city, intersections, horizontal, vertical)
                self.cells.append(c)

        
