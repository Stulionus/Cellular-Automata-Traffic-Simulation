import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

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
        """
        Construct an RGB array representing static road and intersection layout.

        Returns:
            np.ndarray: A (height, width, 3) uint8 array where:
              - White [255, 255, 255] is default background.
              - Light gray [200, 200, 200] for standard roads (cell_type == 2).
              - Medium gray [100, 100, 100] for medium roads (cell_type == 4).
              - Black [0, 0, 0] for highways (cell_type == 6).
              - Green [0, 255, 0] or Red [255, 0, 0] for intersection cells (cell_type == 3),
                depending on the light state (getOnOrOff).
        """
        h, w
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

    def render(self, show_cars=True, show_paths=True, show_occupied=False,
               current_step=None, total_steps=None):
        """
        Update the displayed grid image by overlaying cars, paths, and occupancy.

        Parameters:
            show_cars (bool): If True, mark car positions in blue [0, 0, 255].
            show_paths (bool): If True, draw each car's planned path in light blue [173, 216, 230].
            show_occupied (bool): If True, mark occupied cells (road/intersection) in red [255, 0, 0].
            current_step (int or None): Current simulation step (for title). If None, omit step info.
            total_steps (int or None): Total number of steps (for title). If None, omit step info.

        Behavior:
            - Builds a fresh base image of roads/intersections each call.
            - Overlays paths and car positions for cars that have not yet reached their destinations.
            - If show_occupied is True, colors any cell with occupied==True in red.
            - Updates the displayed image data in-place.
            - Sets a title indicating "Step X / Y" if step parameters are provided.
            - Redraws and pauses briefly (0.0001s) to allow GUI update.
        """
        cars_to_draw = [car for car in self.grid.cars if not car.reached]

        base = self._build_base_image()

        if show_paths or show_cars:
            for car in cars_to_draw:
                if show_paths:
                    if not car.path:
                        car.compute_path()
                    for (py, px) in car.path:
                        base[py, px] = [173, 216, 230]
                if show_cars:
                    cy, cx = car.position
                    if 0 <= cy < self.grid.height and 0 <= cx < self.grid.width:
                        base[cy, cx] = [0, 0, 255]

        if show_occupied:
            for y in range(self.grid.height):
                for x in range(self.grid.width):
                    cell = self.grid.cells[y][x]
                    if cell and cell.cell_type in (2, 3, 4, 6):
                        if cell.occupied:
                            base[y, x] = [255, 0, 0]

        self.img_plot.set_data(base)

        if current_step is not None and total_steps is not None:
            self.ax.set_title(f"Traffic Grid  (Step {current_step+1} / {total_steps})")
        else:
            self.ax.set_title("Traffic Grid")

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        plt.pause(0.0001)



    def render_traffic_heatmap(self):
        """
        Display a heatmap showing traffic throughput at each cell.

        For each road/intersection cell:
          - Compute total_time = sum(time_spent_log).
          - Compute total_cars = total_cars_passed.
          - If total_cars > 0 and total_time > 0, set raw_values[y, x] = (total_cars^2) / total_time.
          - Otherwise, set raw_values[y, x] = 0.0.
        Non-road cells remain NaN (masked out).

        Renders a color‐mapped image (white background for NaN) with a colorbar. 
        Title: "Traffic Throughput Heatmap".
        """
        rows, cols = self.grid.height, self.grid.width
        raw_values = np.full((rows, cols), np.nan)

        for y in range(rows):
            for x in range(cols):
                cell = self.grid.cells[y][x]
                if cell and cell.cell_type in (2, 3, 4, 6):
                    total_time = sum(cell.time_spent_log)
                    total_cars = cell.total_cars_passed

                    if total_cars > 0 and total_time > 0:
                        raw_values[y, x] = (total_cars ** 2) / total_time
                    else:
                        raw_values[y, x] = 0.0

        masked = np.ma.masked_invalid(raw_values)

        cmap = LinearSegmentedColormap.from_list('LightGreenRed', ['#ccffcc', 'red'])
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
        """
        Display a heatmap of how many cars passed through each cell.

        For each road/intersection cell, raw_values[y, x] = total_cars_passed.
        Non-road cells remain NaN (masked out).

        Renders a color‐mapped image (white background for NaN) with a colorbar.
        Title: "Cars‐Per‐Cell Heatmap".
        """
        rows, cols = self.grid.height, self.grid.width
        raw_values = np.full((rows, cols), np.nan)

        for y in range(rows):
            for x in range(cols):
                cell = self.grid.cells[y][x]
                if cell and cell.cell_type in (2, 3, 4, 6):
                    raw_values[y, x] = cell.getTotalCarsPassed()

        masked = np.ma.masked_invalid(raw_values)

        cmap = LinearSegmentedColormap.from_list('GreenRed', ['#ccffcc', 'red'])
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

        ax.set_title("Cars‐Per‐Cell Heatmap", fontsize=16)
        ax.set_xlabel("X", fontsize=12)
        ax.set_ylabel("Y", fontsize=12)
        ax.tick_params(axis='both', which='major', labelsize=10)
        ax.grid(False)
        plt.tight_layout()
        plt.show(block=True)


    def render_avg_time_heatmap(self):
        """
        Display a heatmap of the average time each car spent in each cell.

        For each road/intersection cell:
          - total_time = sum(time_spent_log)
          - total_cars = total_cars_passed
          - If total_cars > 0, raw_values[y, x] = total_time / total_cars; otherwise, 0.0.
        Non-road cells remain NaN (masked out).

        Renders a color‐mapped image (white background for NaN) with a colorbar.
        Title: "Average Steps Per Car Heatmap".
        """
        rows, cols = self.grid.height, self.grid.width
        raw_values = np.full((rows, cols), np.nan)

        for y in range(rows):
            for x in range(cols):
                cell = self.grid.cells[y][x]
                if cell and cell.cell_type in (2, 3, 4, 6):
                    total_time = sum(cell.time_spent_log)
                    total_cars = cell.total_cars_passed

                    if total_cars > 0:
                        raw_values[y, x] = total_time / total_cars
                    else:
                        raw_values[y, x] = 0.0

        masked = np.ma.masked_invalid(raw_values)

        cmap = LinearSegmentedColormap.from_list('GreenRed', ['#ccffcc', 'red'])
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

        ax.set_title("Average Steps Per Car Heatmap", fontsize=16)
        ax.set_xlabel("X", fontsize=12)
        ax.set_ylabel("Y", fontsize=12)
        ax.tick_params(axis='both', which='major', labelsize=10)
        ax.grid(False)
        plt.tight_layout()
        plt.show(block=True)