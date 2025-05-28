from roads import City

def main():
    # Configuration
    width = 200
    height = 200
    block_density = (10, 30)
    base_road_width = 2
    wide_road_width = 4
    highway_width = 6
    road_remove_probability = 0.2

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

    # Generate roads and plot the result
    city.generateRoads()
    city.plot_city_grid()
    city.animate_traffic(10,1)

if __name__ == "__main__":
    main()
