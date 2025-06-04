import numpy as np
import matplotlib.pyplot as plt
import random

class City:
    def __init__(self, width, height, highway_amount, medium_road_amount,
                 block_size_range=(5,10), base_road_width=2, road_remove=0.2):
        
        self.width = width
        self.height = height
        self.block_size_range = block_size_range
        self.base_road_width = base_road_width
        self.wide_road_width = 4
        self.highway_width = 6
        self.road_remove = road_remove
        self.highway_amount = highway_amount + 1
        self.medium_road_amount = medium_road_amount


        self.grid = np.full((height, width), -1.0)
        self.original_roads = np.zeros((height, width), bool)
        self.horizontal_roads = np.zeros((height, width), bool)
        self.vertical_roads   = np.zeros((height, width), bool)
        self.intersections    = np.zeros((height, width), bool)

        self.light_A = np.zeros((height, width), bool)
        self.light_B = np.zeros((height, width), bool)

    def _set_road(self, y_slice, x_slice, road_value, record_original=False):
        ys, ye = y_slice.start or 0, y_slice.stop or self.height
        xs, xe = x_slice.start or 0, x_slice.stop or self.width
        current = self.grid[ys:ye, xs:xe]
        prio   = {2:1, 4:2, 6:3}
        cur_p  = np.vectorize(prio.get)(current, 0)
        new_p  = prio.get(road_value, 0)
        if record_original:
            self.original_roads[ys:ye, xs:xe] = True
        mask = new_p > cur_p
        self.grid[ys:ye, xs:xe][mask] = road_value

    def _spaced_positions(self, length):
        pos = random.randint(*self.block_size_range)
        out = []
        while pos < length - self.base_road_width:
            out.append(pos)
            pos += random.randint(*self.block_size_range)
        return out

    def generateRoads(self):
        h_pos = self._spaced_positions(self.height)
        v_pos = self._spaced_positions(self.width)

        for y in h_pos:
            self._set_road(slice(y, y + self.base_road_width),
                           slice(0, self.width), 2, True)
            self.horizontal_roads[y:y + self.base_road_width, :] = True

        for x in v_pos:
            self._set_road(slice(0, self.height),
                           slice(x, x + self.base_road_width), 2, True)
            self.vertical_roads[:, x:x + self.base_road_width] = True

        axis = (random.choice(['h','v'])
                if h_pos and v_pos
                else ('h' if h_pos else 'v'))

        if axis == 'h':
            horizontal_highways = []
            for i in range(1, self.highway_amount): 
                y0 = random.choice(h_pos)
                horizontal_highways.append(y0)
                while y0 not in horizontal_highways:
                    y0 = random.choice(h_pos)
                start = max(0, y0 + self.base_road_width//2 - self.highway_width//2)
                end   = min(self.height, start + self.highway_width)
                y_slice = slice(start + 2, end - 2)
                self._set_road(y_slice, slice(0, self.width), 6)
                self.horizontal_roads[y_slice, :] = True

            #Amount of Horinzontal Collector Roads
            for x0 in random.sample(v_pos, min(len(v_pos), self.medium_road_amount)):
                c0 = max(0, x0 + self.base_road_width//2 - self.wide_road_width//2)
                c1 = min(self.width, c0 + self.wide_road_width)
                x_slice = slice(c0 + 1, c1 - 1)
                self._set_road(slice(0, self.height), x_slice, 4)
                self.vertical_roads[:, x_slice] = True

        else:
            vertical_highways = []
            for i in range(1, self.highway_amount):
                x0 = random.choice(v_pos)
                vertical_highways.append(x0)
                while x0 not in vertical_highways:
                    x0 = random.choice(v_pos)
                start = max(0, x0 + self.base_road_width//2 - self.highway_width//2)
                end   = min(self.width, start + self.highway_width)
                x_slice = slice(start + 2, end - 2)
                self._set_road(slice(0, self.height), x_slice, 6)
                self.vertical_roads[:, x_slice] = True

            #Amount of Vertical Collector Roads
            for y0 in random.sample(h_pos, min(len(h_pos), self.medium_road_amount)):
                c0 = max(0, y0 + self.base_road_width//2 - self.wide_road_width//2)
                c1 = min(self.height, c0 + self.wide_road_width)
                y_slice = slice(c0 + 1, c1 - 1)
                self._set_road(y_slice, slice(0, self.width), 4)
                self.horizontal_roads[y_slice, :] = True

        for y in h_pos:
            for i in range(len(v_pos) - 1):
                x1 = v_pos[i] + self.base_road_width
                x2 = v_pos[i + 1]
                seg = self.grid[y:y + self.base_road_width, x1:x2]
                if np.all(seg == 2) and random.random() < self.road_remove:
                    self.grid[y:y + self.base_road_width, x1:x2] = -1
                    self.original_roads[y:y + self.base_road_width, x1:x2] = False
                    self.horizontal_roads[y:y + self.base_road_width, x1:x2] = False

        for x in v_pos:
            for i in range(len(h_pos) - 1):
                y1 = h_pos[i] + self.base_road_width
                y2 = h_pos[i + 1]
                seg = self.grid[y1:y2, x:x + self.base_road_width]
                if np.all(seg == 2) and random.random() < self.road_remove:
                    self.grid[y1:y2, x:x + self.base_road_width] = -1
                    self.original_roads[y1:y2, x:x + self.base_road_width] = False
                    self.vertical_roads[y1:y2, x:x + self.base_road_width] = False

        self.intersections = self.horizontal_roads & self.vertical_roads
        self._assign_light_masks()


    def _assign_light_masks(self):
        h, w = self.intersections.shape
        self.light_A[:] = False
        self.light_B[:] = False
        visited = np.zeros_like(self.intersections, bool)

        for i in range(h):
            for j in range(w):
                if self.intersections[i, j] and not visited[i, j]:
                    stack = [(i, j)]
                    comp  = []
                    visited[i, j] = True
                    while stack:
                        r, c = stack.pop()
                        comp.append((r, c))
                        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                            rr, cc = r+dr, c+dc
                            if 0<=rr<h and 0<=cc<w \
                               and self.intersections[rr,cc] \
                               and not visited[rr,cc]:
                                visited[rr,cc] = True
                                stack.append((rr,cc))

                    rows = [r for r,_ in comp]
                    cols = [c for _,c in comp]
                    rmin, rmax = min(rows), max(rows)
                    cmin, cmax = min(cols), max(cols)
                    rmid = (rmin + rmax + 1)//2
                    cmid = (cmin + cmax + 1)//2

                    for r, c in comp:
                        if (r < rmid and c < cmid) or (r >= rmid and c >= cmid):
                            self.light_A[r, c] = True
                        else:
                            self.light_B[r, c] = True


    def _build_rgb(self):
        cmap = {-1:[250,250,250], 2:[180,180,180], 4:[100,100,100], 6:[0,0,0]}
        rgb = np.zeros((self.height, self.width, 3), np.uint8)
        for k,c in cmap.items():
            rgb[self.grid==k] = c
        return rgb

    def plot_city_grid(self):
        rgb = self._build_rgb()
        rgb[self.intersections] = [255,0,0]
        plt.figure(figsize=(10,10))
        plt.imshow(rgb, origin='upper')
        plt.axis('off')
        plt.show()

    def animate_traffic(self, steps, interval=0.5):
        plt.ion()
        fig, ax = plt.subplots(figsize=(10,10))
        for t in range(steps):
            base = self._build_rgb()
            if t % 2 == 0:
                base[self.light_A] = [  0,255,  0]
                base[self.light_B] = [255,  0,  0]
            else:
                base[self.light_A] = [255,  0,  0]
                base[self.light_B] = [  0,255,  0]
            ax.clear()
            ax.imshow(base, origin='upper')
            ax.axis('off')
            plt.pause(interval)
        plt.ioff()
        plt.show()
