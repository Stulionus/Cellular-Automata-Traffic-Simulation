import time
from model import Model

def main():
    # Configuration
    width = 100
    height = 100
    block_density = (10, 30)
    base_road_width = 2
    wide_road_width = 4
    highway_width = 6
    road_remove_probability = 0.2

    # Rename this local variable so it doesn’t shadow the time module:
    time_steps = 200

    # 1) Measure how long it takes to construct (make) the grid
    t0 = time.perf_counter()
    model = Model(
        width=width,
        height=height,
        time=time_steps,                 # pass time_steps into your Model
        road_remove_probability=road_remove_probability,
        event_chance=0.1,
        traffic_light_time=20,
        block_size_range=(10, 30)
    )
    model.make_grid()
    t1 = time.perf_counter()
    print(f"Grid creation took {t1 - t0:.4f} seconds")

    # 2) Measure how long the simulation+plotting loop takes
    t2 = time.perf_counter()
    model.simulate_w_plot()
    t3 = time.perf_counter()
    print(f"Simulation (with plotting) took {t3 - t2:.4f} seconds")

    # model.plot_traffic_heatmap()

    # model.simulate_w_plot()

if __name__ == "__main__":
    main()
