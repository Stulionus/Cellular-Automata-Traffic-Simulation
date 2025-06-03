class Cell:
    def __init__(self, x, y, cell_type, intersections):
        self.x = x
        self.y = y

        # Determine if the cell is an intersection
        if 0 <= y < intersections.shape[0] and 0 <= x < intersections.shape[1] and intersections[x, y]:
            self.cell_type = 3
        else:
            self.cell_type = cell_type

        self.canMove = []
        self.OnOrOff = False  # Traffic light state: True = green, False = red

        # Occupancy tracking
        self.occupied = False  # True if a car is in the cell or it's a red-light intersection
        self.occupied_by_car = False

        # Car time tracking
        self.time_spent_log = []
        self.total_cars_passed = 0

    # --- Getters & state togglers ---
    def getCellType(self):
        return self.cell_type

    def getOnOrOff(self):
        return self.OnOrOff

    def isOccupied(self):
        return self.occupied

    def setOnOrOff(self, switch):
        """Set traffic light state: True = green, False = red."""
        if self.cell_type == 3:
            self.OnOrOff = switch
            # Update occupancy depending on light state
            if switch:  # Green light
                if not self.occupied_by_car:
                    self.occupied = False
            else:  # Red light
                self.occupied = True

    def switch_traffic_light(self):
        """Toggle the traffic light state and update occupancy accordingly."""
        self.OnOrOff = not self.OnOrOff
        if self.cell_type == 3:
            if self.OnOrOff:  # Green
                if not self.occupied_by_car:
                    self.occupied = False
            else:  # Red
                self.occupied = True

    # --- Car movement & occupancy ---
    def car_enters(self):
        """Call when a car enters the cell."""
        #print("car enters at", self.x, self.y)
        self.occupied = True
        self.occupied_by_car = True

    def leaving(self):
        """Call when a car leaves the cell. Clears occupancy only if light is green."""
        self.occupied_by_car = False
        if self.cell_type != 3 or self.OnOrOff:  # Either not an intersection or light is green
            self.occupied = False

    # --- Car movement logic ---
    def addMove(self, move):
        self.canMove.append(move)

    def getPossibleMoves(self):
        return self.canMove

    # --- Car time tracking ---
    def addTimeSpent(self, time_spent):
        self.time_spent_log.append(time_spent)
        self.total_cars_passed += 1

    def getTimeLog(self):
        return self.time_spent_log

    def getTotalCarsPassed(self):
        return self.total_cars_passed

    # --- Move calculation ---
    def addPossibleMoves(self, city, intersections, horizontal, vertical):
        x, y = self.x, self.y
        grid = city.grid

        def in_bounds(x_, y_):
            return 0 <= x_ < grid.shape[1] and 0 <= y_ < grid.shape[0]

        def is_road(x_, y_):
            return in_bounds(x_, y_) and (horizontal[y_, x_] or vertical[y_, x_])

        def is_intersection(x_, y_):
            return in_bounds(x_, y_) and intersections[y_, x_]

        # Initialize travel_dir
        self.travel_dir = None

        # Determine road direction
        if self.cell_type == 1:  # Horizontal
            if y > 0 and horizontal[y - 1, x]:  # bottom lane → eastbound
                self.travel_dir = (1, 0)
            elif y + 1 < grid.shape[0] and horizontal[y + 1, x]:  # top lane → westbound
                self.travel_dir = (-1, 0)

        elif self.cell_type == 2:  # Vertical
            if x > 0 and vertical[y, x - 1]:  # right lane → northbound
                self.travel_dir = (0, -1)
            elif x + 1 < grid.shape[1] and vertical[y, x + 1]:  # left lane → southbound
                self.travel_dir = (0, 1)

        # Add forward move
        if self.travel_dir:
            dx, dy = self.travel_dir
            fx, fy = x + dx, y + dy
            if in_bounds(fx, fy) and is_road(fx, fy):
                self.addMove((dx, dy))
            else:
                # Border detected — allow U-turn to opposite lane and reverse direction
                if self.cell_type == 1:
                    # Horizontal road U-turn
                    if dy == 0:
                        ny = y - 1 if dx == 1 else y + 1  # move to opposite horizontal lane
                        ndx = -dx  # reverse direction
                        if in_bounds(x, ny) and horizontal[ny, x]:
                            self.addMove((0, ny - y))  # shift lanes vertically
                            self.addMove((ndx, 0))     # reverse direction

                elif self.cell_type == 2:
                    # Vertical road U-turn
                    if dx == 0:
                        nx = x - 1 if dy == 1 else x + 1  # move to opposite vertical lane
                        ndy = -dy  # reverse direction
                        if in_bounds(nx, y) and vertical[y, nx]:
                            self.addMove((nx - x, 0))     # shift lanes horizontally
                            self.addMove((0, ndy))        # reverse direction

        elif self.cell_type == 3:
            # Intersection — allow movement in any connected direction
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if in_bounds(nx, ny) and (horizontal[ny, nx] or vertical[ny, nx] or intersections[ny, nx]):
                    self.addMove((dx, dy))
