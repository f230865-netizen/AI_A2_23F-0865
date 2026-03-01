import pygame
import sys
import time

from informed_grid import Grid
from informed_search import GreedyBFS, AStar
from informed_viz import Visualizer, COLORS


# ══════════════════════════════════════════════════════════════
#  UI constants
# ══════════════════════════════════════════════════════════════

WIN_W, WIN_H = 820, 620

# Accent colors for the two algorithms
ALGO_COLORS = {
    "Greedy BFS": (255, 180,  50),   # amber
    "A*":         ( 80, 180, 255),   # sky blue
}

HEURISTIC_COLORS = {
    "Manhattan": (160, 255, 160),
    "Euclidean": (255, 160, 220),
}

BG_DARK   = (12,  14,  22)
BG_PANEL  = (20,  23,  36)
BORDER    = (50,  55,  80)
TEXT_HEAD = (200, 210, 240)
TEXT_DIM  = ( 90, 100, 140)
WHITE     = (255, 255, 255)


# ══════════════════════════════════════════════════════════════
#  Reusable UI widgets
# ══════════════════════════════════════════════════════════════

class Button:
    def __init__(self, rect, label, color_active, color_idle=None):
        self.rect         = pygame.Rect(rect)
        self.label        = label
        self.color_active = color_active
        self.color_idle   = color_idle or (40, 44, 64)
        self.active       = False
        self.hovered      = False

    def draw(self, surf, font):
        col   = self.color_active if self.active else self.color_idle
        alpha = 255 if self.active else 180

        # Fill
        pygame.draw.rect(surf, col, self.rect, border_radius=6)

        # Border
        border_col = self.color_active if self.active else BORDER
        pygame.draw.rect(surf, border_col, self.rect, 2, border_radius=6)

        # Hover glow when not active
        if self.hovered and not self.active:
            s = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
            s.fill((*self.color_active, 25))
            surf.blit(s, self.rect.topleft)
            pygame.draw.rect(surf, (*self.color_active, 100), self.rect, 1, border_radius=6)

        # Label
        text_col = BG_DARK if self.active else TEXT_HEAD
        t = font.render(self.label, True, text_col)
        surf.blit(t, t.get_rect(center=self.rect.center))

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def handle_click(self, pos):
        return self.rect.collidepoint(pos)


class Slider:
    """Integer slider with label."""

    def __init__(self, x, y, w, label, min_val, max_val, default, accent):
        self.x, self.y, self.w = x, y, w
        self.label   = label
        self.min_val = min_val
        self.max_val = max_val
        self.value   = default
        self.accent  = accent
        self.dragging = False

        self.track_rect = pygame.Rect(x, y + 28, w, 6)
        self._update_handle()

    def _update_handle(self):
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        hx = self.x + int(ratio * self.w)
        self.handle_rect = pygame.Rect(hx - 9, self.y + 22, 18, 18)

    def draw(self, surf, font_label, font_val):
        # Label
        lbl = font_label.render(self.label, True, TEXT_DIM)
        surf.blit(lbl, (self.x, self.y))

        # Value
        val_str = str(self.value)
        v = font_val.render(val_str, True, self.accent)
        surf.blit(v, (self.x + self.w - v.get_width(), self.y))

        # Track
        pygame.draw.rect(surf, BORDER, self.track_rect, border_radius=3)
        filled = pygame.Rect(self.x, self.y + 28,
                             self.handle_rect.centerx - self.x, 6)
        pygame.draw.rect(surf, self.accent, filled, border_radius=3)

        # Handle
        pygame.draw.circle(surf, self.accent,
                           self.handle_rect.center, 9)
        pygame.draw.circle(surf, BG_DARK,
                           self.handle_rect.center, 5)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.handle_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            raw = event.pos[0]
            clamped = max(self.x, min(self.x + self.w, raw))
            ratio = (clamped - self.x) / self.w
            self.value = int(self.min_val + ratio * (self.max_val - self.min_val))
            self._update_handle()


