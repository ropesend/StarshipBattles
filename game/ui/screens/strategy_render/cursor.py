"""Live-cursor overlays: move preview, ghost-hex, hover hex (PROJ-309 sub-phase 3.2)."""
from __future__ import annotations

import math
from typing import Any

import pygame

from game.core.hex_math import hex_to_pixel
from game.strategy.services.cargo_transfer_service import project_fleet_position
from game.ui.colors import HP_HEALTHY, ZONE_HIGHLIGHT


def draw_move_preview(r: Any, screen: Any) -> None:
    """Draw the move preview line from fleet's projected position to mouse cursor."""
    start_hex = project_fleet_position(r.scene.selected_fleet)

    fx, fy = hex_to_pixel(start_hex, r.hex_size)
    f_pos = r.camera.world_to_screen(pygame.math.Vector2(fx, fy))

    mx, my = pygame.mouse.get_pos()

    pygame.draw.line(screen, HP_HEALTHY, f_pos, (mx, my), 2)


def draw_ghost_hex(r: Any, screen: Any, ghost_hex: Any) -> None:
    """Draw a dashed-style ghost hex outline for the old MOVE destination."""
    cx, cy = hex_to_pixel(ghost_hex, r.hex_size)
    corners_px = []
    for i in range(6):
        angle_deg = 60 * i
        angle_rad = math.radians(angle_deg)
        px = cx + r.hex_size * math.cos(angle_rad)
        py = cy + r.hex_size * math.sin(angle_rad)
        corners_px.append(r.camera.world_to_screen(pygame.math.Vector2(px, py)))

    # Semi-transparent yellow outline for the ghost
    ghost_color = (255, 255, 100, 180)
    pygame.draw.lines(screen, ghost_color, True, corners_px, 2)


def draw_hover_hex(r: Any, screen: Any) -> None:
    """Draw highlight around the currently hovered hex."""
    cx, cy = hex_to_pixel(r.scene.hover_hex, r.hex_size)
    corners_px = []
    for i in range(6):
        angle_deg = 60 * i
        angle_rad = math.radians(angle_deg)
        px = cx + r.hex_size * math.cos(angle_rad)
        py = cy + r.hex_size * math.sin(angle_rad)
        corners_px.append(r.camera.world_to_screen(pygame.math.Vector2(px, py)))

    pygame.draw.lines(screen, ZONE_HIGHLIGHT, True, corners_px, 2)
