import heapq
import math


# ──────────────────────────────────────────────
#  Heuristic functions
# ──────────────────────────────────────────────

def manhattan(a, b):
    """Manhattan distance: |x1-x2| + |y1-y2|"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def euclidean(a, b):
    """Euclidean distance: sqrt((x1-x2)^2 + (y1-y2)^2)"""
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


HEURISTICS = {
    "Manhattan": manhattan,
    "Euclidean": euclidean,
}


# ──────────────────────────────────────────────
#  Base class
# ──────────────────────────────────────────────

class SearchAlgorithm:
    def __init__(self, grid, heuristic_name="Manhattan"):
        self.grid = grid
        self.heuristic = HEURISTICS[heuristic_name]
        self.heuristic_name = heuristic_name
        self.explored = set()
        self.frontier_added = set()
        self.steps = []
        self.replans = 0
        self.path_cost = 0.0

    def h(self, node):
        return self.heuristic(node, self.grid.goal)

    def handle_dynamic_obstacle(self):
        spawned = self.grid.spawn_dynamic_obstacle()
        if spawned:
            self.steps.append(('dynamic_obstacle', spawned))
            return True
        return False

    def _reset_state(self):
        """Reset tracking state for re-planning."""
        self.explored.clear()
        self.frontier_added.clear()


# ──────────────────────────────────────────────
#  Greedy Best-First Search  —  f(n) = h(n)
# ──────────────────────────────────────────────

class GreedyBFS(SearchAlgorithm):
    """
    Greedy Best-First Search
    Priority queue ordered purely by heuristic h(n).
    Fast but not guaranteed to be optimal.
    """

    def search(self):
        start = self.grid.start
        goal  = self.grid.goal

        # heap: (h_value, tie_breaker, node, path)
        counter = 0
        pq = [(self.h(start), counter, start, [start])]
        visited = {start}

        while pq:
            self.handle_dynamic_obstacle()

            h_val, _, node, path = heapq.heappop(pq)

            # Re-plan if dynamic obstacle blocks current path
            blocked = self.grid.is_path_blocked(path)
            if blocked:
                self.replans += 1
                self._reset_state()
                visited = {start}
                counter = 0
                pq = [(self.h(start), counter, start, [start])]
                continue

            if node in self.explored:
                continue

            self.explored.add(node)
            self.steps.append(('explored', node))

            if node == goal:
                self.path_cost = self._calc_path_cost(path)
                return path

            for nb in self.grid.get_neighbors(node[0], node[1]):
                if nb not in visited:
                    visited.add(nb)
                    counter += 1
                    heapq.heappush(pq, (self.h(nb), counter, nb, path + [nb]))

                    if nb not in self.frontier_added:
                        self.frontier_added.add(nb)
                        self.steps.append(('frontier', nb))

        return None

    def _calc_path_cost(self, path):
        cost = 0.0
        for i in range(1, len(path)):
            cost += self.grid.get_movement_cost(path[i - 1], path[i])
        return cost


# ──────────────────────────────────────────────
#  A* Search  —  f(n) = g(n) + h(n)
# ──────────────────────────────────────────────

class AStar(SearchAlgorithm):
    """
    A* Search
    Priority queue ordered by f(n) = g(n) + h(n).
    Optimal and complete (with admissible heuristic).
    """

    def search(self):
        start = self.grid.start
        goal  = self.grid.goal

        # heap: (f_value, tie_breaker, g_value, node, path)
        counter = 0
        pq = [(self.h(start), counter, 0.0, start, [start])]

        # Best known g-cost to each node
        g_costs = {start: 0.0}

        while pq:
            self.handle_dynamic_obstacle()

            f_val, _, g_val, node, path = heapq.heappop(pq)

            # Re-plan if dynamic obstacle blocks current path
            blocked = self.grid.is_path_blocked(path)
            if blocked:
                self.replans += 1
                self._reset_state()
                counter = 0
                g_costs = {start: 0.0}
                pq = [(self.h(start), counter, 0.0, start, [start])]
                continue

            # Skip if we've already found a cheaper path to this node
            if node in self.explored:
                continue

            self.explored.add(node)
            self.steps.append(('explored', node))

            if node == goal:
                self.path_cost = g_val
                return path

            for nb in self.grid.get_neighbors(node[0], node[1]):
                move_cost = self.grid.get_movement_cost(node, nb)
                new_g = g_val + move_cost

                if nb not in g_costs or new_g < g_costs[nb]:
                    g_costs[nb] = new_g
                    counter += 1
                    f = new_g + self.h(nb)
                    heapq.heappush(pq, (f, counter, new_g, nb, path + [nb]))

                    if nb not in self.frontier_added:
                        self.frontier_added.add(nb)
                        self.steps.append(('frontier', nb))

        return None
