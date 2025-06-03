import numpy as np
import matplotlib.pyplot as plt

class Visualizer:
    def __init__(self, grid):
        self.grid = grid
        plt.ion()

        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        base_img = self._build_base_image()
        self.img_plot = self.ax.imshow(base_img, origin='upper')
        self.ax.axis('off')
        plt.show()
    def _build_base_image(self):
        h, w = self.grid.height, self.grid.width
        img = np.ones((h, w, 3), dtype=np.uint8) * 255
        for y in range(h):
            for x in range(w):
                cell = self.grid.cells[y][x]
                if not cell:
                    continue
                t = cell.cell_type
                if   t == 2: img[y, x] = [200, 200, 200] 
                elif t == 4: img[y, x] = [100, 100, 100] 
                elif t == 6: img[y, x] = [0, 0, 0]  
                elif t == 3:
                    img[y, x] = [0, 255, 0] if cell.getOnOrOff() else [255, 0, 0]
        return img

    def render(self, show_cars=True, show_paths=True, show_occupied=False):

        base = self._build_base_image()

        if show_paths or show_cars:
            for car in self.grid.cars:
                if show_paths:
                    if not car.path:
                        car.compute_path()
                    for (py, px) in car.path:
                        base[py, px] = [173, 216, 230] 
                if show_cars:
                    cy, cx = car.position
                    if 0 <= cy < self.grid.height and 0 <= cx < self.grid.width:
                        base[cy, cx] = [255, 165, 0] 
                    dy, dx = car.destination
                    # if 0 <= dy < self.grid.height and 0 <= dx < self.grid.width:
                    #     base[dy, dx] = [128, 0, 128]

        if show_occupied:
            for y in range(self.grid.height):
                for x in range(self.grid.width):
                    cell = self.grid.cells[y][x]
                    if cell and cell.cell_type in (2, 3, 4, 6):
                        if cell.occupied:
                            base[y, x] = [255, 0, 0]

        self.img_plot.set_data(base)
        self.ax.set_title("Traffic Grid")
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        plt.pause(0.001)
