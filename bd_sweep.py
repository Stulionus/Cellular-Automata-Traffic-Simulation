# block_sweep.py

import time
import numpy as np
import matplotlib.pyplot as plt

from model import Model

def sweep_block_densities(
    width,
    height,
    num_cars,
    highway_amount,
    medium_road_amount,
    road_remove_probability,
    event_chance,
    traffic_light_time,
    time_steps,
    block_density_values,
    sims_per_setting
):
    """
    For each block_size_range in `block_density_values`, build a Model, call make_grid(),
    then call model.run_many_sims_collect_times(sims_per_setting), which returns the average
    arrival time. Return (block_density_values, list_of_average_times).
    """
    avg_times_list = []

    for bd in block_density_values:
        print(f"\n=== Block Density = {bd} ===")
        # 1) Instantiate Model with this block_density
        model = Model(
            width=width,
            height=height,
            num_cars=num_cars,
            highway_amount=highway_amount,
            medium_road_amount=medium_road_amount,
            time=time_steps,
            road_remove_probability=road_remove_probability,
            event_chance=event_chance,
            traffic_light_time=traffic_light_time,
            block_size_range=bd
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

    return block_density_values, avg_times_list


def main():
    # —––––– CONFIGURATION —–––––  
    width  = 100
    height = 100
    num_cars = 20
    highway_amount = 1
    medium_road_amount = 3
    road_remove_probability = 0.2
    event_chance = 0.1
    traffic_light_time = 10
    time_steps = 500

    # Define the block densities to sweep over as (min_block, max_block)
    block_density_values = [
        (30, 35),
        (25, 30),
        (20, 25),
        (15, 20),
        (10, 15),
        (5, 10),
        (1, 5),
    ]
    sims_per_setting = 20  # run 10 simulations per block_density

    t0 = time.perf_counter()
    x_vals, y_vals = sweep_block_densities(
        width = width,
        height = height,
        num_cars = num_cars,
        highway_amount = highway_amount,
        medium_road_amount = medium_road_amount,
        road_remove_probability = road_remove_probability,
        event_chance = event_chance,
        traffic_light_time = traffic_light_time,
        time_steps = time_steps,
        block_density_values = block_density_values,
        sims_per_setting = sims_per_setting
    )
    t1 = time.perf_counter()

    print(f"\nCompleted full sweep in {t1 - t0:.2f} seconds.\n")

    # Plot the result: label x-axis by stringified block densities
    labels = [f"{bd[0]}–{bd[1]}" for bd in x_vals]
    plt.figure(figsize=(8, 5))
    plt.plot(labels, y_vals, marker='o', linestyle='-')
    plt.xlabel("Block Density (min–max)")
    plt.ylabel("Average Arrival Time (steps)")
    plt.title("Avg. Car Arrival Time vs. Block Density")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
