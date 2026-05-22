"""Systems / stars / colony markers / system-detail dispatch (PROJ-309 sub-phase 3.2).

Composes ``planets``, ``storms``, ``dyson_spheres``, and warp-point rendering
for each visible star system.

PRESERVED CODE SMELL: ``_temp_screen_pos`` and ``_temp_draw_r`` are written
onto planet domain objects in ``_draw_system_details`` to thread layout
results between two passes. This is render data on domain models. Out of
scope to fix here — flagged for follow-up ticket.
"""
from __future__ import annotations

from typing import Any

import pygame

from game.core.hex_math import hex_to_pixel
from game.strategy.data.planet import PlanetType
from game.ui.colors import STAR_LABEL, WARPPOINT_FALLBACK, WHITE
from game.ui.utils import scale_and_rotate_image

from game.ui.screens.strategy_render.context import hex_radius_to_screen

# Animation constants
WARP_POINT_ROTATION_SPEED = 12.0  # degrees per second


def draw_systems(r: Any, screen: Any) -> None:
    """Draw all star systems with stars, planets, and warp points."""
    tl = r.camera.screen_to_world((0, 0))
    br = r.camera.screen_to_world((r.screen_width, r.screen_height))

    margin = 600
    min_x, max_x = min(tl.x, br.x) - margin, max(tl.x, br.x) + margin
    min_y, max_y = min(tl.y, br.y) - margin, max(tl.y, br.y) + margin

    # PROJ-477 Phase 5: live systems via the scene.world seam (no per-frame DTOs).
    for sys in r.world.iter_systems():
        hx, hy = hex_to_pixel(sys.global_location, r.hex_size)
        world_pos = pygame.math.Vector2(hx, hy)

        if not (min_x < world_pos.x < max_x and min_y < world_pos.y < max_y):
            continue

        # Draw Colony Marker when zoomed out
        # NOTE: dispatch through the renderer's wrapper methods so tests that
        # monkey-patch ``renderer._draw_system_details`` etc. continue to work.
        r._draw_colony_marker(screen, sys, world_pos)

        primary = sys.primary_star
        if primary:
            for star in sys.stars:
                is_primary = star == primary
                is_selected = r.scene.selected_object == sys
                r._draw_star(screen, star, (hx, hy), sys.name, is_primary, is_selected)

        if r.camera.zoom >= 0.5:
            r._draw_system_details(screen, sys, world_pos)


def load_star_image(r: Any, star: Any) -> Any:
    """Load a star image using the star's image_id.

    Uses the resolution-aware loader from AssetManager (1024px for strategy view).
    Falls back to None if star has no image_id or image not found.

    Args:
        r: Renderer (for asset_manager).
        star: Star object with image_id attribute.

    Returns:
        pygame.Surface or None
    """
    if not star.image_id:
        return None
    img = r._asset_manager.load_star_image(star.image_id, 1024)
    if img and img != r._asset_manager.get_missing_texture():
        return img
    return None


def draw_colony_marker(r: Any, screen: Any, sys: Any, world_pos: Any) -> None:
    """Draw colony ownership marker at low zoom levels.

    Only draws when zoom < 0.5 and system has owned planets.
    Uses first owned planet's owner color.

    Args:
        r: Renderer.
        screen: pygame.Surface to draw on.
        sys: StarSystem object.
        world_pos: pygame.math.Vector2 - system center in world coords.
    """
    if r.camera.zoom >= 0.5:
        return

    owned_planets = [p for p in sys.planets if p.owner_id is not None]
    if not owned_planets:
        return

    first_owner_id = owned_planets[0].owner_id
    owner_emp = next((e for e in r.world.iter_empires() if e.id == first_owner_id), None)
    if not owner_emp:
        return

    offset_world = pygame.math.Vector2(-0.75 * r.hex_size, -0.75 * r.hex_size)
    marker_world = world_pos + offset_world
    marker_screen = r.camera.world_to_screen(marker_world)

    pygame.draw.circle(screen, owner_emp.color, (int(marker_screen.x), int(marker_screen.y)), 5)
    pygame.draw.circle(screen, WHITE, (int(marker_screen.x), int(marker_screen.y)), 6, 1)


