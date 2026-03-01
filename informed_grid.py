import random


class Grid:
    def __init__(self, width=20, height=20, obstacle_probability=0.2, dynamic_obstacle_probability=0.05):
        self.width = width
        self.height = height
        self.grid = [[0 for _ in range(width)] for _ in range(height)]

        # 0 = empty, 1 = static wall, 2 = start, 3 = goal, 4 = dynamic obstacle
        self.start = (0, 0)
        self.goal = (height - 1, width - 1)

        self.dynamic_obstacle_probability = dynamic_obstacle_probability
        self.dynamic_obstacles = set()

        self.grid[self.start[0]][self.start[1]] = 2
        self.grid[self.goal[0]][self.goal[1]] = 3

        self.add_obstacles(obstacle_probability)

    def add_obstacles(self, probability):
        total_cells = self.width * self.height - 2
        target_obstacle_count = int(total_cells * probability)
        actual_count = 0

        possible_positions = [
            (i, j)
            for i in range(self.height)
            for j in range(self.width)
            if (i, j) not in [self.start, self.goal]
        ]

        random.shuffle(possible_positions)

        for row, col in possible_positions:
            if actual_count >= target_obstacle_count:
                break
            self.grid[row][col] = 1
            actual_count += 1

    def spawn_dynamic_obstacle(self):
        if random.random() < self.dynamic_obstacle_probability:
            attempts = 0
            while attempts < 50:
                row = random.randint(0, self.height - 1)
                col = random.randint(0, self.width - 1)
                if (
                    (row, col) not in [self.start, self.goal]
                    and self.grid[row][col] == 0
                    and (row, col) not in self.dynamic_obstacles
                ):
                    self.grid[row][col] = 4
                    self.dynamic_obstacles.add((row, col))
                    return (row, col)
                attempts += 1
        return None

    def remove_dynamic_obstacle(self, pos):
        if pos in self.dynamic_obstacles:
            self.dynamic_obstacles.remove(pos)
            self.grid[pos[0]][pos[1]] = 0

    def is_path_blocked(self, path):
        for pos in path:
            if self.grid[pos[0]][pos[1]] == 4:
                return pos
        return None

    def is_walkable(self, row, col):
        if 0 <= row < self.height and 0 <= col < self.width:
            return self.grid[row][col] not in [1, 4]
        return False

    def get_neighbors(self, row, col):
        neighbors = []

        moves = [
            (row - 1, col),        # Up
            (row, col + 1),        # Right
            (row + 1, col),        # Down
            (row, col - 1),        # Left
        ]

        # Diagonal: Bottom-Right
        if (self.is_walkable(row + 1, col + 1)
                and self.is_walkable(row + 1, col)
                and self.is_walkable(row, col + 1)):
            moves.append((row + 1, col + 1))

        # Diagonal: Top-Left
        if (self.is_walkable(row - 1, col - 1)
                and self.is_walkable(row - 1, col)
                and self.is_walkable(row, col - 1)):
            moves.append((row - 1, col - 1))

        for r, c in moves[:4]:  # cardinal first
            if self.is_walkable(r, c):
                neighbors.append((r, c))

        # Add diagonals if computed
        for r, c in moves[4:]:
            neighbors.append((r, c))

        return neighbors

    def get_movement_cost(self, from_pos, to_pos):
        row_diff = abs(to_pos[0] - from_pos[0])
        col_diff = abs(to_pos[1] - from_pos[1])
        if row_diff == 1 and col_diff == 1:
            return 1.414
        return 1.0
