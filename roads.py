import numpy as np
import matplotlib.pyplot as plt
import random

class City:
    def __init__(self, width, height, block_size_range=(5, 10), base_road_width=2,
                 wide_road_width=4, highway_width=6, road_remove=0.2):
        self.width = width
        self.height = height
        self.block_size_range = block_size_range
        self.base_road_width = base_road_width
        self.wide_road_width = wide_road_width
        self.highway_width = highway_width
        self.road_remove = road_remove
        self.grid = np.ones((self.height, self.width)) * -1
        self.intersections = np.zeros((self.height, self.width), dtype=bool)
        self.original_roads = np.zeros((self.height, self.width), dtype=bool)

    def _set_with_intersections(self, y_slice, x_slice, road_value, record_original=False):
        ys, ye = y_slice.start or 0, y_slice.stop or self.height
        xs, xe = x_slice.start or 0, x_slice.stop or self.width
    
        current = self.grid[ys:ye, xs:xe]
        original = current.copy()
    
        is_existing_road = (original == 2) | (original == 4) | (original == 6)
    
        road_priority = {2: 1, 4: 2, 6: 3}
        get_priority = np.vectorize(lambda v: road_priority.get(v, 0))
    
        if not record_original:
            original_mask = self.original_roads[ys:ye, xs:xe]
            intersection_mask = is_existing_road & ~original_mask
        else:
            intersection_mask = is_existing_road
            self.original_roads[ys:ye, xs:xe] = True
    
        current_priority = get_priority(original)
        new_priority = road_priority.get(road_value, 0)
        upgrade_mask = new_priority > current_priority
    
        self.grid[ys:ye, xs:xe][upgrade_mask] = road_value
    
        if np.any(intersection_mask):
            for dy in range(ys, ye):
                for dx in range(xs, xe):
                    if intersection_mask[dy - ys, dx - xs]:
                        if 0 <= dy < self.height and 0 <= dx < self.width:
                            self.intersections[dy, dx] = True
    
        

    def _find_largest_gap(self, positions, length):
        positions = sorted(positions)
        positions = [0] + positions + [length]
        max_gap = 0
        best_start = 0
        for i in range(len(positions) - 1):
            gap = positions[i+1] - positions[i]
            if gap > max_gap:
                max_gap = gap
                best_start = positions[i]
        return best_start + max_gap // 2

    def generateRoads(self):
        def spaced_positions(length, min_spacing, max_spacing):
            positions = []
            pos = random.randint(min_spacing, max_spacing)
            while pos < length - self.base_road_width:
                positions.append(pos)
                step = random.randint(min_spacing, max_spacing)
                pos += step
            return positions

        horizontal_positions = spaced_positions(self.height, *self.block_size_range)
        vertical_positions = spaced_positions(self.width, *self.block_size_range)

        for y in horizontal_positions:
            self._set_with_intersections(slice(y, y+self.base_road_width), slice(0, self.width), 2, record_original=True)

        for x in vertical_positions:
            self._set_with_intersections(slice(0, self.height), slice(x, x+self.base_road_width), 2, record_original=True)

        axis = random.choice(['h', 'v']) if horizontal_positions and vertical_positions else ('h' if horizontal_positions else 'v')

        if axis == 'h':
            highway_y = random.choice(horizontal_positions)
            hy_center = highway_y + self.base_road_width // 2
            hy_start = max(0, hy_center - self.highway_width // 2)
            hy_end = min(self.height, hy_start + self.highway_width)
            self._set_with_intersections(slice(hy_start, hy_end), slice(0, self.width), 6)
            remaining = [y for y in horizontal_positions if y != highway_y]
            for y in random.sample(remaining, min(len(remaining), random.randint(1, 3))):
                col_center = y + self.base_road_width // 2
                col_start = max(0, col_center - self.wide_road_width // 2)
                col_end = min(self.height, col_start + self.wide_road_width)
                self._set_with_intersections(slice(col_start, col_end), slice(0, self.width), 4)
        else:
            highway_x = random.choice(vertical_positions)
            hx_center = highway_x + self.base_road_width // 2
            hx_start = max(0, hx_center - self.highway_width // 2)
            hx_end = min(self.width, hx_start + self.highway_width)
            self._set_with_intersections(slice(0, self.height), slice(hx_start, hx_end), 6)
            remaining = [x for x in vertical_positions if x != highway_x]
            for x in random.sample(remaining, min(len(remaining), random.randint(1, 3))):
                col_center = x + self.base_road_width // 2
                col_start = max(0, col_center - self.wide_road_width // 2)
                col_end = min(self.width, col_start + self.wide_road_width)
                self._set_with_intersections(slice(0, self.height), slice(col_start, col_end), 4)

        for y in horizontal_positions:
            for i in range(len(vertical_positions) - 1):
                x1 = vertical_positions[i] + self.base_road_width
                x2 = vertical_positions[i+1]
                segment = self.grid[y:y+self.base_road_width, x1:x2]
                if np.all(segment == 2) and random.random() < self.road_remove:
                    self.grid[y:y+self.base_road_width, x1:x2] = -1
                    self.original_roads[y:y+self.base_road_width, x1:x2] = False


        for x in vertical_positions:
            for i in range(len(horizontal_positions) - 1):
                y1 = horizontal_positions[i] + self.base_road_width
                y2 = horizontal_positions[i+1]
                segment = self.grid[y1:y2, x:x+self.base_road_width]
                if np.all(segment == 2) and random.random() < self.road_remove:
                    self.grid[y1:y2, x:x+self.base_road_width] = -1
                    self.original_roads[y1:y2, x:x+self.base_road_width] = False
        

    def plot_city_grid(self):
        color_map = {
            -1: [250, 250, 250],  # block
            2: [180, 180, 180],   # local road
            4: [100, 100, 100],   # collector road
            6: [0, 0, 0],         # highway
        }

        rgb_grid = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        for key, color in color_map.items():
            mask = self.grid == key
            rgb_grid[mask] = color

        rgb_grid[self.intersections] = [255, 0, 0]

        plt.figure(figsize=(10, 10))
        plt.imshow(rgb_grid, origin='upper')
        plt.axis('off')
        plt.show()

