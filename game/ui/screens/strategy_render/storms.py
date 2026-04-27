"""Storm nebulae overlay rendering (PROJ-309 sub-phase 3.2).

Renders storm nebulae as full image overlays at high zoom and as colored
hex circles at low zoom. Storms are drawn BEFORE Dyson Spheres and planets
so they sit behind those layers.
"""
from __future__ import annotations

import math
from typing import Any

import pygame

from game.core.hex_math import HexCoord, hex_to_pixel
from game.ui.colors import (
    STORM_DARK_NEBULA, STORM_FALLBACK, STORM_GRAVITATIONAL,
    STORM_ION, STORM_PLASMA, STORM_RADIATION,
)


def draw_storms(r: Any, screen: Any, sys: Any, sys_world_pos: Any) -> None:
    """Draw storm nebulae overlays for a star system.

    Storms are rendered BEFORE Dyson Spheres and planets so they appear behind them.
    Each storm uses a nebulae image scaled to cover its hex extent.
    """
    # Skip if system has no storms
    # IStarSystem.storms is always present (List)
    if not sys.storms:
        return

    # Skip detailed rendering at low zoom - just draw colored hex fills
    if r.camera.zoom < 0.3:
        draw_storms_low_detail(r, screen, sys, sys_world_pos)
        return

    # Color tints per storm type (RGBA tint applied via colorkey/blend)
    storm_tints = {
        'ion_storm': STORM_ION,
        'plasma_storm': STORM_PLASMA,
        'gravitational_anomaly': STORM_GRAVITATIONAL,
        'radiation_belt': STORM_RADIATION,
        'dark_nebula': STORM_DARK_NEBULA,
    }

    for storm in sys.storms:
        # Get storm hexes (local coordinates)
        occupied = storm.occupied_hexes
        if not occupied:
            continue

        # Calculate bounding box in world coordinates
        min_q = min(h.q for h in occupied)
        max_q = max(h.q for h in occupied)
        min_r = min(h.r for h in occupied)
        max_r = max(h.r for h in occupied)

        # Convert bounding box corners to pixel positions
        corner_hexes = [
            HexCoord(min_q, min_r),
            HexCoord(max_q, min_r),
            HexCoord(min_q, max_r),
            HexCoord(max_q, max_r),
        ]

        # Calculate bounding box in world pixels
        pixel_coords = []
        for h in corner_hexes:
            px, py = hex_to_pixel(h, r.hex_size)
            pixel_coords.append((sys_world_pos.x + px, sys_world_pos.y + py))

        world_min_x = min(p[0] for p in pixel_coords) - r.hex_size
        world_max_x = max(p[0] for p in pixel_coords) + r.hex_size
        world_min_y = min(p[1] for p in pixel_coords) - r.hex_size
        world_max_y = max(p[1] for p in pixel_coords) + r.hex_size

        # Viewport culling
        screen_tl = r.camera.world_to_screen(pygame.math.Vector2(world_min_x, world_min_y))
        screen_br = r.camera.world_to_screen(pygame.math.Vector2(world_max_x, world_max_y))

        if screen_br.x < 0 or screen_tl.x > r.screen_width:
            continue
        if screen_br.y < 0 or screen_tl.y > r.screen_height:
            continue

        # Calculate center position for rendering
        center_x = (world_min_x + world_max_x) / 2
        center_y = (world_min_y + world_max_y) / 2
        center_screen = r.camera.world_to_screen(pygame.math.Vector2(center_x, center_y))

        # Calculate screen dimensions
        screen_width = int((world_max_x - world_min_x) * r.camera.zoom)
        screen_height = int((world_max_y - world_min_y) * r.camera.zoom)

        # Ensure minimum size
        screen_width = max(20, screen_width)
        screen_height = max(20, screen_height)

        # Load nebulae image using image_variant as seed
        img = r._asset_manager.get_random_from_group(
            'nebulae', 'default', seed_id=storm.image_variant
        )

        if img:
            # Scale image to cover storm extent
            scaled = pygame.transform.smoothscale(img, (screen_width, screen_height))

            # Apply alpha based on intensity (max 180 = ~70% opacity)
            alpha = int(storm.intensity * 180)
            scaled.set_alpha(alpha)

            # Apply color tint if available
            tint = storm_tints.get(storm.storm_type)
            if tint:
                # Create tinted version using per-pixel multiply
                tinted = scaled.copy()
                tinted.fill(tint + (0,), special_flags=pygame.BLEND_RGB_MULT)
                scaled = tinted

            # Blit to screen
            dest = scaled.get_rect(center=(int(center_screen.x), int(center_screen.y)))
            screen.blit(scaled, dest)
        else:
            # Fallback: draw semi-transparent colored polygon
            tint = storm_tints.get(storm.storm_type, STORM_FALLBACK)
            for h in occupied:
                hx, hy = hex_to_pixel(h, r.hex_size)
                h_world = pygame.math.Vector2(sys_world_pos.x + hx, sys_world_pos.y + hy)
                h_screen = r.camera.world_to_screen(h_world)

                # Draw hex fill
                corners = []
                for i in range(6):
                    angle_deg = 60 * i
                    angle_rad = math.radians(angle_deg)
                    corner_x = h_screen.x + r.hex_size * r.camera.zoom * math.cos(angle_rad)
                    corner_y = h_screen.y + r.hex_size * r.camera.zoom * math.sin(angle_rad)
                    corners.append((corner_x, corner_y))

                # Create transparent surface for hex
                hex_surf = pygame.Surface((int(r.hex_size * 2 * r.camera.zoom + 4),
                                          int(r.hex_size * 2 * r.camera.zoom + 4)),
                                          pygame.SRCALPHA)
                offset_corners = [(c[0] - h_screen.x + r.hex_size * r.camera.zoom + 2,
                                  c[1] - h_screen.y + r.hex_size * r.camera.zoom + 2)
                                 for c in corners]
                pygame.draw.polygon(hex_surf, tint + (int(storm.intensity * 100),), offset_corners)
                dest = hex_surf.get_rect(center=(int(h_screen.x), int(h_screen.y)))
                screen.blit(hex_surf, dest)


def draw_storms_low_detail(r: Any, screen: Any, sys: Any, sys_world_pos: Any) -> None:
    """Draw storm zones at low zoom using simple colored hex fills."""
    storm_tints = {
        'ion_storm': STORM_ION + (80,),
        'plasma_storm': STORM_PLASMA + (80,),
        'gravitational_anomaly': STORM_GRAVITATIONAL + (80,),
        'radiation_belt': STORM_RADIATION + (80,),
        'dark_nebula': STORM_DARK_NEBULA + (80,),
    }

    for storm in sys.storms:
        tint = storm_tints.get(storm.storm_type, (100, 100, 100, 80))

        for h in storm.occupied_hexes:
            hx, hy = hex_to_pixel(h, r.hex_size)
            h_world = pygame.math.Vector2(sys_world_pos.x + hx, sys_world_pos.y + hy)
            h_screen = r.camera.world_to_screen(h_world)

            # Skip if off-screen
            if h_screen.x < -50 or h_screen.x > r.screen_width + 50:
                continue
            if h_screen.y < -50 or h_screen.y > r.screen_height + 50:
                continue

            # Draw simple colored circle at hex center
            radius = max(2, int(r.hex_size * r.camera.zoom * 0.5))
            pygame.draw.circle(screen, tint[:3], (int(h_screen.x), int(h_screen.y)), radius)
