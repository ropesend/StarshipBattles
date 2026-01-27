"""
Rendering logic for the strategy map.
Extracted from StrategyScene to reduce file size and improve testability.

This module contains all the drawing functions for the galaxy map,
including grid, warp lanes, systems, planets, and fleets.
"""
import math
import pygame
from game.core.config import UIConfig
from game.strategy.data.hex_math import hex_to_pixel, pixel_to_hex, HexCoord
from game.strategy.data.fleet import OrderType
from game.ui.colors import COLORS


class StrategyRenderer:
    """Handles all rendering for the strategy map."""

    def __init__(self, scene):
        """
        Initialize renderer with a scene reference.

        Args:
            scene: StrategyScene instance providing camera, galaxy, empires, etc.
        """
        self.scene = scene

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
        else:
            screen.fill(COLORS['bg_deep'])

        # Draw Galaxy Elements (Clipped)
        if self.camera.zoom >= 0.4:
            self._draw_grid(screen)

        self._draw_warp_lanes(screen)
        self._draw_systems(screen)
        self._draw_fleets(screen)

        # Move Line Preview
        if getattr(self.scene, 'input_mode', 'SELECT') == 'MOVE' and self.scene.selected_fleet:
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

        pygame.draw.line(screen, (0, 255, 0), f_pos, (mx, my), 2)

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

        pygame.draw.lines(screen, (100, 255, 100), True, corners_px, 2)

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
        drawn_pairs = set()
        for sys in self.galaxy.systems.values():
            sx, sy = hex_to_pixel(sys.global_location, self.hex_size)

            for wp in sys.warp_points:
                target_id = wp.destination_id
                target_sys = next((s for s in self.galaxy.systems.values() if s.name == target_id), None)

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

                        pair_key = tuple(sorted((f"{sys.name}_{wp.location}", f"{target_sys.name}_{reciprocal_wp.location}")))
                        if pair_key in drawn_pairs:
                            continue
                        drawn_pairs.add(pair_key)

                        pygame.draw.line(screen, (50, 50, 100), scr_a, scr_b, 1)
                    else:
                        ts_x, ts_y = hex_to_pixel(target_sys.global_location, self.hex_size)
                        world_b = pygame.math.Vector2(ts_x, ts_y)

                        wx_a, wy_a = hex_to_pixel(wp.location, self.hex_size)
                        world_a = pygame.math.Vector2(sx + wx_a, sy + wy_a)

                        scr_a = self.camera.world_to_screen(world_a)
                        scr_b = self.camera.world_to_screen(world_b)
                        pygame.draw.line(screen, (50, 50, 100), scr_a, scr_b, 1)

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
            if self.camera.zoom < 0.5:
                owned_planets = [p for p in sys.planets if p.owner_id is not None]
                if owned_planets:
                    first_owner_id = owned_planets[0].owner_id
                    owner_emp = next((e for e in self.empires if e.id == first_owner_id), None)
                    if owner_emp:
                        offset_world = pygame.math.Vector2(-0.75 * self.hex_size, -0.75 * self.hex_size)
                        marker_world = world_pos + offset_world
                        marker_screen = self.camera.world_to_screen(marker_world)

                        pygame.draw.circle(screen, owner_emp.color, (int(marker_screen.x), int(marker_screen.y)), 5)
                        pygame.draw.circle(screen, (255, 255, 255), (int(marker_screen.x), int(marker_screen.y)), 6, 1)

            primary = sys.primary_star
            if primary:
                for star in sys.stars:
                    local_pixel_x, local_pixel_y = hex_to_pixel(star.location, self.hex_size)
                    star_screen_pos = self.camera.world_to_screen(pygame.math.Vector2(hx + local_pixel_x, hy + local_pixel_y))

                    asset_key = 'yellow'
                    color = star.color
                    if color[0] > 200 and color[1] < 100:
                        asset_key = 'red'
                    elif color[2] > 200 and color[0] < 100:
                        asset_key = 'blue'
                    elif color[0] > 200 and color[1] > 200 and color[2] > 200:
                        asset_key = 'white'
                    elif color[0] > 200 and color[1] > 150:
                        asset_key = 'orange'

                    from game.assets.asset_manager import get_asset_manager
                    am = get_asset_manager()
                    star_img = am.get_image('stars', asset_key)

                    screen_star_r = max(3, int(star.diameter_hexes * self.hex_size * self.camera.zoom))

                    if self.scene.selected_object == sys and star == primary:
                        pygame.draw.circle(screen, (255, 255, 255), star_screen_pos, screen_star_r + 4, 1)

                    if star_img:
                        scaled_img = pygame.transform.smoothscale(star_img, (screen_star_r * 2, screen_star_r * 2))
                        dest_rect = scaled_img.get_rect(center=(int(star_screen_pos.x), int(star_screen_pos.y)))
                        screen.blit(scaled_img, dest_rect)
                    else:
                        pygame.draw.circle(screen, color, star_screen_pos, screen_star_r)

                    if self.camera.zoom >= 0.5:
                        font_size = 12 if star == primary else 10
                        font = pygame.font.SysFont("arial", font_size)
                        text = font.render(star.name if star != primary else sys.name, True, (200, 200, 200))
                        screen.blit(text, (star_screen_pos.x + 10, star_screen_pos.y))

            if self.camera.zoom >= 0.5:
                self._draw_system_details(screen, sys, world_pos)

    def _draw_system_details(self, screen, sys, sys_world_pos):
        """Draw planets and warp points for a system."""
        hex_groups = {}
        for p in sys.planets:
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
                    if rel_scale < 0.4:
                        rel_scale = 0.4

                    base_r = hex_px_radius * 0.25
                    draw_r = max(2, int(base_r * rel_scale))

                    if p == largest:
                        final_offset = pygame.math.Vector2(group_offset_x, 0)
                        primary_draw_r = max(2, int(largest_draw_r * rel_scale))
                        draw_r = primary_draw_r
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
                        pygame.draw.circle(screen, (255, 255, 255),
                                           (int(p._temp_screen_pos.x), int(p._temp_screen_pos.y)),
                                           int(p._temp_draw_r) + 4, 1)

            else:
                largest = planets[0]
                base_r = 5 * self.camera.zoom
                if 'Giant' in largest.planet_type.name:
                    base_r *= 1.5

                self._draw_planet_sprite(screen, largest, hex_center_screen, int(base_r))

                if self.scene.selected_object == largest:
                    pygame.draw.circle(screen, (255, 255, 255),
                                       (int(hex_center_screen.x), int(hex_center_screen.y)),
                                       int(base_r) + 4, 1)

        for i, wp in enumerate(sys.warp_points):
            wx, wy = hex_to_pixel(wp.location, self.hex_size)
            w_world = pygame.math.Vector2(sys_world_pos.x + wx, sys_world_pos.y + wy)
            w_screen = self.camera.world_to_screen(w_world)

            if self.scene.selected_object == wp:
                pygame.draw.circle(screen, (255, 255, 255), w_screen, max(12, int(12 * self.camera.zoom)), 1)

            from game.assets.asset_manager import get_asset_manager
            am = get_asset_manager()
            img = am.get_random_from_group('warp_points', 'default', seed_id=hash(wp))

            if img:
                size = int(12 * self.camera.zoom)
                scaled = pygame.transform.smoothscale(img, (size, size))
                dest = scaled.get_rect(center=(int(w_screen.x), int(w_screen.y)))
                screen.blit(scaled, dest, special_flags=pygame.BLEND_ADD)
            else:
                pygame.draw.circle(screen, (200, 0, 255), w_screen, max(2, int(5 * self.camera.zoom)))

    def _draw_planet_sprite(self, screen, planet, center_pos, size):
        """Draw a single planet sprite with colony marker if owned."""
        p_type_name = planet.planet_type.name.lower()
        cat = 'terran'
        if 'gas' in p_type_name:
            cat = 'gas'
        elif 'ice' in p_type_name:
            cat = 'ice'
        elif 'desert' in p_type_name or 'hot' in p_type_name:
            cat = 'venus'

        from game.assets.asset_manager import get_asset_manager
        am = get_asset_manager()

        img = am.get_random_from_group('planets', cat, seed_id=id(planet))
        if img:
            scaled = pygame.transform.smoothscale(img, (size * 2, size * 2))
            dest = scaled.get_rect(center=(int(center_pos.x), int(center_pos.y)))
            screen.blit(scaled, dest)
        else:
            pygame.draw.circle(screen, planet.planet_type.color, (int(center_pos.x), int(center_pos.y)), size)

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
                    pygame.draw.circle(screen, (255, 255, 255), marker_pos, max(3, int(size / 3)) + 1, 1)

    def _draw_fleets(self, screen):
        """Draw all fleets and their movement paths."""
        for emp in self.empires:
            for f in emp.fleets:
                if f.location is None:
                    from game.core.logger import log_warning
                    log_warning(f"Skipping render for Fleet {f.id} (Owner {f.owner_id}): Location is None")
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
                            pygame.draw.rect(screen, (255, 255, 0), dest.inflate(4, 4), 1)
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
                            color = (255, 255, 0)

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
            font = pygame.font.SysFont("arial", 18, bold=True)

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

            color = (0, 255, 100)
            width = 2
            if is_warp:
                color = (255, 50, 50)
                width = 1

            pygame.draw.line(screen, color, start_screen, end_screen, width)

            if font and not is_warp and end_on:
                txt = font.render(str(turn_idx), True, (200, 200, 255))
                tr = txt.get_rect(center=(end_screen.x, end_screen.y))
                screen.blit(txt, tr)

            start_screen = end_screen

    def draw_processing_overlay(self, screen):
        """Draw a modal overlay for turn processing."""
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        font = pygame.font.SysFont("arial", 48, bold=True)
        text = font.render("PROCESSING TURN...", True, (255, 200, 0))
        rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(text, rect)
