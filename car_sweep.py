# cars_sweep.py

import time
import numpy as np
import matplotlib.pyplot as plt

from model import Model

def sweep_num_cars(
    width,
    height,
    num_cars_values,
    highway_amount,
    medium_road_amount,
    road_remove_probability,
    event_chance,
    traffic_light_time,
    time_steps,
    block_size_range,
    move_chance,
    sims_per_setting
):
    """
    For each num_cars in `num_cars_values`, build a Model, call make_grid(),
    then call model.run_many_sims_collect_times(sims_per_setting), which returns
    the average arrival time. Return (num_cars_values, list_of_average_times).
    """
    avg_times_list = []

    for nc in num_cars_values:
        print(f"\n=== Num Cars = {nc} ===")
        # 1) Instantiate Model with this num_cars
        model = Model(
            width=width,
            height=height,
            num_cars=nc,
            time=time_steps,
            highway_amount=highway_amount,
            medium_road_amount=medium_road_amount,
            road_remove_probability=road_remove_probability,
            event_chance=event_chance,
            traffic_light_time=traffic_light_time,
            move_chance=move_chance,
            block_size_range=block_size_range
        )

        # 2) Build the grid once
        model.make_grid()

        # 3) Run sims_per_setting simulations, get back the average arrival time
        avg_time = model.run_many_sims_collect_times(num_sims=sims_per_setting)

        # 4) Print a message if no cars reached (avg_time == nan)
        if np.isnan(avg_time):
            print("  No cars reached destination in any of these sims.")
        else:
            print(f"  → Average arrival time over all reached cars: {avg_time:.2f} steps")

        avg_times_list.append(avg_time)

    return num_cars_values, avg_times_list


def main():
    # —––––– CONFIGURATION —–––––  
    width  = 100
    height = 100
    highway_amount = 1
    medium_road_amount = 3
    road_remove_probability = 0.2
    event_chance = 0.1
    traffic_light_time = 20
    time_steps = 600
    block_size_range = (10, 30)
    move_chance = 0.8  # fix move_chance

    # Define the num_cars values to sweep over (e.g., from 10 to 100 in steps of 10)
    num_cars_values = list(range(10, 101, 10))  # [10, 20, ..., 100]
    sims_per_setting = 30  # run 30 simulations per num_cars setting

    t0 = time.perf_counter()
    x_vals, y_vals = sweep_num_cars(
        width = width,
        height = height,
        num_cars_values = num_cars_values,
        highway_amount = highway_amount,
        medium_road_amount = medium_road_amount,
        road_remove_probability = road_remove_probability,
        event_chance = event_chance,
        traffic_light_time = traffic_light_time,
        time_steps = time_steps,
        block_size_range = block_size_range,
        move_chance = move_chance,
        sims_per_setting = sims_per_setting
    )
    t1 = time.perf_counter()

    print(f"\nCompleted full sweep in {t1 - t0:.2f} seconds.\n")

    # Plot the result
    plt.figure(figsize=(8, 5))
    plt.plot(x_vals, y_vals, marker='o', linestyle='-')
    plt.xlabel("Number of Cars")
    plt.ylabel("Average Arrival Time (steps)")
    plt.title("Avg. Car Arrival Time vs. Number of Cars")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