def draw_star(r: Any, screen: Any, star: Any, system_center: tuple, system_name: str, is_primary: bool, is_selected_system: bool) -> None:
    """Render a single star with image, selection highlight, and label.

    Uses star.image_id with core metadata from star_metadata.json for
    proper sizing — the visible core matches the hex radius, corona
    extends freely beyond.
    """
    hx, hy = system_center
    local_pixel_x, local_pixel_y = hex_to_pixel(star.location, r.hex_size)
    star_screen_pos = r.camera.world_to_screen(
        pygame.math.Vector2(hx + local_pixel_x, hy + local_pixel_y)
    )

    screen_star_r = hex_radius_to_screen(star.radius_hexes, r.hex_size, r.camera.zoom)

    # Selection highlight (before star image)
    if is_selected_system and is_primary:
        pygame.draw.circle(screen, WHITE, star_screen_pos, screen_star_r + 4, 1)

    # Star image with core-based sizing, or fallback to colored circle
    star_img = load_star_image(r, star)
    if star_img:
        # Use core metadata to size the image so the visible core
        # matches the hex radius — corona extends beyond
        core_info = r._asset_manager.get_star_core_info(star.image_id)
        core_radius_frac = max(core_info.get('radiusCore', 0.25), 0.05)
        center_x_frac = core_info.get('centerX', 0.5)
        center_y_frac = core_info.get('centerY', 0.5)

        # Progressive scaling boost: larger stars need proportionally more
        # screen space to visually fill their hex footprint. No effect at
        # radius 1, adds ~1 hex ring of extra size by radius 6.
        radius_boost = 1.0 + (star.radius_hexes - 1) * 0.05

        # Scale so core in the image matches the hex screen size.
        core_diameter_frac = core_radius_frac * 2
        display_size = int((screen_star_r * radius_boost) / core_diameter_frac)
        display_size = max(display_size, 4)  # minimum size

        scaled_img = pygame.transform.smoothscale(star_img, (display_size, display_size))

        # Offset for off-center cores
        offset_x = int((0.5 - center_x_frac) * display_size)
        offset_y = int((0.5 - center_y_frac) * display_size)
        dest_rect = scaled_img.get_rect(
            center=(int(star_screen_pos.x) + offset_x, int(star_screen_pos.y) + offset_y)
        )
        screen.blit(scaled_img, dest_rect)
    else:
        pygame.draw.circle(screen, star.color, star_screen_pos, screen_star_r)

    # Label at high zoom
    if r.camera.zoom >= 0.5:
        font_size = 12 if is_primary else 10
        font = r._get_font(font_size)
        label_text = system_name if is_primary else star.name
        text = font.render(label_text, True, STAR_LABEL)
        screen.blit(text, (star_screen_pos.x + 10, star_screen_pos.y))


