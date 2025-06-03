import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import grid as grid_module
from visualizer import Visualizer
import time

class Model:
    def __init__(self, 
                 height=200, 
                 width=200,
                 time=100, 
                 cars_prob=0.0, 
                 road_remove_probability=0.1,
                 event_chance=0.1,
                 traffic_light_time=10,
                 move_chance=0.9,
                 block_size_range=(10,30)
                 ):
        
        self.width = width
        self.height = height
        self.cars_prob = cars_prob
        self.time = time
        self.traffic_light_time = traffic_light_time
        self.move_chance = move_chance
        self.road_remove_probability = road_remove_probability
        self.event_chance = event_chance
        self.block_size_range = block_size_range

    def make_grid(self):
        self.grid = grid_module.Grid(
            width=self.width,
            height=self.height,
            road_remove_probability=self.road_remove_probability,
            event_chance=self.event_chance,
            cars_prob=self.cars_prob,
            block_size_range=self.block_size_range
        )

    def simulate(self):
        for i in range(self.time):
            self.grid.update(i % self.traffic_light_time == 0)

    def simulate_w_plot(self):
            self.make_grid()
            viz = Visualizer(self.grid)

            for i in range(self.time):
                toggle = (i % self.traffic_light_time == 0)
                self.grid.update(toggle)

                viz.render(show_cars=True, show_paths=False, show_occupied=False)

                time.sleep(0.2)

            plt.ioff()
            plt.show()


