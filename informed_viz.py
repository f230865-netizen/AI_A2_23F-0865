import pygame
import time


# ══════════════════════════════════════════════════════════════
#  Color palette  (per assignment spec)
#  Frontier  → Yellow
#  Explored  → Red
#  Path      → Green / Bright green
# ══════════════════════════════════════════════════════════════

COLORS = {
    "bg":           (15,  17,  26),     # near-black bg
    "empty":        (30,  33,  48),     # dark grid cell
    "grid_line":    (45,  48,  68),     # subtle grid lines
    "wall":         (10,  10,  15),     # almost black wall
    "start":        (0,  220, 130),     # emerald green
    "goal":         (255,  60,  80),    # vivid red
    "frontier":     (255, 220,  50),    # yellow  (spec: frontier = yellow)
    "explored":     (220,  60,  60),    # red     (spec: explored = red/blue)
    "path":         (80,  255, 160),    # bright mint green (spec: path = green)
    "dynamic":      (255, 140,  30),    # orange
    "stats_bg":     (20,  22,  34),
    "stats_border": (60,  65,  95),
    "text_head":    (200, 205, 230),
    "text_value":   (255, 255, 255),
    "text_dim":     (100, 110, 150),
    "accent_gbfs":  (255, 180,  50),    # amber for GBFS
    "accent_astar": (80,  180, 255),    # sky blue for A*
}

STATS_WIDTH = 260


