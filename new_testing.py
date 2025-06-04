from grid import Grid
from model import Model
from visualizer import Visualizer

grid = Grid(100,100,road_remove_probability = 0.1, 
                 event_chance = 0.1, 
                 highway_amount=1,
                 medium_road_amount=3,
                 cars_prob= 0.01)
model = Model(time= 200, traffic_light_time = 2)
model.grid = grid #grid.cell
model.time_step = 0

print(grid.cars)
grid.plot_cars()
grid.switch_traffic_light()
grid.plot_occupied()

NUM_STEPS = 200

for step in range(NUM_STEPS):
    print("Time Step: ", {step})
    for car in grid.cars:
        print('---')
        print(f"Car {car.car_id} Start: {car.source}, Destination: {car.destination}")
        
        if car.path_not_found_count > 0:
            print(f"Car {car.car_id}: Path not found {car.path_not_found_count} time(s)")
        
        if not car.reached:
            car.update(step)
            y, x = car.position #here
            grid.cells[y][x].addTimeSpent(1)
            print(f"Updated Position: {car.position}")
            print(f"  Cell ({y}, {x}) → Time spent log: {grid.cells[y][x].time_spent_log}, Total cars passed: {grid.cells[y][x].total_cars_passed}")
        else:
            print(f"Car {car.car_id} has reached its destination.")


    if model.time_step % model.traffic_light_time == 0:
        for row in model.grid.cells: #model.grid:
            for cell in row:
                if cell.getCellType() == 3:
                    cell.switch_traffic_light()
    model.time_step += 1

    failed_count = sum(1 for car in grid.cars if car.path_not_found_count > 0)
    print(f"\nTotal Cars with Pathfinding Failures: {failed_count}")

    print("\n--- Cars That Failed to Find a Path ---")
    for car in grid.cars:
        if car.path_not_found_count > 0:
            print(f"Car {car.car_id} | Start: {car.source} → Destination: {car.destination} | Failures: {car.path_not_found_count}")

    reached_count = sum(1 for car in grid.cars if car.reached)

    print(f"\nTotal Cars That Reached Their Destination: {reached_count}")

#Prints cell traffic summaries
for y in range(grid.height):
    for x in range(grid.width):
        cell = grid.cells[y][x]
        #if cell.total_cars_passed > 0:
            #print(f"Cell ({y},{x}) - Traffic Calculated Time: {sum(cell.time_spent_log)/cell.total_cars_passed:.2f}, Count: {cell.total_cars_passed}, Log: {sum(cell.time_spent_log)}")
#grid.plot_cars()

#print("Simulating heatmap")
#visualizer = Visualizer(grid)
#visualizer.render_traffic_heatmap()
        
# Print summary of failed pathfinding
