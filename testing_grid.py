from grid import Grid

grid = Grid(100,100,road_remove_probability = 0.1, 
                 event_chance = 0.1, 
                 cars_prob= 0.01)

# grid.plot()
#print(grid.cells)
print(grid.cars)
# grid.switch_traffic_light()
# grid.plot()
grid.plot_cars()
grid.switch_traffic_light()
grid.plot_occupied()