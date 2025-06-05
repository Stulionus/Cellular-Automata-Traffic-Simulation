import time
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
        """
        Set the traffic light state for this intersection cell and update occupancy.

        Parameters:
            switch (bool): New light state (True = green, False = red).

        Behavior:
            - If this cell_type is 3 (intersection), update OnOrOff.
            - If setting to green and no car is present, mark occupied = False.
            - If setting to red, mark occupied = True.
        """
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
        """
        Toggle the traffic light state and adjust occupancy accordingly.

        Behavior:
            - Flip OnOrOff (green <=> red) if this is an intersection cell (cell_type == 3).
            - When turning green, mark occupied = False unless a car remains.
            - When turning red, mark occupied = True.
        """
        self.OnOrOff = not self.OnOrOff
        if self.cell_type == 3:
            if self.OnOrOff:  # Green
                # if not self.occupied_by_car:
                    self.occupied = False
            else:  # Red
                self.occupied = True

    def car_enters(self, current_step):
        """
        Record that a car has entered this cell at the given simulation step.

        Parameters:
            current_step (int): The time step when the car enters.

        Behavior:
            - Mark this cell as occupied.
            - Increment total_cars_passed counter.
            - Store entry_step to compute duration later.
        """
        self.occupied = True
        #self.occupied_by_car = True
        self.total_cars_passed += 1
        self.entry_step = current_step

    def leaving(self, current_step):
        """
        Record that a car is leaving this cell at the given simulation step.

        Parameters:
            current_step (int): The time step when the car leaves.

        Behavior:
            - Compute duration spent = current_step - entry_step, if available.
            - Append duration to time_spent_log.
            - Mark occupied_by_car = False.
            - If not a red-light intersection, set occupied = False.
        """
        self.occupied_by_car = False
        
        if self.entry_step is not None:
            duration = current_step - self.entry_step
            self.addTimeSpent(duration)
        else:
            # Fallback if for some reason entry_step was never set:
            self.addTimeSpent(0)

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

    def getTimeLog(self):
        return self.time_spent_log

    def getTotalCarsPassed(self):
        return self.total_cars_passed

    # --- Move calculation ---
    def addPossibleMoves(self, city, intersections, horizontal, vertical):
        """
        Compute and store all valid movement directions from this cell based on road topology.

        Parameters:
            city (City): The City object that provides grid and road masks.
            intersections (np.ndarray): Boolean mask for intersection positions.
            horizontal (np.ndarray): Boolean mask for horizontal-road cells.
            vertical (np.ndarray): Boolean mask for vertical-road cells.

        Behavior:
            - If cell_type == 1 (horizontal), determine canonical east/west direction and allow U-turn if at border.
            - If cell_type == 2 (vertical), determine canonical north/south direction and allow U-turn if at border.
            - If cell_type == 3 (intersection), allow movement in any adjacent direction that is a road or intersection.
            - Otherwise, no moves are added.
        """
        x, y = self.x, self.y
        grid = city.grid

        def in_bounds(x_, y_):
            return 0 <= x_ < grid.shape[1] and 0 <= y_ < grid.shape[0]

        def is_road(x_, y_):
            return in_bounds(x_, y_) and (horizontal[y_, x_] or vertical[y_, x_])

        def is_intersection(x_, y_):
            return in_bounds(x_, y_) and intersections[y_, x_]


        self.travel_dir = None

        if self.cell_type == 1:
            if y > 0 and horizontal[y - 1, x]:
                self.travel_dir = (1, 0)
            elif y + 1 < grid.shape[0] and horizontal[y + 1, x]:
                self.travel_dir = (-1, 0)

        elif self.cell_type == 2:
            if x > 0 and vertical[y, x - 1]:
                self.travel_dir = (0, -1)
            elif x + 1 < grid.shape[1] and vertical[y, x + 1]:
                self.travel_dir = (0, 1)

        if self.travel_dir:
            dx, dy = self.travel_dir
            fx, fy = x + dx, y + dy
            if in_bounds(fx, fy) and is_road(fx, fy):
                self.addMove((dx, dy))
            else:

                if self.cell_type == 1:

                    if dy == 0:
                        ny = y - 1 if dx == 1 else y + 1
                        ndx = -dx
                        if in_bounds(x, ny) and horizontal[ny, x]:
                            self.addMove((0, ny - y))
                            self.addMove((ndx, 0))

                elif self.cell_type == 2:

                    if dx == 0:
                        nx = x - 1 if dy == 1 else x + 1 
                        ndy = -dy 
                        if in_bounds(nx, y) and vertical[y, nx]:
                            self.addMove((nx - x, 0)) 
                            self.addMove((0, ndy))

        elif self.cell_type == 3:

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if in_bounds(nx, ny) and (horizontal[ny, nx] or vertical[ny, nx] or intersections[ny, nx]):
                    self.addMove((dx, dy))
