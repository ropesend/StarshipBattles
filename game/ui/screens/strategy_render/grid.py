"""Hex grid snake-line drawing with viewport culling and surface cache.

PROJ-309 sub-phase 3.2: extracted from the renderer.
PROJ-374: introduced ``GridLayer`` with a quantized property-keyed surface
cache. ``draw_grid`` is preserved for back-compat; new callers should use
``GridLayer.draw``.
"""
from __future__ import annotations

from typing import Any

import pygame

from game.core.hex_math import pixel_to_hex
from game.ui.colors import COLORS


# 0.1 world-unit position tolerance, 0.01 zoom tolerance. Sub-tolerance
# motion is sub-pixel and produces a cache hit.
_POS_QUANT = 1   # round() ndigits arg → 0.1 quantum
_ZOOM_QUANT = 2  # round() ndigits arg → 0.01 quantum


def _render_grid_to_surface(r: Any, target_surface: Any) -> None:
    """Render the hex grid onto ``target_surface``.

    Pure function of ``(camera, hex_size, viewport)`` — no other state read.
    Extracted from the original ``draw_grid`` body so cache logic can wrap it
    and tests can mock the heavy work.
    """
    # 1. Culling
    tl_world = r.camera.screen_to_world((0, 0))
    tr_world = r.camera.screen_to_world((r.screen_width, 0))
    bl_world = r.camera.screen_to_world((0, r.screen_height))
    br_world = r.camera.screen_to_world((r.screen_width, r.screen_height))

    corners = [tl_world, tr_world, bl_world, br_world]
    q_vals = []
    r_vals = []
    for p in corners:
        h = pixel_to_hex(p.x, p.y, r.hex_size)
        q_vals.append(h.q)
        r_vals.append(h.r)

    min_q = min(q_vals) - 1
    max_q = max(q_vals) + 1
    min_r = min(r_vals) - 1
    max_r = max(r_vals) + 1

    hex_count = (max_q - min_q) * (max_r - min_r)
    if hex_count > 80000:
        return

    grid_color = COLORS['border_subtle']

    screen_hex_size = r.hex_size * r.camera.zoom
    SQRT3 = 1.73205080757

    s = screen_hex_size
    col_stride_x = 1.5 * s
    row_stride_y = SQRT3 * s
    half_row_height = row_stride_y / 2

    cam_x = r.camera.position.x
    cam_y = r.camera.position.y
    base_x = (r.camera.width / 2) - cam_x * r.camera.zoom + r.camera.offset_x
    base_y = (r.camera.height / 2) - cam_y * r.camera.zoom + r.camera.offset_y

    v_tl = pygame.math.Vector2(-0.5 * s, -half_row_height)
    v_l = pygame.math.Vector2(-1.0 * s, 0)
    v_bl = pygame.math.Vector2(-0.5 * s, half_row_height)
    v_tr = pygame.math.Vector2(0.5 * s, -half_row_height)

    for q in range(min_q, max_q + 2):
        cx = base_x + q * col_stride_x

        if not (-50 < cx < r.screen_width + 50):
            continue

        col_y_offset = base_y + (row_stride_y * 0.5 * q)

        start_r = int((-50 - col_y_offset) / row_stride_y) - 1
        end_r = int((r.screen_height + 50 - col_y_offset) / row_stride_y) + 1

        snake_points = []

        cy_start = col_y_offset + row_stride_y * start_r
        snake_points.append((cx + v_tl.x, cy_start + v_tl.y))

        for ri in range(start_r, end_r):
            cy = col_y_offset + row_stride_y * ri

            snake_points.append((cx + v_l.x, cy + v_l.y))
            snake_points.append((cx + v_bl.x, cy + v_bl.y))

            p1 = (cx + v_tl.x, cy + v_tl.y)
            p2 = (cx + v_tr.x, cy + v_tr.y)
            pygame.draw.line(target_surface, grid_color, p1, p2, 1)

        if len(snake_points) > 1:
            pygame.draw.lines(target_surface, grid_color, False, snake_points, 1)


def draw_grid(r: Any, screen: Any) -> None:
    """Draw the hex grid directly onto ``screen``.

    Uncached fast path retained for back-compat with existing direct callers
    (e.g. tests). Production rendering goes through ``GridLayer.draw``.
    """
    _render_grid_to_surface(r, screen)


class GridLayer:
    """Property-keyed surface cache for the strategy hex grid.

    Mirrors the pattern in ``BackgroundLayer`` and ``HexOutlineLayer``:
    one cache entry, viewport-sized surface allocated once on first miss
    and reused via ``fill((0,0,0,0))`` + redraw on subsequent misses. The
    cache key is a quantized snapshot of camera state so smooth pan/zoom
    animations don't thrash.

    Below ``zoom < 0.4`` the renderer's existing cutoff means there's
    nothing to draw; we short-circuit at the top of ``draw`` before any
    cache work.
    """

    def __init__(self) -> None:
        self._cache_surface: pygame.Surface | None = None
        self._cache_key: tuple | None = None

    def _compute_key(self, r: Any) -> tuple:
        """Compute the quantized cache key for the current renderer state.

        Every input that affects the rendered bitmap appears here. If a new
        input is introduced (e.g. dynamic grid color from a theme), it must
        be added or the cache will go stale.
        """
        cam = r.camera
        return (
            round(cam.position.x, _POS_QUANT),
            round(cam.position.y, _POS_QUANT),
            round(cam.zoom, _ZOOM_QUANT),
            r.screen_width,
            r.screen_height,
            r.hex_size,
        )

    def _ensure_surface(self, r: Any) -> pygame.Surface:
        """Return a viewport-sized SRCALPHA cache surface, reallocating only
        when the viewport size changes."""
        target_size = (r.screen_width, r.screen_height)
        if (
            self._cache_surface is None
            or self._cache_surface.get_size() != target_size
        ):
            self._cache_surface = pygame.Surface(target_size, pygame.SRCALPHA)
        return self._cache_surface

    def draw(self, r: Any, screen: Any) -> None:
        """Draw the grid via the cache, blitting to ``screen``."""
        if r.camera.zoom < 0.4:
            return

        key = self._compute_key(r)
        if key == self._cache_key and self._cache_surface is not None:
            screen.blit(self._cache_surface, (0, 0))
            return

        surface = self._ensure_surface(r)
        surface.fill((0, 0, 0, 0))
        _render_grid_to_surface(r, surface)
        self._cache_key = key
        screen.blit(surface, (0, 0))
