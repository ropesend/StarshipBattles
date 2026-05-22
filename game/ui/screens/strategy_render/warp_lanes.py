"""System-to-system warp lane segments (PROJ-309 sub-phase 3.2)."""
from __future__ import annotations

from typing import Any

import pygame

from game.core.hex_math import hex_to_pixel
from game.ui.colors import WARP_LANE


def draw_warp_lanes(r: Any, screen: Any) -> None:
    """Draw warp lane connections between systems."""
    # Viewport culling bounds with margin
    margin = 100
    screen_w = r.screen_width
    screen_h = r.screen_height

    def is_on_screen(scr_pos) -> bool:
        """Check if a screen position is within the visible area."""
        return -margin <= scr_pos.x <= screen_w + margin and -margin <= scr_pos.y <= screen_h + margin

    drawn_pairs = set()
    # PROJ-477 Phase 5: live systems via the scene.world seam (no per-frame DTOs).
    for sys in r.world.iter_systems():
        sx, sy = hex_to_pixel(sys.global_location, r.hex_size)

        for wp in sys.warp_points:
            target_id = wp.destination_id
            target_sys = r.world.system_by_name(target_id)

            if target_sys:
                reciprocal_wp = next((w for w in target_sys.warp_points if w.destination_id == sys.name), None)

                if reciprocal_wp:
                    wx_a, wy_a = hex_to_pixel(wp.location, r.hex_size)
                    world_a = pygame.math.Vector2(sx + wx_a, sy + wy_a)

                    ts_x, ts_y = hex_to_pixel(target_sys.global_location, r.hex_size)
                    wx_b, wy_b = hex_to_pixel(reciprocal_wp.location, r.hex_size)
                    world_b = pygame.math.Vector2(ts_x + wx_b, ts_y + wy_b)

                    scr_a = r.camera.world_to_screen(world_a)
                    scr_b = r.camera.world_to_screen(world_b)

                    # Viewport culling: skip if both endpoints are off-screen
                    if not is_on_screen(scr_a) and not is_on_screen(scr_b):
                        continue

                    pair_key = tuple(sorted((f"{sys.name}_{wp.location}", f"{target_sys.name}_{reciprocal_wp.location}")))
                    if pair_key in drawn_pairs:
                        continue
                    drawn_pairs.add(pair_key)

                    pygame.draw.line(screen, WARP_LANE, scr_a, scr_b, 1)
                else:
                    ts_x, ts_y = hex_to_pixel(target_sys.global_location, r.hex_size)
                    world_b = pygame.math.Vector2(ts_x, ts_y)

                    wx_a, wy_a = hex_to_pixel(wp.location, r.hex_size)
                    world_a = pygame.math.Vector2(sx + wx_a, sy + wy_a)

                    scr_a = r.camera.world_to_screen(world_a)
                    scr_b = r.camera.world_to_screen(world_b)

                    # Viewport culling: skip if both endpoints are off-screen
                    if not is_on_screen(scr_a) and not is_on_screen(scr_b):
                        continue

                    pygame.draw.line(screen, WARP_LANE, scr_a, scr_b, 1)
