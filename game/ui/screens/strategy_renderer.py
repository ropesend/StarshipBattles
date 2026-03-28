"""
Rendering logic for the strategy map.
Extracted from StrategyScreen to reduce file size and improve testability.

This module contains all the drawing functions for the galaxy map,
including grid, warp lanes, systems, planets, and fleets.

Cross-layer imports (acceptable for UI rendering):
- hex_to_pixel, pixel_to_hex, HexCoord: Runtime - coordinate conversions for rendering
- OrderType: Runtime - move preview line styling based on order type
"""
import logging
import math
import os
import pygame
from game.core.paths import Paths
from game.ui.config import UIConfig
from game.core.hex_math import hex_to_pixel, pixel_to_hex, HexCoord
from game.strategy.data.order_types import OrderType
from game.strategy.data.planet import PlanetType
from game.ui.colors import (
    COLORS, WHITE,
    WARP_LANE, STAR_LABEL, HP_HEALTHY,
    FLEET_SELECTED, PATH_MOVE, PATH_WARP, PATH_LABEL,
    OVERLAY_PROCESSING, WARPPOINT_FALLBACK, DYSON_FALLBACK, PLANET_FALLBACK,
    STORM_ION, STORM_PLASMA, STORM_GRAVITATIONAL, STORM_RADIATION, STORM_DARK_NEBULA,
    ZONE_HIGHLIGHT, STORM_FALLBACK,
    HEX_OUTLINE_OCCUPIED, HEX_OUTLINE_PLAYER_OWNED,
)
from game.ui.utils import scale_and_rotate_image
from game.ui.fonts import get_font

logger = logging.getLogger(__name__)

# Animation constants
WARP_POINT_ROTATION_SPEED = 12.0  # degrees per second


