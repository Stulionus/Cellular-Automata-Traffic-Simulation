class Cell:
    def __init__(self, x, y, cell_type, intersections):
        self.x = x
        self.y = y

        # Determine if the cell is an intersection
        if 0 <= y < intersections.shape[0] and 0 <= x < intersections.shape[1] and intersections[y, x]:
            self.cell_type = 3
        else:
            self.cell_type = cell_type

        self.canMove = []
        self.OnOrOff = False

        # New variables
        self.time_spent_log = []
        self.total_cars_passed = 0

    # --- Getters & state togglers ---
    def getCellType(self):
        return self.cell_type

    def setOnOrOff(self, switch):
        if self.cell_type == 3:
            self.OnOrOff = switch

    def getOnOrOff(self):
        return self.OnOrOff

    def switch_traffic_light(self):
        self.OnOrOff = not self.OnOrOff

    # --- Car movement ---
    def addMove(self, move):
        self.canMove.append(move)

    def getPossibleMoves(self):
        return self.canMove

    # --- Car time tracking ---
    def addTimeSpent(self, time_spent):
        """Records the time a car spent at this cell."""
        self.time_spent_log.append(time_spent)
        self.total_cars_passed += 1

    def getTimeLog(self):
        """Returns a list of all time durations cars spent at this cell."""
        return self.time_spent_log

    def getTotalCarsPassed(self):
        """Returns total number of cars that have passed through this cell."""
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

        def is_land(x_, y_):
            return in_bounds(x_, y_) and not (horizontal[y_, x_] or vertical[y_, x_]) and not intersections[y_, x_]

        # Directions
        directions = {
            'NW': (-1, -1), 'N': (0, -1), 'NE': (1, -1),
            'W': (-1, 0),               'E': (1, 0),
            'SW': (-1, 1),  'S': (0, 1),  'SE': (1, 1)
        }

        # Classify all 8 neighbors
        status = {}
        for d, (dx, dy) in directions.items():
            xx, yy = x + dx, y + dy
            if not in_bounds(xx, yy):
                status[d] = 'X'  # Out of bounds
            elif is_intersection(xx, yy):
                status[d] = 'I'
            elif is_road(xx, yy):
                status[d] = 'R'
            else:
                status[d] = 'L'

        def add_if_open(dx, dy):
            xx, yy = x + dx, y + dy
            if in_bounds(xx, yy):
                self.addMove((dx, dy))

        if self.cell_type == 3:
            # Simplified logic — example patterns
            if status['N'] in 'RI' and status['S'] in 'RI':
                self.addMove((0, -1))  # North
                self.addMove((0, 1))   # South
            if status['E'] in 'RI' and status['W'] in 'RI':
                self.addMove((1, 0))   # East
                self.addMove((-1, 0))  # West

            # T or corner logic
            if status['N'] in 'RI' and status['E'] in 'RI':
                self.addMove((0, -1))
                self.addMove((1, 0))
            if status['S'] in 'RI' and status['W'] in 'RI':
                self.addMove((0, 1))
                self.addMove((-1, 0))

        elif self.cell_type == 1 or self.cell_type == 2:  # 1 = horizontal, 2 = vertical
            if self.cell_type == 1:  # Horizontal road
                if status['E'] in 'RI':
                    self.addMove((1, 0))
                if status['W'] in 'RI':
                    self.addMove((-1, 0))
            if self.cell_type == 2:  # Vertical road
                if status['N'] in 'RI':
                    self.addMove((0, -1))
                if status['S'] in 'RI':
                    self.addMove((0, 1))
