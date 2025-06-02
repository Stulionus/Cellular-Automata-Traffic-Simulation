class Cell:
    def __init__(self, y, x, cell_type, intersections):
        self.y = y
        self.x = x

        # Determine if the cell is an intersection
        if 0 <= y < intersections.shape[0] and 0 <= x < intersections.shape[1] and intersections[y, x]:
            self.cell_type = 3
        else:
            self.cell_type = cell_type

        # Movement, state, and tracking
        self.canMove = []
        self.OnOrOff = False  # Traffic light state
        self.occupied = False  # Includes both cars and red lights at intersections
        self.occupied_by_car = False
        self.time_spent_log = []
        self.total_cars_passed = 0

    # --- Getters and traffic light control ---
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
            if switch and not self.occupied_by_car:
                self.occupied = False
            elif not switch:
                self.occupied = True

    def switch_traffic_light(self):
        """Toggle the traffic light state and update occupancy accordingly."""
        self.setOnOrOff(not self.OnOrOff)

    # --- Car movement & occupancy ---
    def car_enters(self):
        self.occupied_by_car = True
        self.occupied = True

    def leaving(self):
        self.occupied_by_car = False
        if self.cell_type != 3 or self.OnOrOff:  # If not an intersection, or green light
            self.occupied = False

    # --- Movement configuration ---
    def addMove(self, move):
        self.canMove.append(move)

    def getPossibleMoves(self):
        return self.canMove

    def addPossibleMoves(self, city, intersections, horizontal, vertical):
        x, y = self.x, self.y
        grid = city.grid

        def in_bounds(y_, x_):
            return 0 <= y_ < grid.shape[0] and 0 <= x_ < grid.shape[1]

        def is_road(y_, x_):
            return in_bounds(y_, x_) and (horizontal[y_, x_] or vertical[y_, x_])

        def is_intersection(y_, x_):
            return in_bounds(y_, x_) and intersections[y_, x_]

        self.travel_dir = None  # Reset

        # --- Movement logic for roads (local and highway)
        if self.cell_type in (2, 6):
            # Horizontal direction check
            if y > 0 and horizontal[y - 1, x]:  # Bottom lane → eastbound
                self.travel_dir = (1, 0)
            elif y + 1 < grid.shape[0] and horizontal[y + 1, x]:  # Top lane → westbound
                self.travel_dir = (-1, 0)

            # Vertical direction check
            elif x > 0 and vertical[y, x - 1]:  # Right lane → northbound
                self.travel_dir = (0, -1)
            elif x + 1 < grid.shape[1] and vertical[y, x + 1]:  # Left lane → southbound
                self.travel_dir = (0, 1)

            # Forward movement
            if self.travel_dir:
                dx, dy = self.travel_dir
                fx, fy = x + dx, y + dy
                if in_bounds(fy, fx) and is_road(fy, fx):
                    self.addMove((dx, dy))
                else:
                    # U-turn at edge of road
                    if dy == 0:  # Horizontal
                        ny = y - 1 if dx == 1 else y + 1
                        ndx = -dx
                        if in_bounds(ny, x) and horizontal[ny, x]:
                            self.addMove((0, ny - y))
                            self.addMove((ndx, 0))
                    elif dx == 0:  # Vertical
                        nx = x - 1 if dy == 1 else x + 1
                        ndy = -dy
                        if in_bounds(y, nx) and vertical[y, nx]:
                            self.addMove((nx - x, 0))
                            self.addMove((0, ndy))

        # --- Movement logic for intersections
        elif self.cell_type == 3:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if in_bounds(ny, nx) and (
                    horizontal[ny, nx] or vertical[ny, nx] or intersections[ny, nx]
                ):
                    self.addMove((dx, dy))


    # --- Car time logging ---
    def addTimeSpent(self, time_spent):
        self.time_spent_log.append(time_spent)
        self.total_cars_passed += 1

    def getTimeLog(self):
        return self.time_spent_log

    def getTotalCarsPassed(self):
        return self.total_cars_passed
