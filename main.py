from roads import City
import time

def main():
    # Configuration
    width = 200
    height = 200
    block_density = (10, 30)
    base_road_width = 2
    wide_road_width = 4
    highway_width = 6
    road_remove_probability = 0.2

    start = time.time()
    # Create city instance
    city = City(
        width=width,
        height=height,
        block_size_range=block_density,
        base_road_width=base_road_width,
        wide_road_width=wide_road_width,
        highway_width=highway_width,
        road_remove=road_remove_probability
    )
    time.sleep(1)
    end = time.time()

    print(f"Total runtime of the program is {end - start} seconds")
    # Generate roads and plot the result
    city.generateRoads()
    city.plot_city_grid()
    city.animate_traffic(10,1)

    

if __name__ == "__main__":
    main()
