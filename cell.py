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

        if self.cell_type == 3:
            # Simplified logic — example patterns
            if status['N'] in 'RI' and status['S'] in 'RI':
                self.addMove((0, -1))  # North
                self.addMove((0, 1))   # South
            if status['E'] in 'RI' and status['W'] in 'RI':
                self.addMove((1, 0))  # East
                self.addMove((-1, 0))  # West

            # T or corner logic
            if status['N'] in 'RI' and status['E'] in 'RI':
                self.addMove((0, -1))
                self.addMove((1, 0))
            if status['S'] in 'RI' and status['W'] in 'RI':
                self.addMove((0, 1))
                self.addMove((-1, 0))

        elif self.cell_type == 1 or self.cell_type == 2:
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
