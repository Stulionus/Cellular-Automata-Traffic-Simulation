import time
from model import Model

def main():
    # Configuration
    width = 200
    height = 200
    block_density = (10, 30)
    base_road_width = 2
    wide_road_width = 4
    highway_width = 6
    road_remove_probability = 0.2

    time_steps = 200

    t0 = time.perf_counter()
    model = Model(
        width=width,
        height=height,
        time=time_steps, 
        road_remove_probability=road_remove_probability,
        event_chance=0.1,
        traffic_light_time=20,
        block_size_range=(10, 30)
    )
    model.make_grid()
    t1 = time.perf_counter()
    print(f"Grid creation took {t1 - t0:.4f} seconds")

    t2 = time.perf_counter()
    # model.simulate_w_plot()
    sim_length = 100
    for i in range(sim_length):
        model.simulate()
        model.grid.reset_cars()
        print(f"Simulating: {i/sim_length*100:.2f}%", end="\r", flush=True)
    t3 = time.perf_counter()
    print(f"Simulation (with plotting) took {t3 - t2:.4f} seconds")

    model.plot_traffic_heatmap()
    model.plot_car_count_heatmap()
    # t4 = time.perf_counter()
    # model.grid.reset_cars()
    # t5 = time.perf_counter()
    # print(f"Car reset took {t5 - t4:.4f} seconds")
    # model.simulate_w_plot()

if __name__ == "__main__":
    main()