class StrategyRenderer:
    """Handles all rendering for the strategy map."""

    def __init__(self, scene):
        """
        Initialize renderer with a scene reference.

        Args:
            scene: StrategyScreen instance providing camera, galaxy, empires, etc.
        """
        self.scene = scene

        # Cache asset manager reference
        from game.assets.asset_manager import get_asset_manager
        self._asset_manager = get_asset_manager()

        # Background image (static, not affected by camera)
        self._bg_image = None
        self._bg_scaled = None
        self._bg_scaled_size = (0, 0)
        self._load_background()

        # Animation state
        self._elapsed_time = 0.0

        # Hex outline cache (invalidated on turn change)
        self._hex_outline_cache = None
        self._hex_outline_cache_turn = -1

    def _load_background(self) -> None:
        """Load the galaxy background image from the asset manifest."""
        img = self._asset_manager.load_image('backgrounds', 'strategy_map')
        if isinstance(img, pygame.Surface) and img != self._asset_manager.get_missing_texture():
            self._bg_image = img

    def _draw_background(self, screen, viewport_rect: pygame.Rect) -> None:
        """Draw the static background image scaled to fill the viewport."""
        if self._bg_image is None:
            return

        target_size = (viewport_rect.width, viewport_rect.height)
        if self._bg_scaled is None or self._bg_scaled_size != target_size:
            self._bg_scaled = pygame.transform.smoothscale(self._bg_image, target_size)
            self._bg_scaled_size = target_size

        screen.blit(self._bg_scaled, viewport_rect.topleft)

    def update(self, dt: float) -> None:
        """Update animation state.

        Args:
            dt: Delta time in seconds since last frame.
        """
        self._elapsed_time += dt

    def _get_font(self, size, bold=False):
        """Get a cached font by size and style (uses central font cache)."""
        return get_font(size, bold=bold)

    # --- Property Accessors (delegate to scene) ---
    @property
    def camera(self):
        return self.scene.camera

    @property
    def galaxy(self):
        return self.scene.galaxy

    @property
    def systems(self):
        return self.scene.systems

    @property
    def empires(self):
        return self.scene.empires

    @property
    def hex_size(self):
        return self.scene.hex_size

    @property
    def screen_width(self):
        return self.scene.screen_width

    @property
    def screen_height(self):
        return self.scene.screen_height

    @property
    def SIDEBAR_WIDTH(self):
        return UIConfig.STRATEGY_SIDEBAR_WIDTH

    def _hex_radius_to_screen(self, radius_hexes: float) -> int:
        """Convert a hex-space radius to screen pixels using non-linear scaling.

        Uses a power curve anchored so that radius-2 matches the linear sqrt(3)
        formula exactly, while larger radii grow faster (reaching further into
        outer hex rings) and radius-1 grows slower (not overflowing center hex).

        BUG-94: linear sqrt(3) scaling is correct for radius-2 but undershoots
        large radii and overshoots radius-1.
        """
        if radius_hexes <= 0:
            return 3
        # Reference: radius-2 at hex_size=10, zoom=1 → 34px
        # Exponent > 1 makes large radii grow faster, small radii slower
        _EXPONENT = 1.2
        # Base unit: screen distance for 1 hex ring
        hex_spacing = math.sqrt(3) * self.hex_size * self.camera.zoom
        # Anchor at radius_hexes=2: result == 2 * hex_spacing (preserves current correct size)
        # General: result = 2 * hex_spacing * (radius_hexes / 2) ^ exponent
        return max(3, int(2 * hex_spacing * (radius_hexes / 2) ** _EXPONENT))

    @property
    def TOP_BAR_HEIGHT(self):
        return self.scene.TOP_BAR_HEIGHT

    @property
    def empire_assets(self):
        return self.scene.empire_assets

    def draw(self, screen):
        """Main draw entry point for the galaxy map."""
        viewport_w = self.screen_width - self.SIDEBAR_WIDTH
        viewport_h = self.screen_height - self.TOP_BAR_HEIGHT

        if viewport_w > 0 and viewport_h > 0:
            viewport_rect = pygame.Rect(0, self.TOP_BAR_HEIGHT, viewport_w, viewport_h)
            screen.set_clip(viewport_rect)
            screen.fill(COLORS['bg_deep'], viewport_rect)
            self._draw_background(screen, viewport_rect)
        else:
            screen.fill(COLORS['bg_deep'])

        # Draw Galaxy Elements (Clipped)
        if self.camera.zoom >= 0.4:
            self._draw_grid(screen)

        # Hex occupancy outlines (behind all objects)
        if self.camera.zoom >= 0.5:
            self._draw_hex_outlines(screen)

        self._draw_warp_lanes(screen)
        self._draw_systems(screen)
        self._draw_fleets(screen)

        # Move/Warp Line Preview
        if self.scene.input_mode in ('MOVE', 'WARP_TARGET') and self.scene.selected_fleet:
            self._draw_move_preview(screen)

        # Hover Highlight
        if self.scene.hover_hex and self.camera.zoom >= 0.5:
            self._draw_hover_hex(screen)

        # Remove Clip for UI
        screen.set_clip(None)

        # Draw Border around Galaxy Viewport
        if viewport_w > 0 and viewport_h > 0:
            viewport_rect = pygame.Rect(0, self.TOP_BAR_HEIGHT, viewport_w, viewport_h)
            pygame.draw.rect(screen, COLORS['border_normal'], viewport_rect, 2)

    def _draw_move_preview(self, screen):
        """Draw the move preview line from fleet to mouse cursor."""
        # Determine start point (Fleet Location or Last Order Target)
        start_hex = self.scene.selected_fleet.location
        for o in reversed(self.scene.selected_fleet.orders):
            if o.type == OrderType.MOVE:
                start_hex = o.target
                break

        fx, fy = hex_to_pixel(start_hex, self.hex_size)
        f_pos = self.camera.world_to_screen(pygame.math.Vector2(fx, fy))

        mx, my = pygame.mouse.get_pos()

        pygame.draw.line(screen, HP_HEALTHY, f_pos, (mx, my), 2)

    def _draw_hover_hex(self, screen):
        """Draw highlight around the currently hovered hex."""
        cx, cy = hex_to_pixel(self.scene.hover_hex, self.hex_size)
        corners_px = []
        for i in range(6):
            angle_deg = 60 * i
            angle_rad = math.radians(angle_deg)
            px = cx + self.hex_size * math.cos(angle_rad)
            py = cy + self.hex_size * math.sin(angle_rad)
            corners_px.append(self.camera.world_to_screen(pygame.math.Vector2(px, py)))

        pygame.draw.lines(screen, ZONE_HIGHLIGHT, True, corners_px, 2)

    # --- Hex Outline Methods (PROJ-214) ---

    def _build_hex_outline_data(self):
        """Build mapping of occupied global hexes to ownership flags.

        Returns:
            Dict mapping HexCoord -> (has_player_owned: bool, has_non_player: bool)
        """
        player_id = self.scene.session.player_empire.id if self.scene.session.player_empire else None
        result = {}

        # 1. Planets (from spatial index)
        for global_hex, planets in self.galaxy._global_hex_planets.items():
            has_player = False
            has_non_player = False
            for planet in planets:
                if planet.owner_id is not None and planet.owner_id == player_id:
                    has_player = True
                else:
                    has_non_player = True
            result[global_hex] = (has_player, has_non_player)

        # 2. Zones (stars, Dyson Spheres, storms)
        for global_hex, zones in self.galaxy._global_hex_zones.items():
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
        for global_hex in self.galaxy._global_hex_warp_points:
            entry = result.get(global_hex, (False, False))
            result[global_hex] = (entry[0], True)

        # 4. Fleets (check ownership per fleet)
        for empire in self.empires:
            for fleet in empire.fleets:
                if fleet.location is None:
                    continue
                entry = result.get(fleet.location, (False, False))
                if fleet.owner_id == player_id:
                    result[fleet.location] = (True, entry[1])
                else:
                    result[fleet.location] = (entry[0], True)

        return result

    def _get_hex_outline_data(self):
        """Get cached hex outline data, rebuilding if turn changed."""
        current_turn = getattr(self.scene.session, 'turn_number', 0)
        if self._hex_outline_cache is None or self._hex_outline_cache_turn != current_turn:
            self._hex_outline_cache = self._build_hex_outline_data()
            self._hex_outline_cache_turn = current_turn
        return self._hex_outline_cache

    def _draw_hex_outlines(self, screen):
        """Draw inner hex outlines for occupied hexes.

        Red outline for any object, white for player-owned,
        dual concentric outlines when both are present.
        """
        outline_data = self._get_hex_outline_data()
        if not outline_data:
            return

        sw = self.screen_width
        sh = self.screen_height
        margin = 50

        for global_hex, (has_player, has_non_player) in outline_data.items():
            cx, cy = hex_to_pixel(global_hex, self.hex_size)
            screen_center = self.camera.world_to_screen(pygame.math.Vector2(cx, cy))

            if screen_center.x < -margin or screen_center.x > sw + margin:
                continue
            if screen_center.y < -margin or screen_center.y > sh + margin:
                continue

            if has_player and has_non_player:
                self._draw_inner_hex(screen, cx, cy, 0.90, HEX_OUTLINE_PLAYER_OWNED)
                self._draw_inner_hex(screen, cx, cy, 0.80, HEX_OUTLINE_OCCUPIED)
            elif has_player:
                self._draw_inner_hex(screen, cx, cy, 0.88, HEX_OUTLINE_PLAYER_OWNED)
            else:
                self._draw_inner_hex(screen, cx, cy, 0.88, HEX_OUTLINE_OCCUPIED)

    def _draw_inner_hex(self, screen, cx, cy, scale, color):
        """Draw a single inner hex outline at the given scale factor.

        Args:
            screen: Pygame surface to draw on.
            cx, cy: World-space center of the hex.
            scale: Scale factor (0.0-1.0) relative to hex_size.
            color: RGB tuple for the outline color.
        """
        inner_size = self.hex_size * scale
        corners = []
        for i in range(6):
            angle_rad = math.radians(60 * i)
            px = cx + inner_size * math.cos(angle_rad)
            py = cy + inner_size * math.sin(angle_rad)
            corners.append(self.camera.world_to_screen(pygame.math.Vector2(px, py)))

        pygame.draw.lines(screen, color, True, corners, 2)

    def _draw_grid(self, screen):
        """Draw the hex grid with optimized snake lines."""
        # 1. Culling
        tl_world = self.camera.screen_to_world((0, 0))
        tr_world = self.camera.screen_to_world((self.screen_width, 0))
        bl_world = self.camera.screen_to_world((0, self.screen_height))
        br_world = self.camera.screen_to_world((self.screen_width, self.screen_height))

        corners = [tl_world, tr_world, bl_world, br_world]
        q_vals = []
        r_vals = []
        for p in corners:
            h = pixel_to_hex(p.x, p.y, self.hex_size)
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

        screen_hex_size = self.hex_size * self.camera.zoom
        SQRT3 = 1.73205080757

        s = screen_hex_size
        col_stride_x = 1.5 * s
        row_stride_y = SQRT3 * s
        half_row_height = row_stride_y / 2

        cam_x = self.camera.position.x
        cam_y = self.camera.position.y
        base_x = (self.camera.width / 2) - cam_x * self.camera.zoom + self.camera.offset_x
        base_y = (self.camera.height / 2) - cam_y * self.camera.zoom + self.camera.offset_y

        v_tl = pygame.math.Vector2(-0.5 * s, -half_row_height)
        v_l = pygame.math.Vector2(-1.0 * s, 0)
        v_bl = pygame.math.Vector2(-0.5 * s, half_row_height)
        v_tr = pygame.math.Vector2(0.5 * s, -half_row_height)

        for q in range(min_q, max_q + 2):
            cx = base_x + q * col_stride_x

            if not (-50 < cx < self.screen_width + 50):
                continue

            col_y_offset = base_y + (row_stride_y * 0.5 * q)

            start_r = int((-50 - col_y_offset) / row_stride_y) - 1
            end_r = int((self.screen_height + 50 - col_y_offset) / row_stride_y) + 1

            snake_points = []

            cy_start = col_y_offset + row_stride_y * start_r
            snake_points.append((cx + v_tl.x, cy_start + v_tl.y))

            for r in range(start_r, end_r):
                cy = col_y_offset + row_stride_y * r

                snake_points.append((cx + v_l.x, cy + v_l.y))
                snake_points.append((cx + v_bl.x, cy + v_bl.y))

                p1 = (cx + v_tl.x, cy + v_tl.y)
                p2 = (cx + v_tr.x, cy + v_tr.y)
                pygame.draw.line(screen, grid_color, p1, p2, 1)

            if len(snake_points) > 1:
                pygame.draw.lines(screen, grid_color, False, snake_points, 1)

    def _draw_warp_lanes(self, screen):
        """Draw warp lane connections between systems."""
        # Viewport culling bounds with margin
        margin = 100
        screen_w = self.screen_width
        screen_h = self.screen_height

        def is_on_screen(scr_pos):
            """Check if a screen position is within the visible area."""
            return -margin <= scr_pos.x <= screen_w + margin and -margin <= scr_pos.y <= screen_h + margin

        drawn_pairs = set()
        for sys in self.galaxy.systems.values():
            sx, sy = hex_to_pixel(sys.global_location, self.hex_size)

            for wp in sys.warp_points:
                target_id = wp.destination_id
                target_sys = self.galaxy.get_system_by_name(target_id)

                if target_sys:
                    reciprocal_wp = next((w for w in target_sys.warp_points if w.destination_id == sys.name), None)

                    if reciprocal_wp:
                        wx_a, wy_a = hex_to_pixel(wp.location, self.hex_size)
                        world_a = pygame.math.Vector2(sx + wx_a, sy + wy_a)

                        ts_x, ts_y = hex_to_pixel(target_sys.global_location, self.hex_size)
                        wx_b, wy_b = hex_to_pixel(reciprocal_wp.location, self.hex_size)
                        world_b = pygame.math.Vector2(ts_x + wx_b, ts_y + wy_b)

                        scr_a = self.camera.world_to_screen(world_a)
                        scr_b = self.camera.world_to_screen(world_b)

                        # Viewport culling: skip if both endpoints are off-screen
                        if not is_on_screen(scr_a) and not is_on_screen(scr_b):
                            continue

                        pair_key = tuple(sorted((f"{sys.name}_{wp.location}", f"{target_sys.name}_{reciprocal_wp.location}")))
                        if pair_key in drawn_pairs:
                            continue
                        drawn_pairs.add(pair_key)

                        pygame.draw.line(screen, WARP_LANE, scr_a, scr_b, 1)
                    else:
                        ts_x, ts_y = hex_to_pixel(target_sys.global_location, self.hex_size)
                        world_b = pygame.math.Vector2(ts_x, ts_y)

                        wx_a, wy_a = hex_to_pixel(wp.location, self.hex_size)
                        world_a = pygame.math.Vector2(sx + wx_a, sy + wy_a)

                        scr_a = self.camera.world_to_screen(world_a)
                        scr_b = self.camera.world_to_screen(world_b)

                        # Viewport culling: skip if both endpoints are off-screen
                        if not is_on_screen(scr_a) and not is_on_screen(scr_b):
                            continue

                        pygame.draw.line(screen, WARP_LANE, scr_a, scr_b, 1)

    def _draw_systems(self, screen):
        """Draw all star systems with stars, planets, and warp points."""
        tl = self.camera.screen_to_world((0, 0))
        br = self.camera.screen_to_world((self.screen_width, self.screen_height))

        margin = 600
        min_x, max_x = min(tl.x, br.x) - margin, max(tl.x, br.x) + margin
        min_y, max_y = min(tl.y, br.y) - margin, max(tl.y, br.y) + margin

        for sys in self.galaxy.systems.values():
            hx, hy = hex_to_pixel(sys.global_location, self.hex_size)
            world_pos = pygame.math.Vector2(hx, hy)

            if not (min_x < world_pos.x < max_x and min_y < world_pos.y < max_y):
                continue

            screen_pos = self.camera.world_to_screen(world_pos)

            # Draw Colony Marker when zoomed out
            self._draw_colony_marker(screen, sys, world_pos)

            primary = sys.primary_star
            if primary:
                for star in sys.stars:
                    is_primary = star == primary
                    is_selected = self.scene.selected_object == sys
                    self._draw_star(screen, star, (hx, hy), sys.name, is_primary, is_selected)

            if self.camera.zoom >= 0.5:
                self._draw_system_details(screen, sys, world_pos)

    def _load_star_image(self, star) -> 'pygame.Surface':
        """Load a star image using the star's image_id.

        Uses the resolution-aware loader from AssetManager (1024px for strategy view).
        Falls back to None if star has no image_id or image not found.

        Args:
            star: Star object with image_id attribute

        Returns:
            pygame.Surface or None
        """
        if not star.image_id:
            return None
        img = self._asset_manager.load_star_image(star.image_id, 1024)
        if img and img != self._asset_manager.get_missing_texture():
            return img
        return None

    def _draw_colony_marker(self, screen, sys, world_pos):
        """Draw colony ownership marker at low zoom levels.

        Only draws when zoom < 0.5 and system has owned planets.
        Uses first owned planet's owner color.

        Args:
            screen: pygame.Surface to draw on
            sys: StarSystem object
            world_pos: pygame.math.Vector2 - system center in world coords
        """
        if self.camera.zoom >= 0.5:
            return

        owned_planets = [p for p in sys.planets if p.owner_id is not None]
        if not owned_planets:
            return

        first_owner_id = owned_planets[0].owner_id
        owner_emp = next((e for e in self.empires if e.id == first_owner_id), None)
        if not owner_emp:
            return

        offset_world = pygame.math.Vector2(-0.75 * self.hex_size, -0.75 * self.hex_size)
        marker_world = world_pos + offset_world
        marker_screen = self.camera.world_to_screen(marker_world)

        pygame.draw.circle(screen, owner_emp.color, (int(marker_screen.x), int(marker_screen.y)), 5)
        pygame.draw.circle(screen, WHITE, (int(marker_screen.x), int(marker_screen.y)), 6, 1)

    def _draw_star(self, screen, star, system_center: tuple, system_name: str, is_primary: bool, is_selected_system: bool):
        """Render a single star with image, selection highlight, and label.

        Uses star.image_id with core metadata from star_metadata.json for
        proper sizing — the visible core matches the hex radius, corona
        extends freely beyond.

        Args:
            screen: pygame.Surface to draw on
            star: Star object to render
            system_center: (hx, hy) tuple - system center in world pixels
            system_name: str - name of the parent system (for primary star label)
            is_primary: bool - whether this is the primary star
            is_selected_system: bool - whether the parent system is selected
        """
        hx, hy = system_center
        local_pixel_x, local_pixel_y = hex_to_pixel(star.location, self.hex_size)
        star_screen_pos = self.camera.world_to_screen(
            pygame.math.Vector2(hx + local_pixel_x, hy + local_pixel_y)
        )

        screen_star_r = self._hex_radius_to_screen(star.radius_hexes)

        # Selection highlight (before star image)
        if is_selected_system and is_primary:
            pygame.draw.circle(screen, WHITE, star_screen_pos, screen_star_r + 4, 1)

        # Star image with core-based sizing, or fallback to colored circle
        star_img = self._load_star_image(star)
        if star_img:
            # Use core metadata to size the image so the visible core
            # matches the hex radius — corona extends beyond
            core_info = self._asset_manager.get_star_core_info(star.image_id)
            core_radius_frac = max(core_info.get('radiusCore', 0.25), 0.05)
            center_x_frac = core_info.get('centerX', 0.5)
            center_y_frac = core_info.get('centerY', 0.5)

            # Scale so core in the image matches the hex screen size.
            # Metadata 'radius' is normalized to image width; treat as diameter
            # to get the correct visual scale on the hex grid.
            core_diameter_frac = core_radius_frac * 2
            display_size = int(screen_star_r / core_diameter_frac)
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
        if self.camera.zoom >= 0.5:
            font_size = 12 if is_primary else 10
            font = self._get_font(font_size)
            label_text = system_name if is_primary else star.name
            text = font.render(label_text, True, STAR_LABEL)
            screen.blit(text, (star_screen_pos.x + 10, star_screen_pos.y))

    def _draw_system_details(self, screen, sys, sys_world_pos):
        """Draw planets and warp points for a system."""
        # Render storms first (behind Dyson Spheres and planets)
        self._draw_storms(screen, sys, sys_world_pos)

        # Render Dyson Spheres (behind normal planets)
        self._draw_dyson_spheres(screen, sys, sys_world_pos)

        # Group normal planets by hex (excluding Dyson Spheres)
        hex_groups = {}
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
            px, py = hex_to_pixel(coord, self.hex_size)
            hex_center_world = pygame.math.Vector2(sys_world_pos.x + px, sys_world_pos.y + py)
            hex_center_screen = self.camera.world_to_screen(hex_center_world)

            EXPAND_START = 1.5
            EXPAND_END = 2.0
            expansion_t = max(0.0, min(1.0, (self.camera.zoom - EXPAND_START) / (EXPAND_END - EXPAND_START)))

            hex_px_radius = self.hex_size * self.camera.zoom

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
                    smaller_angles = [40, -40]  # 40° above and below horizontal (was 35°)
                elif smaller_count == 3:
                    smaller_angles = [46, 0, -46]  # 46° up, horizontal, 46° down (was 40°)
                elif smaller_count == 4:
                    smaller_angles = [58, 23, -23, -58]  # Even spread (was 50, 20, -20, -50)
                elif smaller_count == 5:
                    smaller_angles = [63, 31, 0, -31, -63]  # Even spread (was 55, 27, 0, -27, -55)
                else:
                    # 6+ planets: spread evenly from 70° to -80° (150° arc, was 130°)
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

                    p._temp_screen_pos = p_screen
                    p._temp_draw_r = draw_r

                for p in draw_order:
                    self._draw_planet_sprite(screen, p, p._temp_screen_pos, p._temp_draw_r)
                    if self.scene.selected_object == p:
                        pygame.draw.circle(screen, WHITE,
                                           (int(p._temp_screen_pos.x), int(p._temp_screen_pos.y)),
                                           int(p._temp_draw_r) + 4, 1)

            else:
                largest = planets[0]
                base_r = 5 * self.camera.zoom
                if 'Giant' in largest.planet_type.name:
                    base_r *= 1.5

                self._draw_planet_sprite(screen, largest, hex_center_screen, int(base_r))

                if self.scene.selected_object == largest:
                    pygame.draw.circle(screen, WHITE,
                                       (int(hex_center_screen.x), int(hex_center_screen.y)),
                                       int(base_r) + 4, 1)

        for i, wp in enumerate(sys.warp_points):
            wx, wy = hex_to_pixel(wp.location, self.hex_size)
            w_world = pygame.math.Vector2(sys_world_pos.x + wx, sys_world_pos.y + wy)
            w_screen = self.camera.world_to_screen(w_world)

            if self.scene.selected_object == wp:
                pygame.draw.circle(screen, WHITE, w_screen, max(12, int(12 * self.camera.zoom)), 1)

            img = self._asset_manager.get_random_from_group('warp_points', 'default', seed_id=hash(wp))

            if img:
                size = int(12 * self.camera.zoom)

                # Calculate rotation: unique offset per warp point + continuous rotation
                rotation_offset = hash(wp) % 360
                rotation_angle = rotation_offset + (self._elapsed_time * WARP_POINT_ROTATION_SPEED)

                # Scale factor for rotation utility
                orig_size = max(img.get_width(), img.get_height())
                scale_factor = size / orig_size if orig_size > 0 else 1.0

                # Apply scale and rotation
                rotated = scale_and_rotate_image(img, scale_factor, rotation_angle)
                dest = rotated.get_rect(center=(int(w_screen.x), int(w_screen.y)))
                screen.blit(rotated, dest, special_flags=pygame.BLEND_ADD)
            else:
                pygame.draw.circle(screen, WARPPOINT_FALLBACK, w_screen, max(2, int(5 * self.camera.zoom)))

    def _draw_dyson_spheres(self, screen, sys, sys_world_pos):
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
            px, py = hex_to_pixel(planet.location, self.hex_size)
            center_world = pygame.math.Vector2(sys_world_pos.x + px, sys_world_pos.y + py)
            center_screen = self.camera.world_to_screen(center_world)

            # Calculate size using non-linear hex-to-screen scaling (BUG-94)
            screen_radius = max(6, self._hex_radius_to_screen(radius_hexes))

            # Load Dyson Sphere image
            img = self._load_dyson_sphere_image()

            # Draw selection circle if selected
            if self.scene.selected_object == planet:
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

            # Draw owner marker if colonized
            if planet.owner_id is not None:
                owner_emp = next((e for e in self.empires if e.id == planet.owner_id), None)
                if owner_emp:
                    marker_offset = screen_radius * 0.8
                    marker_pos = (int(center_screen.x + marker_offset), int(center_screen.y - marker_offset))

                    emp_assets = self.empire_assets.get(owner_emp.id)
                    if emp_assets and 'colony' in emp_assets:
                        flag_img = emp_assets['colony']
                        # Preserve original aspect ratio
                        orig_w, orig_h = flag_img.get_width(), flag_img.get_height()
                        f_w = max(10, int(screen_diameter * 0.15))
                        f_h = int(f_w * orig_h / orig_w) if orig_w > 0 else f_w

                        scaled_flag = pygame.transform.smoothscale(flag_img, (f_w, f_h))
                        flag_rect = scaled_flag.get_rect(center=marker_pos)
                        screen.blit(scaled_flag, flag_rect)
                    else:
                        # Fallback: colored circle
                        pygame.draw.circle(screen, owner_emp.color, marker_pos, max(3, screen_diameter // 10))
                        pygame.draw.circle(screen, WHITE, marker_pos, max(3, screen_diameter // 10) + 1, 1)

    def _draw_storms(self, screen, sys, sys_world_pos):
        """Draw storm nebulae overlays for a star system.

        Storms are rendered BEFORE Dyson Spheres and planets so they appear behind them.
        Each storm uses a nebulae image scaled to cover its hex extent.
        """
        # Skip if system has no storms
        # IStarSystem.storms is always present (List)
        if not sys.storms:
            return

        # Skip detailed rendering at low zoom - just draw colored hex fills
        if self.camera.zoom < 0.3:
            self._draw_storms_low_detail(screen, sys, sys_world_pos)
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
            from game.core.hex_math import HexCoord
            corner_hexes = [
                HexCoord(min_q, min_r),
                HexCoord(max_q, min_r),
                HexCoord(min_q, max_r),
                HexCoord(max_q, max_r),
            ]

            # Calculate bounding box in world pixels
            pixel_coords = []
            for h in corner_hexes:
                px, py = hex_to_pixel(h, self.hex_size)
                pixel_coords.append((sys_world_pos.x + px, sys_world_pos.y + py))

            world_min_x = min(p[0] for p in pixel_coords) - self.hex_size
            world_max_x = max(p[0] for p in pixel_coords) + self.hex_size
            world_min_y = min(p[1] for p in pixel_coords) - self.hex_size
            world_max_y = max(p[1] for p in pixel_coords) + self.hex_size

            # Viewport culling
            screen_tl = self.camera.world_to_screen(pygame.math.Vector2(world_min_x, world_min_y))
            screen_br = self.camera.world_to_screen(pygame.math.Vector2(world_max_x, world_max_y))

            if screen_br.x < 0 or screen_tl.x > self.screen_width:
                continue
            if screen_br.y < 0 or screen_tl.y > self.screen_height:
                continue

            # Calculate center position for rendering
            center_x = (world_min_x + world_max_x) / 2
            center_y = (world_min_y + world_max_y) / 2
            center_screen = self.camera.world_to_screen(pygame.math.Vector2(center_x, center_y))

            # Calculate screen dimensions
            screen_width = int((world_max_x - world_min_x) * self.camera.zoom)
            screen_height = int((world_max_y - world_min_y) * self.camera.zoom)

            # Ensure minimum size
            screen_width = max(20, screen_width)
            screen_height = max(20, screen_height)

            # Load nebulae image using image_variant as seed
            img = self._asset_manager.get_random_from_group(
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
                    hx, hy = hex_to_pixel(h, self.hex_size)
                    h_world = pygame.math.Vector2(sys_world_pos.x + hx, sys_world_pos.y + hy)
                    h_screen = self.camera.world_to_screen(h_world)

                    # Draw hex fill
                    corners = []
                    for i in range(6):
                        angle_deg = 60 * i
                        angle_rad = math.radians(angle_deg)
                        corner_x = h_screen.x + self.hex_size * self.camera.zoom * math.cos(angle_rad)
                        corner_y = h_screen.y + self.hex_size * self.camera.zoom * math.sin(angle_rad)
                        corners.append((corner_x, corner_y))

                    # Create transparent surface for hex
                    hex_surf = pygame.Surface((int(self.hex_size * 2 * self.camera.zoom + 4),
                                              int(self.hex_size * 2 * self.camera.zoom + 4)),
                                              pygame.SRCALPHA)
                    offset_corners = [(c[0] - h_screen.x + self.hex_size * self.camera.zoom + 2,
                                      c[1] - h_screen.y + self.hex_size * self.camera.zoom + 2)
                                     for c in corners]
                    pygame.draw.polygon(hex_surf, tint + (int(storm.intensity * 100),), offset_corners)
                    dest = hex_surf.get_rect(center=(int(h_screen.x), int(h_screen.y)))
                    screen.blit(hex_surf, dest)

    def _draw_storms_low_detail(self, screen, sys, sys_world_pos):
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
                hx, hy = hex_to_pixel(h, self.hex_size)
                h_world = pygame.math.Vector2(sys_world_pos.x + hx, sys_world_pos.y + hy)
                h_screen = self.camera.world_to_screen(h_world)

                # Skip if off-screen
                if h_screen.x < -50 or h_screen.x > self.screen_width + 50:
                    continue
                if h_screen.y < -50 or h_screen.y > self.screen_height + 50:
                    continue

                # Draw simple colored circle at hex center
                radius = max(2, int(self.hex_size * self.camera.zoom * 0.5))
                pygame.draw.circle(screen, tint[:3], (int(h_screen.x), int(h_screen.y)), radius)

    def _draw_planet_sprite(self, screen, planet, center_pos, size):
        """Draw a single planet sprite with colony marker if owned."""
        img = None

        # Load planet image from Planets_V3 using image_id
        if planet.image_id:
            img = self._load_planet_v3_image(planet.image_id)

        if img:
            scaled = pygame.transform.smoothscale(img, (size * 2, size * 2))
            dest = scaled.get_rect(center=(int(center_pos.x), int(center_pos.y)))
            screen.blit(scaled, dest)
        else:
            # Fallback: gray circle if no image_id (should not happen for new planets)
            pygame.draw.circle(screen, PLANET_FALLBACK, (int(center_pos.x), int(center_pos.y)), size)

        # Owner Marker (Colony Flag)
        if planet.owner_id is not None:
            owner_emp = next((e for e in self.empires if e.id == planet.owner_id), None)

            if owner_emp:
                flag_offset = size * 0.8
                marker_pos = (int(center_pos.x + flag_offset), int(center_pos.y - flag_offset))

                emp_assets = self.empire_assets.get(owner_emp.id)
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

    def _load_planet_v3_image(self, image_id):
        """Load a planet image from the Planets_V3 directory.

        Args:
            image_id: Filename of the planet image (e.g., "planet_5_994_1769750020702.png")

        Returns:
            Pygame Surface or None if loading fails
        """
        if not image_id:
            return None

        # Load planet image at 512px resolution (optimal for portraits)
        # Uses resolution-aware loading with fallback chain (PROJ-54 Phase 10)
        img = self._asset_manager.load_planet_image(image_id, requested_size=512)

        # Check if we got the missing texture placeholder
        if img is self._asset_manager.missing_texture:
            return None

        return img

    def _load_dyson_sphere_image(self):
        """Load the Dyson Sphere image from Sphere world directory.

        Returns:
            Pygame Surface or None if loading fails
        """
        from game.core.paths import Paths
        import os

        image_path = os.path.join(Paths.SPHERE_WORLD_DIR, "Sphereworld_Portrait.png")
        img = self._asset_manager.load_external_image(image_path)

        # Check if we got the missing texture placeholder
        if img is self._asset_manager.missing_texture:
            return None

        return img

    def _draw_fleets(self, screen):
        """Draw all fleets and their movement paths."""
        for emp in self.empires:
            for f in emp.fleets:
                if f.location is None:
                    logger.warning(f"Skipping render for Fleet {f.id} (Owner {f.owner_id}): Location is None")
                    continue

                fx, fy = hex_to_pixel(f.location, self.hex_size)
                f_screen = self.camera.world_to_screen(pygame.math.Vector2(fx, fy))

                fleet_on_screen = (0 <= f_screen.x <= self.screen_width and 0 <= f_screen.y <= self.screen_height)

                if fleet_on_screen:
                    emp_assets = self.empire_assets.get(emp.id)
                    if emp_assets and 'fleet' in emp_assets:
                        img = emp_assets['fleet']
                        size = int(24 * self.camera.zoom)
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

                        if self.scene.selected_fleet == f:
                            pygame.draw.rect(screen, FLEET_SELECTED, dest.inflate(4, 4), 1)
                    else:
                        size = 10 * self.camera.zoom
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
                        if self.scene.selected_fleet == f:
                            color = FLEET_SELECTED

                        pygame.draw.polygon(screen, color, points)

                # Draw path for selected fleet
                if f == self.scene.selected_fleet:
                    self._draw_fleet_path(screen, f, f_screen)

    def _draw_fleet_path(self, screen, fleet, fleet_screen_pos):
        """Draw the movement path for a fleet."""
        segments = self.scene.session.get_fleet_path_projection(fleet, max_turns=50)

        start_screen = fleet_screen_pos
        font = None
        if segments and self.camera.zoom >= 0.5:
            font = self._get_font(18, bold=True)

        for seg in segments:
            end_hex = seg['end']
            is_warp = seg['is_warp']
            turn_idx = seg['turn']

            ex, ey = hex_to_pixel(end_hex, self.hex_size)
            end_screen = self.camera.world_to_screen(pygame.math.Vector2(ex, ey))

            start_on = (0 <= start_screen.x <= self.screen_width and 0 <= start_screen.y <= self.screen_height)
            end_on = (0 <= end_screen.x <= self.screen_width and 0 <= end_screen.y <= self.screen_height)

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

    def draw_processing_overlay(self, screen):
        """Draw a modal overlay for turn processing."""
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        font = self._get_font(48, bold=True)
        text = font.render("PROCESSING TURN...", True, OVERLAY_PROCESSING)
        rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(text, rect)