# ══════════════════════════════════════════════════════════════
#  Setup screen
# ══════════════════════════════════════════════════════════════

class SetupScreen:
    def __init__(self, screen):
        self.screen = screen
        self.clock  = pygame.time.Clock()

        self.font_huge   = pygame.font.SysFont("Consolas", 36, bold=True)
        self.font_large  = pygame.font.SysFont("Consolas", 22, bold=True)
        self.font_medium = pygame.font.SysFont("Consolas", 16, bold=True)
        self.font_small  = pygame.font.SysFont("Consolas", 13)

        # ── State ──
        self.selected_algo      = "A*"
        self.selected_heuristic = "Manhattan"

        # ── Sliders ──
        self.sl_rows  = Slider(100, 180, 280, "Grid Rows",    5, 40, 20, (80, 180, 255))
        self.sl_cols  = Slider(100, 240, 280, "Grid Cols",    5, 40, 20, (80, 180, 255))
        self.sl_obs   = Slider(100, 300, 280, "Wall density %", 0, 50, 20, (255, 140, 50))
        self.sl_dyn   = Slider(100, 360, 280, "Dyn. obs. prob ‰", 0, 50, 5, (255, 180, 100))
        self.sl_speed = Slider(100, 420, 280, "Anim. speed (FPS)", 5, 60, 20, (160, 255, 160))

        # ── Algorithm buttons ──
        self.algo_buttons = [
            Button((460, 175, 150, 46), "A*",         ALGO_COLORS["A*"]),
            Button((625, 175, 150, 46), "Greedy BFS", ALGO_COLORS["Greedy BFS"]),
        ]
        self.algo_buttons[0].active = True   # A* default

        # ── Heuristic buttons ──
        self.heur_buttons = [
            Button((460, 265, 150, 46), "Manhattan", HEURISTIC_COLORS["Manhattan"]),
            Button((625, 265, 150, 46), "Euclidean", HEURISTIC_COLORS["Euclidean"]),
        ]
        self.heur_buttons[0].active = True

        # ── Dynamic mode toggle ──
        self.dynamic_btn = Button((460, 355, 315, 46), "Dynamic Mode: OFF",
                                  (180, 100, 255), (35, 38, 58))
        self.dynamic_on = False

        # ── Run button ──
        self.run_btn = Button((WIN_W // 2 - 120, WIN_H - 90, 240, 54),
                              "▶  RUN SEARCH", (50, 220, 120))

        # ── Interactive editor hint ──
        # (handled in the grid editor mini-preview section)

    def _set_algo(self, name):
        self.selected_algo = name
        for b in self.algo_buttons:
            b.active = (b.label == name)

    def _set_heuristic(self, name):
        self.selected_heuristic = name
        for b in self.heur_buttons:
            b.active = (b.label == name)

    def run(self):
        """Show setup screen; returns config dict or None to quit."""
        while True:
            mouse_pos = pygame.mouse.get_pos()

            # ── Events ──
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return None

                # Sliders
                for sl in [self.sl_rows, self.sl_cols, self.sl_obs,
                            self.sl_dyn, self.sl_speed]:
                    sl.handle_event(event)

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Algorithm buttons
                    for b in self.algo_buttons:
                        if b.handle_click(event.pos):
                            self._set_algo(b.label)

                    # Heuristic buttons
                    for b in self.heur_buttons:
                        if b.handle_click(event.pos):
                            self._set_heuristic(b.label)

                    # Dynamic toggle
                    if self.dynamic_btn.handle_click(event.pos):
                        self.dynamic_on = not self.dynamic_on
                        self.dynamic_btn.label = (
                            "Dynamic Mode: ON " if self.dynamic_on
                            else "Dynamic Mode: OFF"
                        )
                        self.dynamic_btn.active = self.dynamic_on

                    # Run button
                    if self.run_btn.handle_click(event.pos):
                        dyn_prob = (self.sl_dyn.value / 1000.0) if self.dynamic_on else 0.0
                        return {
                            "rows":       self.sl_rows.value,
                            "cols":       self.sl_cols.value,
                            "obs":        self.sl_obs.value / 100.0,
                            "dyn_prob":   dyn_prob,
                            "algo":       self.selected_algo,
                            "heuristic":  self.selected_heuristic,
                            "fps":        self.sl_speed.value,
                        }

            # Hover updates
            for b in self.algo_buttons + self.heur_buttons + [self.dynamic_btn, self.run_btn]:
                b.update(mouse_pos)

            # ── Draw ──
            self.screen.fill(BG_DARK)
            self._draw_bg_decoration()
            self._draw_ui(mouse_pos)
            pygame.display.flip()
            self.clock.tick(60)

    def _draw_bg_decoration(self):
        """Subtle grid lines in background."""
        for x in range(0, WIN_W, 40):
            pygame.draw.line(self.screen, (22, 25, 38), (x, 0), (x, WIN_H))
        for y in range(0, WIN_H, 40):
            pygame.draw.line(self.screen, (22, 25, 38), (0, y), (WIN_W, y))

    def _draw_ui(self, mouse_pos):
        # ── Title ──
        title = self.font_huge.render("INFORMED SEARCH", True, (80, 180, 255))
        sub   = self.font_medium.render("A*  ·  Greedy Best-First Search  ·  AI Pathfinding", True, TEXT_DIM)
        self.screen.blit(title, title.get_rect(centerx=WIN_W // 2, y=28))
        self.screen.blit(sub,   sub.get_rect(centerx=WIN_W // 2, y=78))

        # Divider
        pygame.draw.line(self.screen, BORDER, (60, 108), (WIN_W - 60, 108), 1)

        # ── Left panel: Grid config ──
        panel_l = pygame.Rect(60, 120, 360, 360)
        pygame.draw.rect(self.screen, BG_PANEL, panel_l, border_radius=10)
        pygame.draw.rect(self.screen, BORDER, panel_l, 1, border_radius=10)

        hdr = self.font_large.render("Grid Configuration", True, TEXT_HEAD)
        self.screen.blit(hdr, (80, 132))

        for sl in [self.sl_rows, self.sl_cols, self.sl_obs, self.sl_dyn, self.sl_speed]:
            sl.draw(self.screen, self.font_small, self.font_medium)

        # ── Right panel: Algorithm + heuristic ──
        panel_r = pygame.Rect(440, 120, 320, 280)
        pygame.draw.rect(self.screen, BG_PANEL, panel_r, border_radius=10)
        pygame.draw.rect(self.screen, BORDER, panel_r, 1, border_radius=10)

        hdr2 = self.font_large.render("Algorithm", True, TEXT_HEAD)
        self.screen.blit(hdr2, (460, 132))

        for b in self.algo_buttons:
            b.draw(self.screen, self.font_medium)

        hdr3 = self.font_large.render("Heuristic", True, TEXT_HEAD)
        self.screen.blit(hdr3, (460, 225))

        for b in self.heur_buttons:
            b.draw(self.screen, self.font_medium)

        hdr4 = self.font_large.render("Options", True, TEXT_HEAD)
        self.screen.blit(hdr4, (460, 318))

        self.dynamic_btn.draw(self.screen, self.font_medium)

        # ── Info row: selected config summary ──
        algo_col = ALGO_COLORS.get(self.selected_algo, WHITE)
        heur_col = HEURISTIC_COLORS.get(self.selected_heuristic, WHITE)

        summary_y = 508
        pygame.draw.line(self.screen, BORDER, (60, summary_y - 8), (WIN_W - 60, summary_y - 8), 1)

        parts = [
            (f"{self.selected_algo}",           algo_col),
            ("  +  ",                           TEXT_DIM),
            (f"{self.selected_heuristic}",       heur_col),
            ("  |  ",                            TEXT_DIM),
            (f"{self.sl_rows.value}×{self.sl_cols.value} grid", (160, 200, 255)),
            ("  |  ",                            TEXT_DIM),
            (f"{self.sl_obs.value}% walls",      (255, 160, 80)),
            ("  |  ",                            TEXT_DIM),
            (f"{'Dyn ON' if self.dynamic_on else 'Dyn OFF'}", (180, 100, 255) if self.dynamic_on else TEXT_DIM),
        ]

        cx = 80
        for txt, col in parts:
            s = self.font_medium.render(txt, True, col)
            self.screen.blit(s, (cx, summary_y))
            cx += s.get_width()

        # ── Run button ──
        self.run_btn.draw(self.screen, self.font_large)

        # Editor note
        note = self.font_small.render(
            "Tip: after the grid loads, click cells to toggle walls  |  SPACE to pause animation",
            True, TEXT_DIM)
        self.screen.blit(note, note.get_rect(centerx=WIN_W // 2, y=WIN_H - 28))


# ══════════════════════════════════════════════════════════════
#  Interactive grid editor (runs before the algorithm starts)
# ══════════════════════════════════════════════════════════════

class GridEditor:
    """
    Shows the generated grid and lets the user click to add/remove walls
    before the search begins.
    """

    def __init__(self, screen, grid, cell_size):
        self.screen    = screen
        self.grid      = grid
        self.cell_size = cell_size
        self.clock     = pygame.time.Clock()

        self.grid_px_w = grid.width  * cell_size
        self.grid_px_h = grid.height * cell_size

        self.font_med   = pygame.font.SysFont("Consolas", 16, bold=True)
        self.font_small = pygame.font.SysFont("Consolas", 13)

        self.painting = None   # True = painting walls, False = erasing

    def run(self):
        """Block until user presses SPACE or ENTER to confirm."""
        while True:
            mouse_pos = pygame.mouse.get_pos()
            mouse_buttons = pygame.mouse.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return False
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        return True
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    cell = self._mouse_to_cell(event.pos)
                    if cell:
                        r, c = cell
                        if (r, c) not in [self.grid.start, self.grid.goal]:
                            self.painting = self.grid.grid[r][c] != 1
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.painting = None

            # Drag painting
            if self.painting is not None and mouse_buttons[0]:
                cell = self._mouse_to_cell(mouse_pos)
                if cell:
                    r, c = cell
                    if (r, c) not in [self.grid.start, self.grid.goal]:
                        self.grid.grid[r][c] = 1 if self.painting else 0

            self._draw()
            pygame.display.flip()
            self.clock.tick(60)

    def _mouse_to_cell(self, pos):
        mx, my = pos
        if mx < 0 or my < 0 or mx >= self.grid_px_w or my >= self.grid_px_h:
            return None
        return (my // self.cell_size, mx // self.cell_size)

    def _draw(self):
        self.screen.fill(BG_DARK)

        # Grid cells
        for i in range(self.grid.height):
            for j in range(self.grid.width):
                pos  = (i, j)
                rect = pygame.Rect(j * self.cell_size, i * self.cell_size,
                                   self.cell_size, self.cell_size)
                val  = self.grid.grid[i][j]

                if pos == self.grid.start:
                    col = COLORS["start"]
                elif pos == self.grid.goal:
                    col = COLORS["goal"]
                elif val == 1:
                    col = COLORS["wall"]
                else:
                    col = COLORS["empty"]

                pygame.draw.rect(self.screen, col, rect)
                pygame.draw.rect(self.screen, COLORS["grid_line"], rect, 1)

        # Sidebar
        sx = self.grid_px_w + 16
        self.screen.blit(self.font_med.render("EDIT GRID", True, TEXT_HEAD), (sx, 20))
        lines = [
            ("Click / drag", (80, 180, 255), 50),
            ("to add walls", TEXT_DIM, 68),
            ("Right-click to", (255, 140, 50), 98),
            ("erase walls", TEXT_DIM, 116),
            ("", TEXT_DIM, 140),
            ("SPACE / ENTER", (50, 220, 120), 160),
            ("to start search", TEXT_DIM, 178),
            ("ESC to cancel", TEXT_DIM, 208),
        ]
        for txt, col, dy in lines:
            s = self.font_small.render(txt, True, col)
            self.screen.blit(s, (sx, dy))

        # S / G labels
        for pos, lbl in [(self.grid.start, "S"), (self.grid.goal, "G")]:
            t = self.font_small.render(lbl, True, BG_DARK)
            x = pos[1] * self.cell_size + (self.cell_size - t.get_width())  // 2
            y = pos[0] * self.cell_size + (self.cell_size - t.get_height()) // 2
            self.screen.blit(t, (x, y))


# ══════════════════════════════════════════════════════════════
#  Main entry point
# ══════════════════════════════════════════════════════════════

def compute_cell_size(rows, cols, max_w=900, max_h=680, sidebar=260):
    """Pick largest cell size that fits the screen."""
    cs_w = (max_w - sidebar) // cols
    cs_h = max_h // rows
    return max(8, min(cs_w, cs_h, 40))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Informed Search — Setup")

    while True:
        # ── 1. Setup screen ──
        setup = SetupScreen(screen)
        config = setup.run()

        if config is None:
            break   # user closed window

        rows      = config["rows"]
        cols      = config["cols"]
        obs       = config["obs"]
        dyn_prob  = config["dyn_prob"]
        algo_name = config["algo"]
        heur_name = config["heuristic"]
        fps       = config["fps"]

        # ── 2. Build grid ──
        grid = Grid(width=cols, height=rows,
                    obstacle_probability=obs,
                    dynamic_obstacle_probability=dyn_prob)

        # ── 3. Interactive editor ──
        cell_size = compute_cell_size(rows, cols)
        editor_w  = cols * cell_size + 160
        editor_h  = max(rows * cell_size, 240)

        editor_screen = pygame.display.set_mode((editor_w, editor_h))
        pygame.display.set_caption("Edit Grid — SPACE to start")

        editor = GridEditor(editor_screen, grid, cell_size)
        ok = editor.run()

        if not ok:
            # Back to setup
            screen = pygame.display.set_mode((WIN_W, WIN_H))
            pygame.display.set_caption("Informed Search — Setup")
            continue

        # ── 4. Run algorithm ──
        if algo_name == "A*":
            algorithm = AStar(grid, heuristic_name=heur_name)
        else:
            algorithm = GreedyBFS(grid, heuristic_name=heur_name)

        print(f"\n{'='*50}")
        print(f"  Running {algo_name} with {heur_name} heuristic")
        print(f"  Grid: {rows}×{cols}  |  Walls: {int(obs*100)}%")
        print(f"  Dynamic obstacles: {'ON' if dyn_prob > 0 else 'OFF'}")
        print(f"{'='*50}")

        t0   = time.time()
        path = algorithm.search()
        t1   = time.time()

        elapsed_ms = (t1 - t0) * 1000

        if path:
            print(f"  ✔ Path found! Length: {len(path)}  Cost: {algorithm.path_cost:.3f}")
        else:
            print(f"  ✘ No path found.")

        print(f"  Nodes explored : {len(algorithm.explored)}")
        print(f"  Re-plans       : {algorithm.replans}")
        print(f"  Time           : {elapsed_ms:.1f} ms")

        # ── 5. Visualize ──
        vis_cell  = compute_cell_size(rows, cols)
        vis_w     = cols * vis_cell + 260
        vis_h     = max(rows * vis_cell, 560)

        vis_screen = pygame.display.set_mode((vis_w, vis_h))
        pygame.display.set_caption(f"{algo_name} ({heur_name}) — Visualization")

        viz = Visualizer(grid, cell_size=vis_cell)
        viz.screen = vis_screen
        viz.width   = vis_w
        viz.height  = vis_h
        viz.grid_px_w = cols * vis_cell
        viz.grid_px_h = rows * vis_cell
        viz.set_path_cost(algorithm.path_cost)
        viz.visualize_search(algo_name, heur_name,
                             algorithm.steps, path, algorithm.replans)
        viz.close()

        # Back to setup for another run
        screen = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption("Informed Search — Setup")

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
