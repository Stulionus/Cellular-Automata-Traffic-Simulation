from grid import Grid
from model import Model

grid = Grid(100,100,road_remove_probability = 0.1, 
                 event_chance = 0.1, 
                 cars_prob= 0.01)
model = Model(time= 100, traffic_light_time = 2)

model.grid = grid.cells
model.time_step = 0

# grid.plot()
#print(grid.cells)
print(grid.cars)
# grid.switch_traffic_light()
# grid.plot()
grid.plot_cars()
grid.switch_traffic_light()
grid.plot_occupied()

NUM_STEPS = 100

for step in range(NUM_STEPS):
    print("Time Step: ", {step})
    for car in grid.cars:
        print('---')
        print(f"Car {car.car_id} Start: {car.source}, Destination: {car.destination}")
        
        '''
        if car.path and car.path_index < len(car.path):
            print(f"Next step in path: {car.path[car.path_index]}")
        else:
            print("No next step (either reached or no path).")
        '''       
        # Run the update for this time step
        if not car.reached:
            car.update()
            print(f"Updated Position: {car.position}")
        else:
            print(f"Car {car.car_id} has reached its destination.")


        if model.time_step % model.traffic_light_time == 0:
            for row in model.grid:
                for cell in row:
                    if cell.getCellType() == 3:
                        cell.switch_traffic_light()
        model.time_step += 1
      
  grid.plot_cars()

  ''' 
        start_cell = grid.cells[car.position[0]][car.position[1]]
        dest_cell = grid.cells[car.destination[0]][car.destination[1]]

        print(f"Start cell type: {start_cell.getCellType()}, Possible moves: {start_cell.getPossibleMoves()}")
        print(f"Dest cell type: {dest_cell.getCellType()}, Possible moves: {dest_cell.getPossibleMoves()}")

        car.compute_path()

        if car.path:
            print(f"Path found with {len(car.path)} steps:")
            for step in car.path:
                print(step, end=" ")
            print()
        else:
            print("No path found.")

    grid.plot_cars()

  '''
