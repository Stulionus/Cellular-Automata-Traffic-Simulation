import numpy as np
import matplotlib.pyplot as plt

class Cell:
    def __init__(self, x, y, cell_type):
        self.x = x
        self.y = y
        self.cell_type = cell_type
        self.canMoves = []

    def addMove(self, move):
        if len(move) == 2:
            self.canMoves.append(move)
        else:
            raise ValueError("Needs tuple: [x, y].")

    def getMoves(self):
        return self.canMoves
