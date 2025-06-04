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
                 num_cars=20,
                 time=100, 
                 highway_amount=1,
                 medium_road_amount=3,
                 cars_prob=0.0, 
                 road_remove_probability=0.1,
                 event_chance=0.1,
                 traffic_light_time=10,
                 move_chance=0.9,
                 block_size_range=(10,30)
                 ):
        
        self.width = width
        self.height = height
        self.num_cars=num_cars
        self.cars_prob = cars_prob
        self.time = time
        self.traffic_light_time = traffic_light_time
        self.move_chance = move_chance
        self.road_remove_probability = road_remove_probability
        self.event_chance = event_chance
        self.block_size_range = block_size_range
        self.highway_amount = highway_amount
        self.medium_road_amount = medium_road_amount


    def make_grid(self):
        self.grid = grid_module.Grid(
            width=self.width,
            height=self.height,
            num_cars=self.num_cars,
            road_remove_probability=self.road_remove_probability,
            highway_amount=self.highway_amount,
            medium_road_amount=self.medium_road_amount,
            event_chance=self.event_chance,
            block_size_range=self.block_size_range
        )

    def reset_cars(self):
            self.grid.reset_cars()

    def simulate(self, car_stats=False):
        for i in range(self.time):
            toggle = (i % self.traffic_light_time == 0)
            self.grid.update(toggle, current_step=i)

            for car in self.grid.cars:
                cid = car.car_id
                if self.grid.car_dist[cid] is None:
                    # didn’t reach during the run → record whatever it has now:
                    self.grid.car_dist[cid] = car.path_index
                    self.grid.car_time[cid] = car.time_spent

        num_reached = sum(1 for car in self.grid.cars if car.reached)
        total_cars = len(self.grid.cars)

        if car_stats:
            print(f"Simulation complete. {num_reached} out of {total_cars} cars reached destination.")
            for car in self.grid.cars:
                dist = self.grid.car_dist[car.car_id]
                tsteps = self.grid.car_time[car.car_id]
                print(f"  Car {car.car_id}: distance traveled = {dist}, time steps = {tsteps}")

    def simulate_w_plot(self, car_stats=False):
        viz = Visualizer(self.grid)
        for i in range(self.time):
            toggle = (i % self.traffic_light_time == 0)
            self.grid.update(toggle, current_step=i)
            viz.render(show_cars=True, show_paths=False, show_occupied=False,
            current_step=i, total_steps=self.time)
            time.sleep(0.01)

        plt.ioff()
        plt.show()

        for car in self.grid.cars:
            cid = car.car_id
            if self.grid.car_dist[cid] is None:
                self.grid.car_dist[cid] = car.path_index
                self.grid.car_time[cid] = car.time_spent

        num_reached = sum(1 for car in self.grid.cars if car.reached)
        total_cars = len(self.grid.cars)

        if car_stats:
            for car in self.grid.cars:
                dist = self.grid.car_dist[car.car_id]
                tsteps = self.grid.car_time[car.car_id]
                print(f"Car {car.car_id}: distance traveled = {dist}, time steps = {tsteps}")
            print(f"Simulation (with plot) complete. {num_reached} out of {total_cars} cars reached destination.")

    def run_many_sims(self, num_sims=100):
        sims100average = np.array([])
        t2 = time.perf_counter()
        for i in range(num_sims):
            self.simulate()
            self.grid.reset_cars()
            print(f"Simulating: {i/num_sims*100:.2f}%", end="\r", flush=True)
            num_reached = sum(1 for car in self.grid.cars if car.reached)
            total_cars = len(self.grid.cars)
        t3 = time.perf_counter()
        print(f"Simulation (with plotting) took {t3 - t2:.4f} seconds")
        print(f"On average {sims100average:.2f} cars made it out of ")
        self.plot_traffic_heatmap()
        self.plot_car_count_heatmap()

    def plot_traffic_heatmap(self):
        viz = Visualizer(self.grid)
        viz.render_traffic_heatmap()
        plt.ioff()
        plt.show()

    def plot_car_count_heatmap(self):
        viz = Visualizer(self.grid)
        viz.render_car_count_heatmap()
        plt.ioff()
        plt.show()

    def plot_car_time_heatmap(self):
        viz = Visualizer(self.grid)
        viz.render_avg_time_heatmap()
        plt.ioff()
        plt.show()
