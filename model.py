import numpy as np
import grid as grid

class Model:
    def __init__(self, 
                 height, 
                 width,
                 time, 
                 cars_prob, 
                 road_remove_probability = 0.1,
                 event_chance = 0.1,
                 traffic_light_time = 10,
                 move_chance = 0.9,
                 ):
        
        self.cars_prob = cars_prob
        self.time = time
        self.traffic_light_time = traffic_light_time
        self.move_chance = move_chance
        self.event_chance = event_chance

    def make_grid(self):
        self.grid = grid(
            width = self.width,
            height = self.height,    
            road_remove_probability = self.road_remove_probability,
            event_chance = self.event_chance,
            cars_prob = self.cars_prob,
        )

    def simulate(self):
        for i in range(self.time):
            self.grid.update(i % self.traffic_light_time == 0)

    def simulate_w_plot(self):
        for i in range(self.time):
            self.grid.update()
            #Visualize
