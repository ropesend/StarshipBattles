"""Hex grid snake-line drawing with viewport culling (PROJ-309 sub-phase 3.2)."""
from __future__ import annotations

from typing import Any

import pygame

from game.core.hex_math import pixel_to_hex
from game.ui.colors import COLORS


def draw_grid(r: Any, screen: Any) -> None:
    """Draw the hex grid with optimized snake lines."""
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
            pygame.draw.line(screen, grid_color, p1, p2, 1)

        if len(snake_points) > 1:
            pygame.draw.lines(screen, grid_color, False, snake_points, 1)
