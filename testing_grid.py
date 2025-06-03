from grid import Grid
from visualizer import Visualizer
import time

grid = Grid(100, 100, road_remove_probability=0.1, event_chance=0.1, cars_prob=0.01)
viz = Visualizer(grid)

for step in range(10):
    if step % 2 == 0:
        swithc = True
    else:
        swithc = False
    grid.update(switch=swithc)
    
    
    viz.render(show_cars=True, show_paths=True, show_occupied=False)
    time.sleep(0.5)             
