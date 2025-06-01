class Cell:
    def __init__(self, y, x, cell_type, intersections):
        self.y = y
        self.x = x

        # Determine if the cell is an intersection
        if 0 <= y < intersections.shape[0] and 0 <= x < intersections.shape[1] and intersections[y, x]:
            self.cell_type = 3
        else:
            self.cell_type = cell_type

        self.canMove = []
        self.OnOrOff = False  # Traffic light state: True = green, False = red

        # Occupancy tracking
        self.occupied = False
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
            if switch:
                if not self.occupied_by_car:
                    self.occupied = False
            else:
                self.occupied = True

    def switch_traffic_light(self):
        """Toggle the traffic light state and update occupancy accordingly."""
        self.OnOrOff = not self.OnOrOff
        if self.cell_type == 3:
            if self.OnOrOff:
                if not self.occupied_by_car:
                    self.occupied = False
            else:
                self.occupied = True

    # --- Car movement & occupancy ---
    def car_enters(self):
        self.occupied = True
        self.occupied_by_car = True

    def leaving(self):
        self.occupied_by_car = False
        if self.cell_type != 3 or self.OnOrOff:
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
        y, x = self.y, self.x
        grid = city.grid

        def in_bounds(y_, x_):
            return 0 <= y_ < grid.shape[0] and 0 <= x_ < grid.shape[1]

        def is_road(y_, x_):
            return in_bounds(y_, x_) and (horizontal[y_, x_] or vertical[y_, x_])

        def is_intersection(y_, x_):
            return in_bounds(y_, x_) and intersections[y_, x_]

        def is_land(y_, x_):
            return in_bounds(y_, x_) and not (horizontal[y_, x_] or vertical[y_, x_]) and not intersections[y_, x_]

        # Directions: dy, dx
        directions = {
            'NW': (-1, -1), 'N': (-1, 0), 'NE': (-1, 1),
            'W':  (0, -1),               'E':  (0, 1),
            'SW': (1, -1),  'S': (1, 0),  'SE': (1, 1)
        }

        status = {}
        for d, (dy, dx) in directions.items():
            yy, xx = y + dy, x + dx
            if not in_bounds(yy, xx):
                status[d] = 'X'
            elif is_intersection(yy, xx):
                status[d] = 'I'
            elif is_road(yy, xx):
                status[d] = 'R'
            else:
                status[d] = 'L'

        if self.cell_type == 3:
            if status['N'] in 'RI' and status['S'] in 'RI':
                self.addMove((-1, 0))  # North
                self.addMove((1, 0))   # South
            if status['E'] in 'RI' and status['W'] in 'RI':
                self.addMove((0, 1))   # East
                self.addMove((0, -1))  # West
            if status['N'] in 'RI' and status['E'] in 'RI':
                self.addMove((-1, 0))
                self.addMove((0, 1))
            if status['S'] in 'RI' and status['W'] in 'RI':
                self.addMove((1, 0))
                self.addMove((0, -1))

        elif self.cell_type == 1 or self.cell_type == 2:
            if self.cell_type == 1:  # Horizontal road
                if status['E'] in 'RI':
                    self.addMove((0, 1))
                if status['W'] in 'RI':
                    self.addMove((0, -1))
            if self.cell_type == 2:  # Vertical road
                if status['N'] in 'RI':
                    self.addMove((-1, 0))
                if status['S'] in 'RI':
                    self.addMove((1, 0))
