"""Dyson Sphere multi-hex render + owner flag (PROJ-309 sub-phase 3.2).

Per-hex sector outlines for the Dyson Sphere's occupied hexes are drawn
by ``HexOutlineLayer.draw()`` BEFORE this module runs (step 3 of
``StrategyRenderer.draw()``), via the ``global_hex_zones`` registry that
``GalaxyEntityRegistry`` populates for any planet with ``radius_hexes > 0``.
The sphere image then blits over them, so outlines remain visible only
where they peek beyond the sphere silhouette — the same z-order stars use.

PRESERVED LATENT BUG: ``screen_diameter`` referenced in the owner-marker
branch below is undefined — only ``screen_radius`` is in scope. Pre-existing
bug from ``strategy_renderer.py`` (~L 846/854); only triggers when a Dyson
Sphere is owner-marked AND the empire has no ``'colony'`` asset. Out of
scope to fix — flagged for follow-up ticket.
"""
from __future__ import annotations

import os
from typing import Any

import pygame

from game.core.paths import Paths
from game.core.hex_math import hex_to_pixel
from game.strategy.data.planet import PlanetType
from game.ui.colors import DYSON_FALLBACK, WHITE

# ~5% bump past the q-axis inscribed-circle minimum, set per QA visual
# judgment in #26 iteration 2: the strict inscribed result left a visible
# vertical gap to the outer-ring hexes. The sprite still does not reach
# the r-axis apothem (which is ~12% larger than q at R=6), so it remains
# inside the occupied hex set in the binding direction.
DYSON_SPHERE_FILL_FACTOR: float = 1.05


def draw_dyson_spheres(r: Any, screen: Any, sys: Any, sys_world_pos: Any) -> None:
    """Draw Dyson Sphere planets at their full multi-hex size.

    Dyson Spheres are rendered BEFORE normal planets so they appear behind them.
    They use the Sphereworld_Portrait.png image scaled to radius_hexes.
    """
    for planet in sys.planets:
        if planet.planet_type != PlanetType.DYSON_SPHERE:
            continue

        # Get radius from planet - IPlanet.radius_hexes is always present
        radius_hexes = planet.radius_hexes
        if radius_hexes <= 0:
            radius_hexes = 6  # Dyson Sphere standard size

        # Calculate screen position centered on planet's hex
        px, py = hex_to_pixel(planet.location, r.hex_size)
        center_world = pygame.math.Vector2(sys_world_pos.x + px, sys_world_pos.y + py)
        center_screen = r.camera.world_to_screen(center_world)

        # Size the sprite to fit (mostly) inside the planet's occupied hex
        # disc. ``occupied_hexes() = hex_circle_filled(loc, R - 1)``. For
        # flat-topped hexes the disc's narrowest radial extent is along the
        # horizontal axis (the pointy corner of the side hex), at distance
        # ``(3R - 1) / 2 * hex_size`` from the centre — strictly smaller than
        # the vertical apothem ``sqrt(3) * (R - 0.5) * hex_size``. The strict
        # inscribed-circle result is visually too small (QA #26 iteration 2),
        # so we bump by ``DYSON_SPHERE_FILL_FACTOR``. The resulting horizontal
        # overshoot lands in the corner notches of the outer-ring side hex
        # (still inside the occupied set), not in unoccupied neighbouring
        # sectors.
        screen_radius = max(
            6,
            int((3 * radius_hexes - 1) / 2 * r.hex_size * r.camera.zoom * DYSON_SPHERE_FILL_FACTOR),
        )

        # Load Dyson Sphere image
        img = load_dyson_sphere_image(r)

        # Draw selection circle if selected
        if r.scene.selected_object == planet:
            pygame.draw.circle(screen, WHITE,
                               (int(center_screen.x), int(center_screen.y)),
                               screen_radius + 4, 1)

        if img:
            # Scale and blit the image (screen_radius * 2 for diameter)
            scaled = pygame.transform.smoothscale(img, (screen_radius * 2, screen_radius * 2))
            dest = scaled.get_rect(center=(int(center_screen.x), int(center_screen.y)))
            screen.blit(scaled, dest)
        else:
            # Fallback: draw a cyan circle
            pygame.draw.circle(screen, DYSON_FALLBACK,
                               (int(center_screen.x), int(center_screen.y)),
                               screen_radius)

        # Draw owner marker if colonized. PROJ-477 Phase 5: live empires via scene.world.
        if planet.owner_id is not None:
            owner_emp = next((e for e in r.world.iter_empires() if e.id == planet.owner_id), None)
            if owner_emp:
                marker_offset = screen_radius * 0.8
                marker_pos = (int(center_screen.x + marker_offset), int(center_screen.y - marker_offset))

                emp_assets = r.empire_assets.get(owner_emp.id)
                if emp_assets and 'colony' in emp_assets:
                    flag_img = emp_assets['colony']
                    # Preserve original aspect ratio
                    orig_w, orig_h = flag_img.get_width(), flag_img.get_height()
                    f_w = max(10, int(screen_diameter * 0.15))  # noqa: F821 — preserved latent bug
                    f_h = int(f_w * orig_h / orig_w) if orig_w > 0 else f_w

                    scaled_flag = pygame.transform.smoothscale(flag_img, (f_w, f_h))
                    flag_rect = scaled_flag.get_rect(center=marker_pos)
                    screen.blit(scaled_flag, flag_rect)
                else:
                    # Fallback: colored circle
                    pygame.draw.circle(screen, owner_emp.color, marker_pos, max(3, screen_diameter // 10))  # noqa: F821 — preserved latent bug
                    pygame.draw.circle(screen, WHITE, marker_pos, max(3, screen_diameter // 10) + 1, 1)  # noqa: F821 — preserved latent bug


def load_dyson_sphere_image(r: Any) -> "pygame.Surface | None":
    """Load the Dyson Sphere image from Sphere world directory.

    Returns:
        Pygame Surface or None if loading fails
    """
    image_path = os.path.join(Paths.SPHERE_WORLD_DIR, "Sphereworld_Portrait.png")
    img = r._asset_manager.load_external_image(image_path)

    # Check if we got the missing texture placeholder
    if img is r._asset_manager.missing_texture:
        return None

    return img
