"""FormationRenderer - Handles all rendering for the formation editor.

Extracted from FormationEditorScene to separate rendering concerns from
event handling and business logic.
"""

from __future__ import annotations

import math
import pygame
from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple

if TYPE_CHECKING:
    from pygame import Rect, Surface


class FormationRenderer:
    """Handles rendering for the formation editor canvas.

    Responsibilities:
    - Coordinate transformations (world <-> screen)
    - Grid rendering
    - Arrow/marker rendering
    - Selection box and resize handle rendering
    - Snap-to-grid logic
    """

    def __init__(self, width: int, height: int, toolbar_height: int = 80) -> None:
        """Initialize the renderer.

        Args:
            width: Screen width in pixels
            height: Screen height in pixels
            toolbar_height: Height of toolbar area at bottom
        """
        self.width = width
        self.height = height
        self.toolbar_height = toolbar_height

        # Camera state
        self.camera_zoom = 1.0
        self.camera_pan = [0, 0]

        # Grid settings
        self.grid_size = 50
        self.snap_enabled = True
        self.show_grid = True

        # Colors
        self.col_bg = (30, 30, 40)
        self.col_grid = (45, 45, 55)
        self.col_axis = (60, 60, 70)
        self.col_arrow = (100, 200, 255)
        self.col_arrow_sel = (255, 255, 100)
        self.col_box = (100, 255, 100)
        self.col_arrow_fixed = (100, 255, 100)
        self.col_arrow_fixed_sel = (200, 255, 200)

    def get_canvas_rect(self) -> pygame.Rect:
        """Get the drawable canvas area (excludes toolbar)."""
        return pygame.Rect(0, 0, self.width, self.height - self.toolbar_height)

    def handle_resize(self, width: int, height: int) -> None:
        """Handle window resize."""
        self.width = width
        self.height = height

    # --- Coordinate Transforms ---

    def world_to_screen(self, wx: float, wy: float) -> Tuple[float, float]:
        """Convert world coordinates to screen coordinates.

        Args:
            wx: World X coordinate
            wy: World Y coordinate

        Returns:
            Tuple of (screen_x, screen_y)
        """
        cx = self.width / 2
        cy = (self.height - self.toolbar_height) / 2
        sx = (wx * self.camera_zoom) + self.camera_pan[0] + cx
        sy = (wy * self.camera_zoom) + self.camera_pan[1] + cy
        return sx, sy

    def screen_to_world(self, sx: float, sy: float) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates.

        Args:
            sx: Screen X coordinate
            sy: Screen Y coordinate

        Returns:
            Tuple of (world_x, world_y)
        """
        cx = self.width / 2
        cy = (self.height - self.toolbar_height) / 2
        wx = (sx - self.camera_pan[0] - cx) / self.camera_zoom
        wy = (sy - self.camera_pan[1] - cy) / self.camera_zoom
        return wx, wy

    def snap(self, val: float) -> float:
        """Snap value to grid if snap is enabled.

        Args:
            val: Value to potentially snap

        Returns:
            Snapped value if snap enabled, otherwise original value
        """
        if not self.snap_enabled:
            return val
        return round(val / self.grid_size) * self.grid_size

    # --- Selection Bounds ---

    def get_selection_bounds(
        self,
        arrows: List[List[float]],
        selected_indices: Set[int]
    ) -> Optional[pygame.Rect]:
        """Get bounding rectangle of selected arrows.

        Args:
            arrows: List of arrow [x, y] positions
            selected_indices: Set of selected arrow indices

        Returns:
            Bounding Rect in world coordinates, or None if no selection
        """
        if not selected_indices:
            return None

        xs: List[float] = []
        ys: List[float] = []

        for i in selected_indices:
            ax, ay = arrows[i]
            if self.snap_enabled:
                ax = self.snap(ax)
                ay = self.snap(ay)
            xs.append(ax)
            ys.append(ay)

        return pygame.Rect(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))

    def get_resize_handles(
        self,
        bounds_rect: Optional[pygame.Rect]
    ) -> Dict[str, pygame.Rect]:
        """Get resize handle rectangles for a selection bounds.

        Args:
            bounds_rect: Selection bounding box in world coordinates

        Returns:
            Dict mapping handle names ('TL', 'TR', etc.) to screen-space Rects
        """
        if not bounds_rect:
            return {}

        # Inflate bounds by 1 grid unit for drawing box
        padding = self.grid_size
        inflated = bounds_rect.inflate(padding * 2, padding * 2)

        l, t = self.world_to_screen(inflated.left, inflated.top)
        r, b = self.world_to_screen(inflated.right, inflated.bottom)
        w, h = r - l, b - t

        handles: Dict[str, pygame.Rect] = {}
        hs = 8  # handle size

        # Corner handles
        handles['TL'] = pygame.Rect(l - hs, t - hs, hs * 2, hs * 2)
        handles['TR'] = pygame.Rect(r - hs, t - hs, hs * 2, hs * 2)
        handles['BL'] = pygame.Rect(l - hs, b - hs, hs * 2, hs * 2)
        handles['BR'] = pygame.Rect(r - hs, b - hs, hs * 2, hs * 2)

        # Edge handles (only if large enough)
        if w > 40:
            handles['T'] = pygame.Rect(l + w / 2 - hs, t - hs, hs * 2, hs * 2)
            handles['B'] = pygame.Rect(l + w / 2 - hs, b - hs, hs * 2, hs * 2)
        if h > 40:
            handles['L'] = pygame.Rect(l - hs, t + h / 2 - hs, hs * 2, hs * 2)
            handles['R'] = pygame.Rect(r - hs, t + h / 2 - hs, hs * 2, hs * 2)

        return handles

    # --- Drawing Methods ---

    def draw(
        self,
        screen: pygame.Surface,
        arrows: List[List[float]],
        arrow_attrs: List[Dict[str, str]],
        selected_indices: Set[int],
        state: str,
        drag_start_screen: Optional[Tuple[int, int]]
    ) -> None:
        """Draw the complete formation editor canvas.

        Args:
            screen: Pygame surface to draw on
            arrows: List of arrow [x, y] positions
            arrow_attrs: List of arrow attribute dicts
            selected_indices: Set of selected arrow indices
            state: Current interaction state ('IDLE', 'BOX_SELECT', etc.)
            drag_start_screen: Start position of current drag (for box select)
        """
        screen.fill(self.col_bg)

        if self.show_grid:
            self._draw_grid(screen)

        self._draw_axes(screen)
        self._draw_arrows(screen, arrows, arrow_attrs, selected_indices)
        self._draw_single_selection_controls(screen, arrows, selected_indices)
        self._draw_selection_box(screen, arrows, selected_indices)
        self._draw_marquee(screen, state, drag_start_screen)
        self._draw_toolbar_background(screen)

    def _draw_grid(self, screen: pygame.Surface) -> None:
        """Draw the background grid."""
        wx0, wy0 = self.screen_to_world(0, 0)
        wx1, wy1 = self.screen_to_world(self.width, self.height - self.toolbar_height)

        start_x = math.floor(wx0 / self.grid_size) * self.grid_size
        end_x = math.ceil(wx1 / self.grid_size) * self.grid_size
        start_y = math.floor(wy0 / self.grid_size) * self.grid_size
        end_y = math.ceil(wy1 / self.grid_size) * self.grid_size

        x = start_x
        while x <= end_x:
            sx, _ = self.world_to_screen(x, 0)
            pygame.draw.line(screen, self.col_grid, (sx, 0),
                             (sx, self.height - self.toolbar_height))
            x += self.grid_size

        y = start_y
        while y <= end_y:
            _, sy = self.world_to_screen(0, y)
            pygame.draw.line(screen, self.col_grid, (0, sy), (self.width, sy))
            y += self.grid_size

    def _draw_axes(self, screen: pygame.Surface) -> None:
        """Draw the origin axes."""
        ox, oy = self.world_to_screen(0, 0)
        pygame.draw.line(screen, self.col_axis, (ox, 0),
                         (ox, self.height - self.toolbar_height), 2)
        pygame.draw.line(screen, self.col_axis, (0, oy), (self.width, oy), 2)

    def _draw_arrows(
        self,
        screen: pygame.Surface,
        arrows: List[List[float]],
        arrow_attrs: List[Dict[str, str]],
        selected_indices: Set[int]
    ) -> None:
        """Draw all arrow markers."""
        font = pygame.font.SysFont("Arial", 14, bold=True)
        scale = 20 * self.camera_zoom
        canvas_rect = self.get_canvas_rect()

        for i, (ax, ay) in enumerate(arrows):
            if self.snap_enabled:
                ax = self.snap(ax)
                ay = self.snap(ay)

            sx, sy = self.world_to_screen(ax, ay)

            # Skip if outside visible canvas
            if not canvas_rect.inflate(100, 100).collidepoint(sx, sy):
                continue

            # Determine colors based on selection and rotation mode
            is_selected = i in selected_indices
            attr = arrow_attrs[i]
            is_fixed = attr.get('rotation_mode', 'relative') == 'fixed'

            if is_fixed:
                color = self.col_arrow_fixed_sel if is_selected else self.col_arrow_fixed
            else:
                color = self.col_arrow_sel if is_selected else self.col_arrow

            border_col = (255, 255, 255) if is_selected else (0, 0, 0)

            # Draw triangle pointing up
            points = [
                (sx, sy - scale),
                (sx - scale * 0.8, sy + scale * 0.8),
                (sx + scale * 0.8, sy + scale * 0.8)
            ]
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, border_col, points, 2)

            # Draw number label
            if scale > 10:
                txt = font.render(str(i + 1), True, (0, 0, 0))
                screen.blit(txt, (int(sx) - txt.get_width() // 2, int(sy)))

    def _draw_single_selection_controls(
        self,
        screen: pygame.Surface,
        arrows: List[List[float]],
        selected_indices: Set[int]
    ) -> None:
        """Draw reorder arrows for single selection."""
        if len(selected_indices) != 1:
            return

        idx = list(selected_indices)[0]
        ax, ay = arrows[idx]

        if self.snap_enabled:
            ax = self.snap(ax)
            ay = self.snap(ay)

        sx, sy = self.world_to_screen(ax, ay)
        scale = 20 * self.camera_zoom

        # Up arrow (decrease index)
        up_poly = [
            (sx, sy - scale - 25),
            (sx - 10, sy - scale - 10),
            (sx + 10, sy - scale - 10)
        ]
        pygame.draw.polygon(screen, (200, 200, 200), up_poly)

        # Down arrow (increase index)
        down_poly = [
            (sx, sy + scale + 25),
            (sx - 10, sy + scale + 10),
            (sx + 10, sy + scale + 10)
        ]
        pygame.draw.polygon(screen, (200, 200, 200), down_poly)

    def _draw_selection_box(
        self,
        screen: pygame.Surface,
        arrows: List[List[float]],
        selected_indices: Set[int]
    ) -> None:
        """Draw selection bounding box and resize handles."""
        if not selected_indices:
            return

        bounds = self.get_selection_bounds(arrows, selected_indices)
        if not bounds:
            return

        # Inflate visual bounds for handles
        padding = self.grid_size
        inflated = bounds.inflate(padding * 2, padding * 2)

        l, t = self.world_to_screen(inflated.left, inflated.top)
        r, b = self.world_to_screen(inflated.right, inflated.bottom)
        screen_bounds = pygame.Rect(l, t, r - l, b - t)

        pygame.draw.rect(screen, self.col_box, screen_bounds, 1)

        # Draw resize handles
        handles = self.get_resize_handles(bounds)
        for h_rect in handles.values():
            pygame.draw.rect(screen, self.col_box, h_rect)

    def _draw_marquee(
        self,
        screen: pygame.Surface,
        state: str,
        drag_start_screen: Optional[Tuple[int, int]]
    ) -> None:
        """Draw the selection marquee during box select."""
        if state not in ('BOX_SELECT', 'POTENTIAL_CLICK'):
            return

        if drag_start_screen is None:
            return

        mx, my = pygame.mouse.get_pos()
        sx, sy = drag_start_screen
        rect = pygame.Rect(min(sx, mx), min(sy, my), abs(mx - sx), abs(my - sy))

        if state == 'BOX_SELECT':
            surf = pygame.Surface(rect.size, pygame.SRCALPHA)
            surf.fill((100, 255, 100, 50))
            screen.blit(surf, rect.topleft)
            pygame.draw.rect(screen, (100, 255, 100), rect, 1)

    def _draw_toolbar_background(self, screen: pygame.Surface) -> None:
        """Draw the toolbar background area."""
        pygame.draw.rect(
            screen,
            (20, 20, 30),
            (0, self.height - self.toolbar_height, self.width, self.toolbar_height)
        )

    def get_renumber_arrow_rects(
        self,
        arrows: List[List[float]],
        selected_indices: Set[int]
    ) -> Tuple[Optional[pygame.Rect], Optional[pygame.Rect]]:
        """Get hit rects for reorder arrows on single selection.

        Args:
            arrows: List of arrow positions
            selected_indices: Set of selected indices

        Returns:
            Tuple of (up_rect, down_rect), or (None, None) if not single selection
        """
        if len(selected_indices) != 1:
            return None, None

        idx = list(selected_indices)[0]
        ax, ay = arrows[idx]

        if self.snap_enabled:
            ax = self.snap(ax)
            ay = self.snap(ay)

        sx, sy = self.world_to_screen(ax, ay)
        scale = 20 * self.camera_zoom

        up_rect = pygame.Rect(sx - 15, sy - scale - 30, 30, 30)
        down_rect = pygame.Rect(sx - 15, sy + scale - 5, 30, 30)

        return up_rect, down_rect
