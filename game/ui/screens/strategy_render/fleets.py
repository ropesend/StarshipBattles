"""Fleet icons + race shield flags + selection ring + path projection
(PROJ-309 sub-phase 3.2)."""
from __future__ import annotations

import logging
from typing import Any

import pygame

from game.core.hex_math import hex_to_pixel
from game.ui.colors import FLEET_SELECTED, PATH_LABEL, PATH_MOVE, PATH_WARP

logger = logging.getLogger(__name__)


def draw_fleets(r: Any, screen: Any) -> None:
    """Draw all fleets and their movement paths."""
    for emp in r.empires:
        for f in emp.fleets:
            if f.location is None:
                logger.warning(f"Skipping render for Fleet {f.id} (Owner {f.owner_id}): Location is None")
                continue

            fx, fy = hex_to_pixel(f.location, r.hex_size)
            f_screen = r.camera.world_to_screen(pygame.math.Vector2(fx, fy))

            fleet_on_screen = (0 <= f_screen.x <= r.screen_width and 0 <= f_screen.y <= r.screen_height)

            if fleet_on_screen:
                emp_assets = r.empire_assets.get(emp.id)
                if emp_assets and 'fleet' in emp_assets:
                    img = emp_assets['fleet']
                    size = int(24 * r.camera.zoom)
                    if size < 12:
                        size = 12
                    if size > 64:
                        size = 64

                    scaled = pygame.transform.smoothscale(img, (size, size))
                    dest = scaled.get_rect(center=(int(f_screen.x), int(f_screen.y)))

                    screen.blit(scaled, dest)

                    # Draw shield flag alongside ship icon (if race has custom flag)
                    if emp_assets and 'fleet_flag' in emp_assets:
                        flag_img = emp_assets['fleet_flag']
                        # Shield flag is smaller, positioned to top-right of ship icon
                        flag_size = max(8, int(size * 0.6))
                        scaled_flag = pygame.transform.smoothscale(flag_img, (flag_size, flag_size))
                        # Position flag at top-right corner of ship icon
                        flag_x = int(f_screen.x + size * 0.4)
                        flag_y = int(f_screen.y - size * 0.4)
                        flag_dest = scaled_flag.get_rect(center=(flag_x, flag_y))
                        screen.blit(scaled_flag, flag_dest)

                    if r.scene.selected_fleet == f:
                        pygame.draw.rect(screen, FLEET_SELECTED, dest.inflate(4, 4), 1)
                else:
                    size = 10 * r.camera.zoom
                    if size < 8:
                        size = 8
                    if size > 30:
                        size = 30

                    points = [
                        (f_screen.x, f_screen.y - size),
                        (f_screen.x - size / 2, f_screen.y + size / 2),
                        (f_screen.x + size / 2, f_screen.y + size / 2)
                    ]

                    color = emp.color
                    if r.scene.selected_fleet == f:
                        color = FLEET_SELECTED

                    pygame.draw.polygon(screen, color, points)

            # Draw path for selected fleet
            # NOTE: dispatch through renderer wrapper so tests can monkey-patch.
            if f == r.scene.selected_fleet:
                r._draw_fleet_path(screen, f, f_screen)


def draw_fleet_path(r: Any, screen: Any, fleet: Any, fleet_screen_pos: Any) -> None:
    """Draw the movement path for a fleet.

    PROJ-472 Phase 1C: path segments are read through the facade
    (``facade.fleets.path_projection(fleet_id, max_turns=50)``) instead of
    the live-session ``get_fleet_path_projection`` bypass. The facade returns
    the same ``List[dict]`` segment shape, so this is a one-for-one swap with
    no per-frame DTO allocation. NOTE the signature difference: the facade
    takes a ``fleet_id`` (int), so pass ``fleet.id``, not the fleet object.
    """
    segments = r.scene.facade.fleets.path_projection(fleet.id, max_turns=50)

    start_screen = fleet_screen_pos
    font = None
    if segments and r.camera.zoom >= 0.5:
        font = r._get_font(18, bold=True)

    for seg in segments:
        end_hex = seg['end']
        is_warp = seg['is_warp']
        turn_idx = seg['turn']

        ex, ey = hex_to_pixel(end_hex, r.hex_size)
        end_screen = r.camera.world_to_screen(pygame.math.Vector2(ex, ey))

        start_on = (0 <= start_screen.x <= r.screen_width and 0 <= start_screen.y <= r.screen_height)
        end_on = (0 <= end_screen.x <= r.screen_width and 0 <= end_screen.y <= r.screen_height)

        if not start_on and not end_on:
            start_screen = end_screen
            continue

        color = PATH_MOVE
        width = 2
        if is_warp:
            color = PATH_WARP
            width = 1

        pygame.draw.line(screen, color, start_screen, end_screen, width)

        if font and not is_warp and end_on:
            txt = font.render(str(turn_idx), True, PATH_LABEL)
            tr = txt.get_rect(center=(end_screen.x, end_screen.y))
            screen.blit(txt, tr)

        start_screen = end_screen
