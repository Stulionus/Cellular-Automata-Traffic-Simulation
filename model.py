import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import grid as grid_module

class Model:
    def __init__(self, 
                 height=200, 
                 width=200,
                 time=100, 
                 cars_prob=0.0, 
                 road_remove_probability=0.1,
                 event_chance=0.1,
                 traffic_light_time= 2,
                 current_time_step = 0,
                 traffic_light_time=10,
                 move_chance=0.9):
        
        self.width = width
        self.height = height
        self.cars_prob = cars_prob
        self.time = time
        self.traffic_light_time = traffic_light_time
        self.move_chance = move_chance
        self.road_remove_probability = road_remove_probability
        self.event_chance = event_chance

    def make_grid(self):
        self.grid = grid_module.Grid(
            width=self.width,
            height=self.height,
            road_remove_probability=self.road_remove_probability,
            event_chance=self.event_chance,
            cars_prob=self.cars_prob
        )

    def simulate(self):
        for i in range(self.time):
            self.grid.update(i % self.traffic_light_time == 0)

    def simulate_w_plot(self):
        fig, ax = plt.subplots(figsize=(8, 8))
        img = np.ones((self.height, self.width, 3), dtype=np.uint8) * 255
        im = ax.imshow(img, animated=True)
        ax.set_title("Grid Animation")
        ax.axis("off")  

        def update_plot(frame):
            self.grid.update(frame % self.traffic_light_time == 0)
            new_img = self.grid.get_image()
            im.set_array(new_img)
            return [im]

        ani = animation.FuncAnimation(fig, update_plot, frames=self.time, interval=100, blit=True)
        plt.show()

if __name__ == "__main__":
    sim = Model()
    sim.make_grid()
    sim.simulate_w_plot()