def draw_system_details(r: Any, screen: Any, sys: Any, sys_world_pos: Any) -> None:
    """Draw planets and warp points for a system."""
    # Render storms first (behind Dyson Spheres and planets)
    # NOTE: dispatch through the renderer's wrapper methods so tests that
    # monkey-patch ``renderer._draw_storms`` / ``_draw_dyson_spheres`` still work.
    r._draw_storms(screen, sys, sys_world_pos)

    # Render Dyson Spheres (behind normal planets)
    r._draw_dyson_spheres(screen, sys, sys_world_pos)

    # Group normal planets by hex (excluding Dyson Spheres)
    hex_groups: dict = {}
    for p in sys.planets:
        # Skip Dyson Spheres - they're rendered separately
        if p.planet_type == PlanetType.DYSON_SPHERE:
            continue
        key = (p.location.q, p.location.r)
        if key not in hex_groups:
            hex_groups[key] = []
        hex_groups[key].append(p)

    for key, planets in hex_groups.items():
        coord = planets[0].location
        px, py = hex_to_pixel(coord, r.hex_size)
        hex_center_world = pygame.math.Vector2(sys_world_pos.x + px, sys_world_pos.y + py)
        hex_center_screen = r.camera.world_to_screen(hex_center_world)

        EXPAND_START = 1.5
        EXPAND_END = 2.0
        expansion_t = max(0.0, min(1.0, (r.camera.zoom - EXPAND_START) / (EXPAND_END - EXPAND_START)))

        hex_px_radius = r.hex_size * r.camera.zoom

        if len(planets) > 1:
            planets.sort(key=lambda x: x.mass, reverse=True)
            largest = planets[0]

            # Rev 4: Largest planet draw radius is 50% of hex_px_radius
            largest_draw_r = hex_px_radius * 0.5
            largest_diameter = largest_draw_r * 2
            # Offset left by 20% of the largest planet's diameter (was 10%)
            group_offset_x = -largest_diameter * 0.20

            draw_order = planets[1:] + [planets[0]]

            # Rev 5: Define angles for smaller planets based on count
            # Polar coordinates centered on largest planet
            # Angular spread increased by 15% from Rev 4 values
            smaller_count = len(planets) - 1
            if smaller_count == 1:
                smaller_angles = [0]  # Right of largest
            elif smaller_count == 2:
                smaller_angles = [40, -40]  # 40 deg above and below horizontal (was 35)
            elif smaller_count == 3:
                smaller_angles = [46, 0, -46]  # 46 deg up, horizontal, 46 deg down (was 40)
            elif smaller_count == 4:
                smaller_angles = [58, 23, -23, -58]  # Even spread (was 50, 20, -20, -50)
            elif smaller_count == 5:
                smaller_angles = [63, 31, 0, -31, -63]  # Even spread (was 55, 27, 0, -27, -55)
            else:
                # 6+ planets: spread evenly from 70 to -80 deg (150 deg arc, was 130)
                smaller_angles = [70 - i * (150 / max(1, smaller_count - 1)) for i in range(smaller_count)]

            for i, p in enumerate(planets):
                rel_scale = p.radius / largest.radius

                # Rev 5: Secondary planets sized proportionally to primary.
                # Base is largest_draw_r so ratio maps directly to screen size.
                # Minimum 5px diameter (3px radius) to keep tiny moons visible.
                draw_r = max(3, int(largest_draw_r * rel_scale))

                if p == largest:
                    final_offset = pygame.math.Vector2(group_offset_x, 0)
                else:
                    idx = planets.index(p) - 1
                    angle = smaller_angles[idx] if idx < len(smaller_angles) else 0
                    # Rev 4: Distance = 1.5x radius of largest planet (center to center)
                    dist = largest_draw_r * 1.5
                    # Offset from the center of the largest planet (not from hex center)
                    final_offset = pygame.math.Vector2(group_offset_x + dist, 0).rotate(-angle)

                current_offset = final_offset * expansion_t
                p_screen = hex_center_screen + current_offset

                # PRESERVED CODE SMELL: writing render data onto domain object.
                p._temp_screen_pos = p_screen
                p._temp_draw_r = draw_r

            for p in draw_order:
                r._draw_planet_sprite(screen, p, p._temp_screen_pos, p._temp_draw_r)
                if r.scene.selected_object == p:
                    pygame.draw.circle(screen, WHITE,
                                       (int(p._temp_screen_pos.x), int(p._temp_screen_pos.y)),
                                       int(p._temp_draw_r) + 4, 1)

        else:
            largest = planets[0]
            base_r = 5 * r.camera.zoom
            if 'Giant' in largest.planet_type.name:
                base_r *= 1.5

            r._draw_planet_sprite(screen, largest, hex_center_screen, int(base_r))

            if r.scene.selected_object == largest:
                pygame.draw.circle(screen, WHITE,
                                   (int(hex_center_screen.x), int(hex_center_screen.y)),
                                   int(base_r) + 4, 1)

    for i, wp in enumerate(sys.warp_points):
        wx, wy = hex_to_pixel(wp.location, r.hex_size)
        w_world = pygame.math.Vector2(sys_world_pos.x + wx, sys_world_pos.y + wy)
        w_screen = r.camera.world_to_screen(w_world)

        if r.scene.selected_object == wp:
            pygame.draw.circle(screen, WHITE, w_screen, max(12, int(12 * r.camera.zoom)), 1)

        img = r._asset_manager.get_random_from_group('warp_points', 'default', seed_id=hash(wp))

        if img:
            size = int(12 * r.camera.zoom)

            # Calculate rotation: unique offset per warp point + continuous rotation
            rotation_offset = hash(wp) % 360
            rotation_angle = rotation_offset + (r._elapsed_time * WARP_POINT_ROTATION_SPEED)

            # Scale factor for rotation utility
            orig_size = max(img.get_width(), img.get_height())
            scale_factor = size / orig_size if orig_size > 0 else 1.0

            # Apply scale and rotation
            rotated = scale_and_rotate_image(img, scale_factor, rotation_angle)
            dest = rotated.get_rect(center=(int(w_screen.x), int(w_screen.y)))
            screen.blit(rotated, dest, special_flags=pygame.BLEND_ADD)
        else:
            pygame.draw.circle(screen, WARPPOINT_FALLBACK, w_screen, max(2, int(5 * r.camera.zoom)))
