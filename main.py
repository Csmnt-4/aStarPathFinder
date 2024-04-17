import tkinter as tk
import numpy as np
import noise

GRID_SIZE = 20
GRID_WIDTH = 400
GRID_HEIGHT = 400


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
        if self.state == 0:     # "Open" road
            gray_value = int(((11 - self.value) / 10) * 255)
            return f'#{gray_value:02x}{gray_value:02x}{gray_value:02x}'
        elif self.state == 1:   # Entrance
            return "#C2EFB3"
        elif self.state == 2:   # Exit
            return "#EDAFB8"
        elif self.state == 3:    # Path
            return "#F3C053"


class TileGrid(tk.Canvas):
    def __init__(self, master, size, width, height):
        super().__init__(master, width=width, height=height, bg='white')
        self.size = size
        self.width = width
        self.height = height
        if not (self.load_grid_from_file("Map.txt")):
            self.randomize_grid()
        self.entrance = None
        self.exit = None
        self.draw_grid()

    def draw_grid(self):
        cell_width = self.width / self.size
        cell_height = self.height / self.size

        for i in range(self.size):
            for j in range(self.size):
                self.draw_tile(i, j)

    def clear_grid(self):
        self.delete("all")
        self.tiles = [[Tile(i, j, 999999, 999999, 0, 1, None) for i in range(self.size)] for j in range(self.size)]
        self.entrance = None
        self.exit = None
        self.draw_grid()

    def randomize_grid(self):
        self.clear_grid()
        for i in range(self.size):
            for j in range(self.size):
                value = np.random.uniform(0, 10)
                self.tiles[i][j] = Tile(i, j, 0, 0, 0, value, None)
                self.draw_tile(i, j)

    def load_grid_from_file(self, filename):
        self.clear_grid()
        try:
            with open(filename, 'r') as file:
                lines = file.readlines()
                for i, line in enumerate(lines):
                    values = line.strip().split()
                    for j, val in enumerate(values):
                        value = float(val)
                        self.tiles[i][j] = Tile(i, j, 999999, 999999, 0, value, None)
                        self.draw_tile(i, j)
            return Tile
        except FileNotFoundError:
            print("File not found! Map.txt not found!")
            return False

    def perlin_grid(self):
        self.clear_grid()
        scale = 4.0  # Adjust the scale to modify the "roughness" of the terrain
        octaves = np.random.randint(4, 8)  # Randomize the number of octaves
        persistence = np.random.uniform(0.3, 0.7)  # Randomize the persistence
        lacunarity = np.random .uniform(1.5, 2.5)  # Randomize the lacunarity
        for i in range(self.size):
            for j in range(self.size):
                value = noise.pnoise2(i / scale,
                                      j / scale,
                                      octaves=octaves,
                                      persistence=persistence,
                                      lacunarity=lacunarity,
                                      repeatx=self.size,
                                      repeaty=self.size,
                                      base=0)
                value = (value + 1) * 6 # Normalize to [1, 10]
                self.tiles[i][j] = Tile(i, j, 99999, 99999, 0, value, None)
                self.draw_tile(i, j)

    def set_entrance_exit(self, event):
        cell_width = self.width / self.size
        cell_height = self.height / self.size
        col = int(event.x // cell_width)
        row = int(event.y // cell_height)

        if 0 <= row < self.size and 0 <= col < self.size:
            if self.tiles[row][col].state == 0 or self.tiles[row][col].state == 3:  # Road
                if self.entrance is None:
                    self.entrance = (row, col)
                    self.tiles[self.entrance[0]][self.entrance[1]].state = 1  # Entrance
                elif self.exit is None:
                    self.exit = (row, col)
                    self.tiles[self.exit[0]][self.exit[1]].state = 2  # Exit
            else:
                if self.tiles[row][col].state == 1:  # Entrance
                    self.entrance = None
                elif self.tiles[row][col].state == 2:  # Exit
                    self.exit = None
                self.tiles[row][col].state = 0  # Road
            self.draw_tile(row, col)

    def draw_tile(self, row, col):
        cell_width = self.width / self.size
        cell_height = self.height / self.size
        x0 = col * cell_width
        y0 = row * cell_height
        x1 = x0 + cell_width
        y1 = y0 + cell_height
        self.create_rectangle(x0, y0, x1, y1, fill=self.tiles[row][col].get_color(), outline='')
        self.create_text(x0 + 10, y0 + 10,
                         text=str(round(self.tiles[row][col].value, 1)).rstrip('0').rstrip('.'),
                         fill='black')  # Remove trailing zeros and display value

    def clear_states(self, clear_all):
        if clear_all:
            self.entrance = None
            self.exit = None

        for i in range(self.size):
            for j in range(self.size):
                if clear_all:
                    self.tiles[i][j].state = 0
                else:
                    if self.tiles[i][j].state != 1 and self.tiles[i][j].state != 2:
                        self.tiles[i][j].state = 0
                self.tiles[i][j].g = 99999
                self.tiles[i][j].f = 99999
                self.tiles[i][j].parent = None
                self.tiles[i][j].open = False
                self.tiles[i][j].closed = False
        self.update()
        self.draw_grid()

    def find_path(self):
        # Clear all (well, last one) created path and reset the states of tiles
        self.clear_states(False)
        if self.entrance is None or self.exit is None:
            print("Please set both entrance and exit!")
            return

        # Available directions: up, down, left, right
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        open_set = []

        start_node = self.tiles[self.entrance[0]][self.entrance[1]]
        open_set.append(start_node)

        while open_set:
            # Getting node with the lowest f
            current_node = open_set.pop(0)

            # Check if current node is the goal
            if (current_node.x, current_node.y) == self.exit:
                # Reconstruct the path
                path = []
                while current_node.parent is not None:
                    path.append((current_node.x, current_node.y))
                    current_node = self.tiles[current_node.parent.x][current_node.parent.y]
                path.append(self.entrance)
                path.reverse()
                self.mark_path(path)
                return path

            # Set node as closed
            current_node.closed = True
            current_node.open = False

            # Explore neighbors
            for direction in directions:

                # Skip if it's out of bounds
                if not (0 <= current_node.x + direction[0] < self.size
                        and 0 <= current_node.y + direction[1] < self.size):
                    continue

                neighbor = self.tiles[current_node.x + direction[0]][current_node.y + direction[1]]

                # Calculate new g score
                ng = current_node.g + neighbor.value

                # Check if neighbor has been visited or has a better g score
                if neighbor.closed and ng >= neighbor.g:
                    continue

                if ng < neighbor.g or not neighbor.open:
                    # Update g score and f score for the neighbor
                    neighbor.g = ng
                    neighbor.f = ng + neighbor.heuristic(self.tiles[self.exit[0]][self.exit[1]])
                    neighbor.open = True
                    neighbor.closed = False

                    # Update the parent node
                    neighbor.parent = current_node

                    # Add to the open set
                    open_set.append(neighbor)
                    open_set.sort(key=lambda node: node.f)

                self.tiles[neighbor.x][neighbor.y] = neighbor

        # If the open set is empty and goal is not found, return empty path
        return []

    def mark_path(self, path):
        for x, y in path:
            if self.tiles[x][y].state != 1 and self.tiles[x][y].state != 2:
                self.tiles[x][y].state = 3  # Path
                self.draw_tile(x, y)


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tile Grid")
        self.geometry(f"{GRID_WIDTH}x{GRID_HEIGHT + 40}")

        self.grid = TileGrid(self, GRID_SIZE, GRID_WIDTH, GRID_HEIGHT)
        self.grid.pack()

        self.clear_button = tk.Button(self, text="Clear", command=self.clear_grid)
        self.clear_button.pack(side="left", padx=5, pady=5)

        self.path_button = tk.Button(self, text="Do the A*!", command=self.find_path)
        self.path_button.pack(side="left", padx=5, pady=5)

        self.load_button = tk.Button(self, text="Load File", command=self.load_from_file)
        self.load_button.pack(side="left", padx=5, pady=5)

        self.perlin_button = tk.Button(self, text="Perlin", command=self.perlin_grid)
        self.perlin_button.pack(side="right", padx=5, pady=5)

        self.random_button = tk.Button(self, text="Random", command=self.randomize_grid)
        self.random_button.pack(side="right", padx=5, pady=5)


        self.grid.bind("<Button-1>", self.grid.set_entrance_exit)

    def clear_grid(self):
        # self.grid.clear_grid()
        self.grid.clear_states(True)

    def randomize_grid(self):
        self.grid.randomize_grid()

    def perlin_grid(self):
        self.grid.perlin_grid()

    def load_from_file(self):
        filename = "Map.txt"
        self.grid.load_grid_from_file(filename)

    def find_path(self):
        path = self.grid.find_path()
        print("Path:", path)


if __name__ == "__main__":
    app = Application()
    app.mainloop()
