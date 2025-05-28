class Cell:
    def __init__(self, x, y, cell_type):
        self.x = x
        self.y = y
        self.cell_type = cell_type
        self.canMove = []

    def addMove(self, move):
        self.canMove.append(move)

    def add_possible_moves(self, city, intersections, horizontal, vertical):
        x, y = self.x, self.y
        grid = city.grid

        def is_valid(x, y):
            return 0 <= x < grid.shape[1] and 0 <= y < grid.shape[0]

        def is_intersection(x, y):
            return is_valid(x, y) and intersections[y, x]

        def is_road(x, y):
            return is_valid(x, y) and (horizontal[y, x] or vertical[y, x])

        # Intersection logic
        if is_intersection(x, y):
            neighbors = {
                "N": is_road(x, y - 1),
                "S": is_road(x, y + 1),
                "E": is_road(x + 1, y),
                "W": is_road(x - 1, y),
                "SE": is_road(x + 1, y + 1),
                "SW": is_road(x - 1, y + 1),
                "NE": is_road(x + 1, y - 1),
                "NW": is_road(x - 1, y - 1),
            }

            # Determine intersection corner
            if not neighbors["SE"]:
                if neighbors["N"]: self.addMove((0, -1))  # N
                if neighbors["E"]: self.addMove((1, 0))   # E
            elif not neighbors["SW"]:
                if neighbors["N"]: self.addMove((0, -1))  # N
                if neighbors["W"]: self.addMove((-1, 0))  # W
            elif not neighbors["NW"]:
                if neighbors["S"]: self.addMove((0, 1))   # S
                if neighbors["W"]: self.addMove((-1, 0))  # W
            elif not neighbors["NE"]:
                if neighbors["S"]: self.addMove((0, 1))   # S
                if neighbors["E"]: self.addMove((1, 0))   # E

        # Horizontal or vertical road logic
        elif is_road(x, y):
            NW = is_road(x - 1, y - 1)
            N  = is_road(x, y - 1)
            NE = is_road(x + 1, y - 1)
            W  = is_road(x - 1, y)
            E  = is_road(x + 1, y)
            SW = is_road(x - 1, y + 1)
            S  = is_road(x, y + 1)
            SE = is_road(x + 1, y + 1)

            # Right side detection
            if not (NW or N or NE) and (W and E and SW and S and SE):
                self.addMove((-1, 0))  # top side of horizontal, go west
            elif not (SW or S or SE) and (W and E and NW and N and NE):
                self.addMove((1, 0))   # bottom side of horizontal, go east
            elif not (NE or E or SE) and (N and S and NW and W and SW):
                self.addMove((0, 1))   # left side of vertical, go south
            elif not (NW or W or SW) and (N and S and NE and E and SE):
                self.addMove((0, -1))  # right side of vertical, go north
