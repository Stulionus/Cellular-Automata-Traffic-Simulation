# lights_sweep.py

import time
import numpy as np
import matplotlib.pyplot as plt

from model import Model

def sweep_using_collect_times(
    width,
    height,
    num_cars,
    highway_amount,
    medium_road_amount,
    road_remove_probability,
    event_chance,
    block_size_range,
    time_steps,
    traffic_light_times,
    sims_per_setting
):
    """
    For each tlt in `traffic_light_times`, build a Model, call make_grid(),
    then call model.run_many_sims_collect_times(sims_per_setting), which now
    returns the average arrival time (float) directly. Return
    (traffic_light_times, list_of_average_times).
    """
    avg_times_list = []

    for tlt in traffic_light_times:
        print(f"\n=== Traffic‐Light Interval = {tlt} steps ===")
        # 1) Instantiate Model with this traffic_light_time
        model = Model(
            width=width,
            height=height,
            num_cars=num_cars,
            highway_amount=highway_amount,
            medium_road_amount=medium_road_amount,
            time=time_steps,
            road_remove_probability=road_remove_probability,
            event_chance=event_chance,
            traffic_light_time=tlt,
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

    return traffic_light_times, avg_times_list


def main():
    # —––––– CONFIGURATION —–––––  
    width  = 100
    height = 100
    num_cars = 20
    highway_amount = 1
    medium_road_amount = 3
    road_remove_probability = 0.2
    event_chance = 0.1
    block_size_range = (10, 30)
    time_steps = 500

    # Pick the traffic‐light intervals you want to sweep over:
    traffic_light_times = np.arange(2, 60, 2)
    sims_per_setting = 10  # run 30 simulations per traffic‐light setting

    t0 = time.perf_counter()
    x_vals, y_vals = sweep_using_collect_times(
        width = width,
        height = height,
        num_cars = num_cars,
        highway_amount = highway_amount,
        medium_road_amount = medium_road_amount,
        road_remove_probability = road_remove_probability,
        event_chance = event_chance,
        block_size_range = block_size_range,
        time_steps = time_steps,
        traffic_light_times = traffic_light_times,
        sims_per_setting = sims_per_setting
    )
    t1 = time.perf_counter()

    print(f"\nCompleted full sweep in {t1 - t0:.2f} seconds.\n")

    # Plot the result
    plt.figure(figsize=(8, 5))
    plt.plot(x_vals, y_vals, marker='o', linestyle='-')
    plt.xlabel("Traffic‐Light Interval (steps)")
    plt.ylabel("Average Arrival Time (steps)")
    plt.title("Avg. Car Arrival Time vs. Traffic‐Light Interval")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
