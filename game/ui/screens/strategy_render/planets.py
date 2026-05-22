"""Single-planet sprite rendering + planet-image loaders (PROJ-309 sub-phase 3.2).

NOTE: The polar-angle table for laying out multi-planet groups is duplicated
in ``strategy_click_dispatcher.py`` (search for "must match strategy_renderer.py
Rev 5 values"). Deduplication is OUT OF SCOPE for this sub-phase but flagged
for follow-up.
"""
from __future__ import annotations

from typing import Any

import pygame

from game.ui.colors import PLANET_FALLBACK, WHITE


def draw_planet_sprite(r: Any, screen: Any, planet: Any, center_pos: Any, size: int) -> None:
    """Draw a single planet sprite with colony marker if owned."""
    img = None

    # Load planet image from Planets_V3 using image_id
    if planet.image_id:
        img = load_planet_v3_image(r, planet.image_id)

    if img:
        scaled = pygame.transform.smoothscale(img, (size * 2, size * 2))
        dest = scaled.get_rect(center=(int(center_pos.x), int(center_pos.y)))
        screen.blit(scaled, dest)
    else:
        # Fallback: gray circle if no image_id (should not happen for new planets)
        pygame.draw.circle(screen, PLANET_FALLBACK, (int(center_pos.x), int(center_pos.y)), size)

    # Owner Marker (Colony Flag). PROJ-477 Phase 5: live empires via scene.world.
    if planet.owner_id is not None:
        owner_emp = next((e for e in r.world.iter_empires() if e.id == planet.owner_id), None)

        if owner_emp:
            flag_offset = size * 0.8
            marker_pos = (int(center_pos.x + flag_offset), int(center_pos.y - flag_offset))

            emp_assets = r.empire_assets.get(owner_emp.id)
            if emp_assets and 'colony' in emp_assets:
                flag_img = emp_assets['colony']
                # Preserve original aspect ratio
                orig_w, orig_h = flag_img.get_width(), flag_img.get_height()
                f_w = max(10, int(size * 1.5))
                f_h = int(f_w * orig_h / orig_w) if orig_w > 0 else f_w

                scaled_flag = pygame.transform.smoothscale(flag_img, (f_w, f_h))
                flag_rect = scaled_flag.get_rect(bottomleft=marker_pos)
                screen.blit(scaled_flag, flag_rect)
            else:
                pygame.draw.circle(screen, owner_emp.color, marker_pos, max(3, int(size / 3)))
                pygame.draw.circle(screen, WHITE, marker_pos, max(3, int(size / 3)) + 1, 1)


def load_planet_v3_image(r: Any, image_id: str) -> Any:
    """Load a planet image from the Planets_V3 directory.

    Args:
        r: Renderer (for asset_manager access).
        image_id: Filename of the planet image (e.g., "planet_5_994_1769750020702.png")

    Returns:
        Pygame Surface or None if loading fails
    """
    if not image_id:
        return None

    # Load planet image at 512px resolution (optimal for portraits)
    # Uses resolution-aware loading with fallback chain (PROJ-54 Phase 10)
    img = r._asset_manager.load_planet_image(image_id, requested_size=512)

    # Check if we got the missing texture placeholder
    if img is r._asset_manager.missing_texture:
        return None

    return img
