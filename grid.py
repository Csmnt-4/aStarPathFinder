import noise
import numpy as np

from tile import Tile


class TileGrid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.perlin_grid()
        self.base = None
        self.towers = []

    def clear_grid(self):
        self.tiles = [[Tile(i, j, 999999, 999999, 0, 1, None) for i in range(self.width)] for j in range(self.height)]
        self.base = None
        self.towers = []

    def perlin_grid(self):
        self.clear_grid()
        scale = np.random.randint(3, 5)  # Adjust the scale to modify the "roughness" of the terrain
        octaves = np.random.randint(4, 8)  # Randomize the number of octaves
        persistence = np.random.uniform(0.3, 0.7)  # Randomize the persistence
        lacunarity = np.random.uniform(1.5, 2.5)  # Randomize the lacunarity
        for i in range(self.width):
            for j in range(self.height):
                value = noise.pnoise2(i / scale,
                                      j / scale,
                                      octaves=octaves,
                                      persistence=persistence,
                                      lacunarity=lacunarity,
                                      repeatx=self.width,
                                      repeaty=self.height,
                                      base=0)
                value = (value + 1) * 6  # Normalize to [1, 10]
                self.tiles[i][j] = Tile(i, j, 99999, 99999, 0, value, None)

    def set_base_tower(self, x, y, towers_available):
        if 0 <= x < self.width and 0 <= y < self.height:
            if self.tiles[x][y].state == 0 or self.tiles[x][y].state == 3:  # Road
                if self.base is None:
                    self.base = (x, y)
                    self.tiles[self.base[0]][self.base[1]].state = 1  # Base
                elif towers_available > 0:
                    self.towers.append((x, y))
                    self.tiles[x][y].state = 2  # Tower

    def clear_states(self, clear_all):
        if clear_all:
            self.base = None
            self.towers = None

        for i in range(self.width):
            for j in range(self.height):
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


