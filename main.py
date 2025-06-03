from model import Model
import time

def main():
    # Configuration
    width = 100
    height = 100
    block_density = (10, 30)
    base_road_width = 2
    wide_road_width = 4
    highway_width = 6
    road_remove_probability = 0.2
    time = 10

    model = Model(
        width=width,
        height=height,
        time=time,
        road_remove_probability=road_remove_probability,
        event_chance=0.1,
        traffic_light_time=5,
        block_size_range=(10,30)
    )
    model.make_grid()
    model.simulate_w_plot()

if __name__ == "__main__":
    main()
