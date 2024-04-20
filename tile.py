import numpy as np


class Tile:
    def __init__(self, x, y, g, f, state, value, parent):
        self.x = x
        self.y = y
        self.g = g
        self.f = f
        self.state = state
        self.value = value
        self.parent = parent
        self.open = False
        self.closed = False

    def heuristic(self, point_to):
        return np.sqrt((self.x - point_to.x) ** 2 + (self.y - point_to.y) ** 2)  # Euclidean distance

    def get_color(self):
        if self.state == 0:  # "Open" road
            gray_value = int(((11 - self.value) / 10) * 255)
            return f'#{gray_value:02x}{gray_value:02x}{gray_value:02x}'
        elif self.state == 1:  # Entrance
            return "#C2EFB3"
        elif self.state == 2:  # Exit
            return "#EDAFB8"
        elif self.state == 3:  # Path
            return "#F3C053"