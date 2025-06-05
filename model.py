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
                 road_remove_probability=0.1,
                 event_chance=0.1,
                 traffic_light_time=10,
                 move_chance=0.9,
                 block_size_range=(10,30),
                 ):
        
        self.width = width
        self.height = height
        self.num_cars=num_cars
        self.time = time
        self.traffic_light_time = traffic_light_time
        self.road_remove_probability = road_remove_probability
        self.event_chance = event_chance
        self.block_size_range = block_size_range
        self.highway_amount = highway_amount
        self.medium_road_amount = medium_road_amount
        self.move_chance = move_chance


    def make_grid(self):
        """
        Create and assign a new Grid object to this Model.

        This method instantiates a Grid from the grid_module with the model's
        parameters). After calling this method, self.grid will hold a fully constructed Grid
        ready for simulation.
        """
        self.grid = grid_module.Grid(
            width=self.width,
            height=self.height,
            num_cars=self.num_cars,
            road_remove_probability=self.road_remove_probability,
            highway_amount=self.highway_amount,
            medium_road_amount=self.medium_road_amount,
            event_chance=self.event_chance,
            block_size_range=self.block_size_range,
            move_chance=self.move_chance
        )

    def reset_cars(self):
            """
            Reset all cars in the current grid to their initial state.

            This method calls the Grid.reset_cars() function, which generate a new list 
            of cars at new random positions and assigns them to the grid.
            """
            self.grid.reset_cars()

    def simulate(self, car_stats=True):
        """
        Run a traffic simulation for the configured number of time steps without visualization.

        For each time step:
          - Toggle traffic lights if the current step is a multiple of traffic_light_time.
          - Update the grid (move cars)
          - Collect car movement information.

        After all time steps:
          - Compute how many cars reached their destination.
          - If car_stats is True, print the total number of cars that reached and,
            for each car, its final path index and total time spent.

        Parameters:
            car_stats (bool): If True, print per-car statistics at the end of the run.
        """
        for i in range(self.time):
            toggle = (i % self.traffic_light_time == 0)
            self.grid.update(toggle, current_step=i)

            for car in self.grid.cars:
                cid = car.car_id
                if self.grid.car_dist[cid] is None:

                    self.grid.car_dist[cid] = car.path_index
                    self.grid.car_time[cid] = car.time_spent

        num_reached = sum(1 for car in self.grid.cars if car.reached)
        total_cars = len(self.grid.cars)

        if car_stats:
            print(f"Simulation complete. {num_reached} out of {total_cars} cars reached destination.")
            for car in self.grid.cars:

                path_index = car.path_index
                time_spent = car.time_spent
                print(f"  Car {car.car_id}: Path Index = {path_index}, Time Spent = {time_spent}")
                #print(f"  Car {car.car_id}: distance traveled = {dist}, time steps = {tsteps}")

    def simulate_w_plot(self, car_stats=False):
        """
        Run a traffic simulation with a live visualization.

        This method creates a Visualizer for the current grid. For each time step:
          - Toggle traffic lights if needed.
          - Update the grid state.
          - Render the grid, showing cars but hiding their full paths and occupancy details.
          - Pause briefly (0.01 seconds) to animate the update.

        After simulation:
          - Turn off interactive plotting and show the final static image.
          - Record any cars that did not reach their destination.
          - If car_stats is True, print per-car statistics and the total reached count.

        Parameters:
            car_stats (bool): If True, print per-car statistics at the end of the run.
        """
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
                path_index = car.path_index
                time_spent = car.time_spent
                print(f"  Car {car.car_id}: Path Index = {path_index}, Time Spent = {time_spent}")
                #print(f"  Car {car.car_id}: distance traveled = {dist}, time steps = {tsteps}")
            print(f"Simulation (with plot) complete. {num_reached} out of {total_cars} cars reached destination.")

        
    def run_many_sims(self, num_sims=100):
        """
        Execute multiple back‐to‐back simulations and report aggregated statistics.

        For each of num_sims iterations:
          - Run a single simulation (without per-step printing).
          - Compute each car’s distance traveled (path_index) and record the average.
          - Count how many cars reached their destination.
          - Reset the grid’s cars before the next simulation.
          - Print a progress percentage in‐place.

        After all simulations:
          - Print the total elapsed wall‐clock time for all runs.
          - Print the average number of cars that reached their destination and
            the average distance traveled per car.

        Parameters:
            num_sims (int): Number of independent simulations to run.
        """
        cars_reached_per_sim = []
        avg_distance_per_sim = []

        start_time = time.perf_counter()

        for sim_index in range(num_sims):
            self.simulate(car_stats=False)

            # Collect distance traveled for each car (path_index > 0)
            distances = [car.path_index for car in self.grid.cars if car.path_index > 0]
            average_distance = np.mean(distances) if distances else 0.0
            avg_distance_per_sim.append(average_distance)

            # Count how many cars reached their destination
            num_cars_reached = sum(1 for car in self.grid.cars if car.reached)
            cars_reached_per_sim.append(num_cars_reached)

            # Reset the grid and cars for the next simulation
            self.grid.reset_cars()

            print(f"Simulating: {sim_index / num_sims * 100:.2f}%", end="\r", flush=True)

        end_time = time.perf_counter()

        # Final statistics over all simulations
        avg_cars_reached = np.mean(cars_reached_per_sim)
        avg_distance_traveled = np.mean(avg_distance_per_sim)
        total_cars = self.num_cars  # consistent with init

        print("\n")
        print(f"Total simulation time: {end_time - start_time:.2f} seconds")
        print(f"Average number of cars that reached destination: {avg_cars_reached:.2f} out of {total_cars}")
        print(f"Average distance traveled per car over {num_sims} simulations: {avg_distance_traveled:.2f}")

        # Optional visualizations
        #self.plot_traffic_heatmap()
        #self.plot_car_count_heatmap()
        
    def plot_traffic_heatmap(self):
        """
        Display a heatmap representing traffic density over the grid.

        This method instantiates a Visualizer for the current grid and calls
        its render_traffic_heatmap() function, which renders a color‐coded map
        indicating how often each cell was occupied by a car during the last run.
        """
        viz = Visualizer(self.grid)
        viz.render_traffic_heatmap()
        plt.ioff()
        plt.show()

    def plot_car_count_heatmap(self):
        """
        Display a heatmap representing the number of cars that passed through each cell.

        This method creates a Visualizer for the current grid and calls
        render_car_count_heatmap(), which shows how many unique cars visited each cell.
        """
        viz = Visualizer(self.grid)
        viz.render_car_count_heatmap()
        plt.ioff()
        plt.show()

    def plot_car_time_heatmap(self):
        """
        Display a heatmap representing average time spent by cars in each cell.

        This method uses a Visualizer to render a map where each cell’s color intensity
        corresponds to the average time cars spent occupying that cell during the last run.
        """
        viz = Visualizer(self.grid)
        viz.render_avg_time_heatmap()
        plt.ioff()
        plt.show()

    def run_many_sims_collect_times(self, num_sims=100):
        """
        Run multiple simulations and collect arrival times for cars that reached their destination.

        For each of num_sims iterations:
          1. Run a single simulation (suppressing per‐car output).
          2. Append each reached car’s time_spent to a master list.
          3. Reset the grid’s cars before the next iteration.
          4. Print a progress indicator in‐place.

        After all runs:
          - Print the total wall‐clock time and the total number of collected times.
          - Compute and print the average arrival time across all reached cars.
          - Return the average arrival time. If no cars reached in any run, returns NaN.

        Parameters:
            num_sims (int): Number of independent simulations to collect data from.

        Returns:
            float: The average arrival time across all cars that reached their destination.
        """
        all_reached_times = []
        t0 = time.perf_counter()

        for sim_idx in range(num_sims):

            self.simulate(car_stats=False)

            for car in self.grid.cars:
                if car.reached:
                    all_reached_times.append(car.time_spent)

            self.grid.reset_cars()

            print(f"  [Collect] sims run: {sim_idx+1}/{num_sims}", end="\r", flush=True)

        t1 = time.perf_counter()
        print(
            f"\n  → Completed collection of {num_sims} sims in {t1 - t0:.2f}s, "
            f"gathered {len(all_reached_times)} reached‐times."
        )

        if not all_reached_times:
            return float('nan')

        avg_time = np.mean(all_reached_times)
        print(f"  → Average arrival time over all reached cars: {avg_time:.2f} steps")
        return avg_time