class Visualizer:
    def __init__(self, grid, cell_size=30):
        self.grid = grid
        self.cell_size = cell_size
        self.grid_px_w = grid.width  * cell_size
        self.grid_px_h = grid.height * cell_size
        self.width  = self.grid_px_w + STATS_WIDTH
        self.height = self.grid_px_h

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Informed Search Visualizer")
        self.clock = pygame.time.Clock()

        # Fonts
        self.font_tiny   = pygame.font.SysFont("Consolas", 13)
        self.font_small  = pygame.font.SysFont("Consolas", 15)
        self.font_medium = pygame.font.SysFont("Consolas", 18, bold=True)
        self.font_large  = pygame.font.SysFont("Consolas", 22, bold=True)

        self.start_time = time.time()

    # ──────────────────────────────────────────
    #  Grid drawing
    # ──────────────────────────────────────────

    def draw_grid(self, explored_set=None, frontier_set=None, path=None):
        explored_set  = explored_set  or set()
        frontier_set  = frontier_set  or set()
        path_set      = set(path[1:-1]) if path else set()

        for i in range(self.grid.height):
            for j in range(self.grid.width):
                pos  = (i, j)
                rect = pygame.Rect(j * self.cell_size, i * self.cell_size,
                                   self.cell_size, self.cell_size)

                cell_val = self.grid.grid[i][j]

                if pos == self.grid.start:
                    color = COLORS["start"]
                elif pos == self.grid.goal:
                    color = COLORS["goal"]
                elif cell_val == 1:
                    color = COLORS["wall"]
                elif cell_val == 4:
                    color = COLORS["dynamic"]
                elif pos in path_set:
                    color = COLORS["path"]
                elif pos in explored_set:
                    color = COLORS["explored"]
                elif pos in frontier_set:
                    color = COLORS["frontier"]
                else:
                    color = COLORS["empty"]

                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, COLORS["grid_line"], rect, 1)

        # Draw S / G labels
        self._draw_cell_label(self.grid.start, "S", COLORS["bg"])
        self._draw_cell_label(self.grid.goal,  "G", COLORS["bg"])

    def _draw_cell_label(self, pos, label, color):
        surf = self.font_tiny.render(label, True, color)
        x = pos[1] * self.cell_size + (self.cell_size - surf.get_width())  // 2
        y = pos[0] * self.cell_size + (self.cell_size - surf.get_height()) // 2
        self.screen.blit(surf, (x, y))

    # ──────────────────────────────────────────
    #  Stats panel
    # ──────────────────────────────────────────

    def draw_stats(self, algo_name, heuristic_name,
                   explored_count, path_cost, elapsed_ms,
                   replans, dynamic_count, path_found):

        x0 = self.grid_px_w
        panel = pygame.Rect(x0, 0, STATS_WIDTH, self.height)
        pygame.draw.rect(self.screen, COLORS["stats_bg"], panel)
        pygame.draw.line(self.screen, COLORS["stats_border"],
                         (x0, 0), (x0, self.height), 2)

        x = x0 + 16
        y = 18

        # ── Title ──
        accent = COLORS["accent_astar"] if algo_name == "A*" else COLORS["accent_gbfs"]
        self._label("INFORMED SEARCH", x, y, self.font_medium, COLORS["text_dim"])
        y += 24
        self._label(algo_name, x, y, self.font_large, accent)
        y += 30

        # Divider
        pygame.draw.line(self.screen, COLORS["stats_border"],
                         (x, y), (x0 + STATS_WIDTH - 16, y), 1)
        y += 14

        # ── Heuristic ──
        self._label("Heuristic", x, y, self.font_small, COLORS["text_dim"])
        y += 18
        self._label(heuristic_name, x + 8, y, self.font_medium, COLORS["text_value"])
        y += 30

        # ── Metrics ──
        metrics = [
            ("Nodes Visited",   str(explored_count),          COLORS["frontier"]),
            ("Path Cost",       f"{path_cost:.3f}",           COLORS["path"]),
            ("Time (ms)",       f"{elapsed_ms:.1f}",          COLORS["accent_astar"]),
            ("Re-plans",        str(replans),                  (200, 100, 255)),
            ("Dynamic Obs.",    str(dynamic_count),            COLORS["dynamic"]),
        ]

        for label, value, val_color in metrics:
            self._label(label, x, y, self.font_small, COLORS["text_dim"])
            y += 18
            self._label(value, x + 8, y, self.font_medium, val_color)
            y += 28

        # Status badge
        y += 4
        status_text = "PATH FOUND" if path_found else "NO PATH"
        status_col  = COLORS["path"] if path_found else COLORS["goal"]
        badge = pygame.Rect(x, y, STATS_WIDTH - 32, 28)
        pygame.draw.rect(self.screen, (*status_col, 60), badge, border_radius=4)
        pygame.draw.rect(self.screen, status_col, badge, 2, border_radius=4)
        surf = self.font_medium.render(status_text, True, status_col)
        self.screen.blit(surf, (x + (badge.width - surf.get_width()) // 2, y + 6))
        y += 44

        # Divider
        pygame.draw.line(self.screen, COLORS["stats_border"],
                         (x, y), (x0 + STATS_WIDTH - 16, y), 1)
        y += 14

        # ── Legend ──
        self._label("LEGEND", x, y, self.font_small, COLORS["text_dim"])
        y += 20

        legend = [
            (COLORS["start"],    "Start node"),
            (COLORS["goal"],     "Goal node"),
            (COLORS["frontier"], "Frontier (queue)"),
            (COLORS["explored"], "Explored nodes"),
            (COLORS["path"],     "Final path"),
            (COLORS["wall"],     "Static wall"),
            (COLORS["dynamic"],  "Dynamic obstacle"),
        ]

        for color, lbl in legend:
            pygame.draw.rect(self.screen, color, (x, y + 1, 13, 13), border_radius=2)
            pygame.draw.rect(self.screen, COLORS["stats_border"], (x, y + 1, 13, 13), 1, border_radius=2)
            self._label(lbl, x + 20, y, self.font_tiny, COLORS["text_head"])
            y += 20

        # Controls hint at bottom
        hint_y = self.height - 36
        pygame.draw.line(self.screen, COLORS["stats_border"],
                         (x, hint_y - 8), (x0 + STATS_WIDTH - 16, hint_y - 8), 1)
        self._label("ESC / ✕  to close", x, hint_y, self.font_tiny, COLORS["text_dim"])
        self._label("SPACE to pause", x, hint_y + 16, self.font_tiny, COLORS["text_dim"])

    def _label(self, text, x, y, font, color):
        surf = font.render(text, True, color)
        self.screen.blit(surf, (x, y))

    # ──────────────────────────────────────────
    #  Main animation loop
    # ──────────────────────────────────────────

    def visualize_search(self, algo_name, heuristic_name, steps, path, replans=0):
        self.start_time = time.time()

        frontier_set  = set()
        explored_set  = set()
        dynamic_set   = set()
        paused        = False

        path_found = path is not None

        for step_type, node in steps:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    if event.key == pygame.K_SPACE:
                        paused = not paused

            while paused:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            paused = False
                        if event.key == pygame.K_ESCAPE:
                            return
                self.clock.tick(30)

            if step_type == 'frontier':
                frontier_set.add(node)
            elif step_type == 'explored':
                frontier_set.discard(node)
                explored_set.add(node)
            elif step_type == 'dynamic_obstacle':
                dynamic_set.add(node)

            elapsed_ms = (time.time() - self.start_time) * 1000

            self.screen.fill(COLORS["bg"])
            self.draw_grid(explored_set, frontier_set)
            self.draw_stats(algo_name, heuristic_name,
                            len(explored_set), 0.0, elapsed_ms,
                            replans, len(dynamic_set), path_found)
            pygame.display.flip()
            self.clock.tick(30)

        # ── Final frame with path drawn ──
        elapsed_ms = (time.time() - self.start_time) * 1000
        self.screen.fill(COLORS["bg"])
        self.draw_grid(explored_set, set(), path)
        self.draw_stats(algo_name, heuristic_name,
                        len(explored_set),
                        getattr(self, "_path_cost", 0.0),
                        elapsed_ms,
                        replans,
                        len(self.grid.dynamic_obstacles),
                        path_found)
        pygame.display.flip()

        # ── Wait for close ──
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        waiting = False
            self.clock.tick(30)

    def set_path_cost(self, cost):
        self._path_cost = cost

    def close(self):
        pygame.quit()
