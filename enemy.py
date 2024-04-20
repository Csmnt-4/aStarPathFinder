class Enemy:
    def __init__(self, x, y, health, speed):
        self.path = None
        self.x = x
        self.y = y
        self.health = health
        self.speed = speed
        self.step = 0

    def update(self):
        if len(self.path) - 1 > self.step:
            self.step += 1
            self.x = self.path[self.step][0]
            self.y = self.path[self.step][1]

    def get_hit(self):
        self.health -= 1

    def find_path(self, grid):
        # Clear all (well, last one) created path and reset the states of tiles
        grid.clear_states(False)
        if grid.base is None or self.x is None or self.y is None:
            print("Please set both start and finish!")
            return

        # Available directions: up, down, left, right
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        open_set = []

        start_node = grid.tiles[grid.base[0]][grid.base[1]]
        open_set.append(start_node)

        while open_set:
            # Getting node with the lowest f
            current_node = open_set.pop(0)

            # Check if current node is the goal
            if (current_node.x, current_node.y) == (self.x, self.y):
                # Reconstruct the path
                path = []
                while current_node.parent is not None:
                    path.append((current_node.x, current_node.y))
                    current_node = grid.tiles[current_node.parent.x][current_node.parent.y]
                path.append(grid.base)
                return path

            # Set node as closed
            current_node.closed = True
            current_node.open = False

            # Explore neighbors
            for direction in directions:

                # Skip if it's out of bounds
                if not (0 <= current_node.x + direction[0] < grid.width
                        and 0 <= current_node.y + direction[1] < grid.height):
                    continue

                neighbor = grid.tiles[current_node.x + direction[0]][current_node.y + direction[1]]

                # Calculate new g score
                ng = current_node.g + neighbor.value

                # Check if neighbor has been visited or has a better g score
                if neighbor.closed and ng >= neighbor.g:
                    continue

                if ng < neighbor.g or not neighbor.open:
                    # Update g score and f score for the neighbor
                    neighbor.g = ng
                    neighbor.f = ng + neighbor.heuristic(grid.tiles[self.x][self.y])
                    neighbor.open = True
                    neighbor.closed = False

                    # Update the parent node
                    neighbor.parent = current_node

                    # Add to the open set
                    open_set.append(neighbor)
                    open_set.sort(key=lambda node: node.f)

                grid.tiles[neighbor.x][neighbor.y] = neighbor

        # If the open set is empty and goal is not found, return empty path
        return []

