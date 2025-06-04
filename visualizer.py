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
        self.grid.cars = [car for car in self.grid.cars if not car.reached]

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
                    # dy, dx = car.destination
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
        plt.pause(0.0001)


    def render_traffic_heatmap(self):
        rows, cols = self.grid.height, self.grid.width
        raw_values = np.full((rows, cols), np.nan)

        for y in range(rows):
            for x in range(cols):
                cell = self.grid.cells[y][x]
                if cell and cell.cell_type in (2, 3, 4, 6):
                    total_time = sum(cell.time_spent_log)
                    total_cars = cell.total_cars_passed

                    if total_cars > 0 and total_time > 0:
                        # throughput = total_cars / (avg_time)
                        raw_values[y, x] = (total_cars ** 2) / total_time
                    else:

                        raw_values[y, x] = 0.0


        masked = np.ma.masked_invalid(raw_values)

        cmap = plt.cm.Wistia
        cmap.set_bad(color='white') 


        if np.ma.count(masked) > 0:
            vmax = masked.max()
        else:
            vmax = 0.0

        fig, ax = plt.subplots(figsize=(10, 10))
        im = ax.imshow(
            masked,
            cmap=cmap,
            interpolation='nearest',
            origin='upper',
            vmin=0,
            vmax=vmax
        )
        cbar = fig.colorbar(im, ax=ax, shrink=0.5, pad=0.05)

        ax.set_title("Traffic Throughput Heatmap", fontsize=16)
        ax.set_xlabel("X", fontsize=12)
        ax.set_ylabel("Y", fontsize=12)
        ax.tick_params(axis='both', which='major', labelsize=10)
        ax.grid(False)
        plt.tight_layout()
        plt.show(block=True)


    def render_car_count_heatmap(self):
        rows, cols = self.grid.height, self.grid.width
        raw_values = np.full((rows, cols), np.nan)

        # 1) Fill raw_values[y, x] = number of cars that have entered this cell
        for y in range(rows):
            for x in range(cols):
                cell = self.grid.cells[y][x]
                if cell and cell.cell_type in (2, 3, 4, 6):
                    raw_values[y, x] = cell.getTotalCarsPassed()
                # else: leave as np.nan so that non‐road cells remain white

        # 2) Mask all NaNs (non‐road cells)
        masked = np.ma.masked_invalid(raw_values)

        # 3) Use the same Wistia colormap, drawing masked entries as white
        cmap = plt.cm.Wistia
        cmap.set_bad(color='white')

        # 4) Determine vmax from the valid entries
        if np.ma.count(masked) > 0:
            vmax = masked.max()
        else:
            vmax = 0.0

        # 5) Plot
        fig, ax = plt.subplots(figsize=(10, 10))
        im = ax.imshow(
            masked,
            cmap=cmap,
            interpolation='nearest',
            origin='upper',
            vmin=0,
            vmax=vmax
        )
        cbar = fig.colorbar(im, ax=ax, shrink=0.5, pad=0.05)

        ax.set_title("Cars‐Per‐Cell Heatmap", fontsize=16)
        ax.set_xlabel("X", fontsize=12)
        ax.set_ylabel("Y", fontsize=12)
        ax.tick_params(axis='both', which='major', labelsize=10)
        ax.grid(False)
        plt.tight_layout()
        plt.show(block=True)
