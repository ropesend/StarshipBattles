"""Hex occupancy outlines (PROJ-214) with turn-keyed cache.

The ``HexOutlineLayer`` owns the ``_hex_outline_cache`` and rebuilds it
only when ``scene.session.turn_number`` changes.
"""
from __future__ import annotations

import math
from typing import Any

import pygame

from game.core.hex_math import hex_to_pixel
from game.ui.colors import HEX_OUTLINE_OCCUPIED, HEX_OUTLINE_PLAYER_OWNED


class HexOutlineLayer:
    """Holds the turn-keyed cache for hex occupancy outlines."""

    def __init__(self) -> None:
        self._hex_outline_cache: Any = None
        self._hex_outline_cache_turn: int = -1

    def build_data(self, r: Any) -> dict:
        """Build mapping of occupied global hexes to ownership flags.

        Returns:
            Dict mapping HexCoord -> (has_player_owned: bool, has_non_player: bool)
        """
        player_id = r.scene.session.player_empire.id if r.scene.session.player_empire else None
        result = {}

        # 1. Planets (from spatial index)
        for global_hex, planets in r.galaxy._global_hex_planets.items():
            has_player = False
            has_non_player = False
            for planet in planets:
                if planet.owner_id is not None and planet.owner_id == player_id:
                    has_player = True
                else:
                    has_non_player = True
            result[global_hex] = (has_player, has_non_player)

        # 2. Zones (stars, Dyson Spheres, storms)
        for global_hex, zones in r.galaxy._global_hex_zones.items():
            entry = result.get(global_hex, (False, False))
            zone_has_player = entry[0]
            zone_has_non_player = entry[1]
            for zone_obj in zones:
                if hasattr(zone_obj, 'owner_id') and zone_obj.owner_id == player_id:
                    zone_has_player = True
                else:
                    zone_has_non_player = True
            result[global_hex] = (zone_has_player, zone_has_non_player)

        # 3. Warp points (always non-player)
        for global_hex in r.galaxy._global_hex_warp_points:
            entry = result.get(global_hex, (False, False))
            result[global_hex] = (entry[0], True)

        # 4. Fleets (check ownership per fleet)
        for empire in r.empires:
            for fleet in empire.fleets:
                if fleet.location is None:
                    continue
                entry = result.get(fleet.location, (False, False))
                if fleet.owner_id == player_id:
                    result[fleet.location] = (True, entry[1])
                else:
                    result[fleet.location] = (entry[0], True)

        return result

    def get_data(self, r: Any) -> dict:
        """Get cached hex outline data, rebuilding if turn changed."""
        current_turn = getattr(r.scene.session, 'turn_number', 0)
        if self._hex_outline_cache is None or self._hex_outline_cache_turn != current_turn:
            self._hex_outline_cache = self.build_data(r)
            self._hex_outline_cache_turn = current_turn
        return self._hex_outline_cache

    def draw(self, r: Any, screen: Any) -> None:
        """Draw inner hex outlines for occupied hexes.

        Red outline for any object, white for player-owned,
        dual concentric outlines when both are present.
        """
        outline_data = self.get_data(r)
        if not outline_data:
            return

        sw = r.screen_width
        sh = r.screen_height
        margin = 50

        for global_hex, (has_player, has_non_player) in outline_data.items():
            cx, cy = hex_to_pixel(global_hex, r.hex_size)
            screen_center = r.camera.world_to_screen(pygame.math.Vector2(cx, cy))

            if screen_center.x < -margin or screen_center.x > sw + margin:
                continue
            if screen_center.y < -margin or screen_center.y > sh + margin:
                continue

            # NOTE: dispatch through renderer wrapper so tests can monkey-patch.
            if has_player and has_non_player:
                r._draw_inner_hex(screen, cx, cy, 0.90, HEX_OUTLINE_PLAYER_OWNED)
                r._draw_inner_hex(screen, cx, cy, 0.80, HEX_OUTLINE_OCCUPIED)
            elif has_player:
                r._draw_inner_hex(screen, cx, cy, 0.88, HEX_OUTLINE_PLAYER_OWNED)
            else:
                r._draw_inner_hex(screen, cx, cy, 0.88, HEX_OUTLINE_OCCUPIED)


def draw_inner_hex(r: Any, screen: Any, cx: float, cy: float, scale: float, color: tuple) -> None:
    """Draw a single inner hex outline at the given scale factor.

    Args:
        r: Renderer (for hex_size and camera).
        screen: Pygame surface to draw on.
        cx, cy: World-space center of the hex.
        scale: Scale factor (0.0-1.0) relative to hex_size.
        color: RGB tuple for the outline color.
    """
    inner_size = r.hex_size * scale
    corners = []
    for i in range(6):
        angle_rad = math.radians(60 * i)
        px = cx + inner_size * math.cos(angle_rad)
        py = cy + inner_size * math.sin(angle_rad)
        corners.append(r.camera.world_to_screen(pygame.math.Vector2(px, py)))

    pygame.draw.lines(screen, color, True, corners, 2)
