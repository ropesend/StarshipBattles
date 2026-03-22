"""
Click mode dispatching for strategy input.

Handles all mouse click events based on current input mode (SELECT, MOVE, JOIN, etc.).
Extracted from StrategyInputHandler for router decomposition (PROJ-173 Phase 3).
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

import pygame

from game.core.hex_math import pixel_to_hex

if TYPE_CHECKING:
    from game.ui.screens.strategy_input_handler import StrategyInputHandler

logger = logging.getLogger(__name__)


class ClickModeDispatcher:
    """Dispatches mouse clicks based on current input mode.

    Routes clicks to mode-specific handlers for fleet movement, joining,
    colonization, cargo operations, superweapon targeting, and selection.
    """

    def __init__(self, handler: "StrategyInputHandler") -> None:
        """Initialize click dispatcher.

        Args:
            handler: Parent StrategyInputHandler for state access.
        """
        self._handler = handler
        # Mode dispatch table
        self._mode_handlers = {
            'MOVE': self._handle_move_mode_click,
            'JOIN': self._handle_join_mode_click,
            'COLONIZE_TARGET': self._handle_colonize_mode_click,
            'TRANSFER': self._handle_transfer_mode_click,
            'DROP_CARGO': self._handle_drop_cargo_mode_click,
            'LOAD_CARGO': self._handle_load_cargo_mode_click,
            'WARP_TARGET': self._handle_warp_target_click,
            'IMPLODE_PLANET_TARGET': self._handle_implode_planet_click,
            'STELLERATE_STAR_TARGET': self._handle_stellerate_star_click,
            'OPEN_WARP_TARGET': self._handle_open_warp_click,
            'CLOSE_WARP_TARGET': self._handle_close_warp_click,
            'DYSON_SPHERE_TARGET': self._handle_dyson_sphere_click,
            'SELECT': self._handle_select_mode_click,
        }

    @property
    def scene(self):
        """Access scene through handler."""
        return self._handler.scene

    @property
    def input_mode(self) -> str:
        """Get current input mode from handler."""
        return self._handler.input_mode

    @input_mode.setter
    def input_mode(self, value: str) -> None:
        """Set input mode on handler."""
        self._handler.input_mode = value

    def dispatch_click(self, mx: int, my: int, button: int) -> bool:
        """Dispatch click to appropriate mode handler.

        Args:
            mx: Mouse x screen coordinate.
            my: Mouse y screen coordinate.
            button: Mouse button (1=left, 3=right).

        Returns:
            True if click was handled, False otherwise.
        """
        handler = self._mode_handlers.get(self.input_mode)
        if handler:
            return handler(mx, my, button)
        return False

    # =========================================================================
    # Mode Click Handlers
    # =========================================================================

    def _handle_move_mode_click(self, mx: int, my: int, button: int) -> bool:
        """Handle click in MOVE mode."""
        if button == 1:  # Left Click
            result = self.scene._fleet_ops.handle_move_designation(
                mx, my, self.scene.selected_fleet
            )
            if result and result.get('type') == 'choice':
                # Prompt user for move vs intercept
                target_hex = result['target_hex']
                target_fleet = result['target_fleet']

                def on_move():
                    res = self.scene._fleet_ops.execute_move(
                        self.scene.selected_fleet, target_hex
                    )
                    if res and res.get('type') == 'success':
                        self._handler._fleet_router.finish_move_action(res['fleet'])

                def on_intercept():
                    res = self.scene._fleet_ops.execute_intercept(
                        self.scene.selected_fleet, target_fleet
                    )
                    if res and res.get('type') == 'success':
                        self._handler._fleet_router.finish_move_action(res['fleet'])

                self.scene.ui.prompt_move_choice(
                    target_fleet, target_hex, on_move, on_intercept
                )
            elif result and result.get('type') == 'success':
                self._handler._fleet_router.finish_move_action(result['fleet'])
            else:
                # BUG-93: Error or no result — exit MOVE mode to prevent trapping
                self.input_mode = 'SELECT'
                logger.debug("Input Mode: SELECT (move failed)")
            return True

        elif button == 3:  # Right click cancels
            self.input_mode = 'SELECT'
            logger.debug("Input Mode: SELECT")
            return True

        return False

    def _handle_join_mode_click(self, mx: int, my: int, button: int) -> bool:
        """Handle click in JOIN mode."""
        if button == 1:  # Left Click
            result = self.scene._fleet_ops.handle_join_designation(
                mx, my, self.scene.selected_fleet
            )
            if result and result.get('type') == 'choice':
                # Multiple valid fleets — prompt user to select
                fleets = result['fleets']
                fleet_ref = self.scene.selected_fleet

                def on_fleet_selected(target_fleet):
                    res = self.scene._fleet_ops.execute_join(fleet_ref, target_fleet)
                    if res and res.get('type') == 'success':
                        self.input_mode = 'SELECT'
                        self.scene.on_ui_selection(res['fleet'])

                self.scene.ui.prompt_fleet_selection(fleets, on_fleet_selected)

            elif result and result.get('type') == 'success':
                self.input_mode = 'SELECT'
                self.scene.on_ui_selection(result['fleet'])
            return True

        elif button == 3:  # Right click cancels
            self.input_mode = 'SELECT'
            logger.debug("Input Mode: SELECT")
            return True

        return False

    def _handle_colonize_mode_click(self, mx: int, my: int, button: int) -> bool:
        """Handle click in COLONIZE_TARGET mode."""
        if button == 1:  # Left Click
            result = self.scene._colonization.handle_colonize_designation(
                mx, my, self.scene.selected_fleet
            )

            if result and result.get('type') == 'prompt':
                # Capture fleet reference for callback
                fleet_ref = self.scene.selected_fleet

                def on_selected(planet):
                    self.scene._colonization.queue_colonize_mission(
                        result['target_hex'], planet, fleet_ref
                    )
                    if self.scene.selected_fleet == fleet_ref:
                        self.scene.on_ui_selection(self.scene.selected_fleet)

                self.scene.ui.prompt_planet_selection(result['planets'], on_selected)

            elif result and result.get('type') == 'success':
                self.scene.on_ui_selection(self.scene.selected_fleet)

            self.input_mode = 'SELECT'
            return True

        elif button == 3:  # Right click cancels
            self.input_mode = 'SELECT'
            logger.debug("Input Mode: SELECT")
            return True

        return False

    def _handle_transfer_mode_click(self, mx: int, my: int, button: int) -> bool:
        """Handle click in TRANSFER mode."""
        if button == 1:  # Left Click
            target_hex = self._resolve_click_target(mx, my)
            fleet = self.scene.selected_fleet
            self.scene.ui.open_transfer_dialog(fleet, target_hex)
            self.input_mode = 'SELECT'
            return True
        elif button == 3:  # Right click cancels
            self.input_mode = 'SELECT'
            logger.debug("Input Mode: SELECT")
            return True
        return False

    def _handle_drop_cargo_mode_click(self, mx: int, my: int, button: int) -> bool:
        """Handle click in DROP_CARGO mode."""
        if button == 1:  # Left Click
            target_hex = self._resolve_click_target(mx, my)
            fleet = self.scene.selected_fleet
            self.scene.ui.open_cargo_quick_dialog(fleet, target_hex, 'unload')
            self.input_mode = 'SELECT'
            return True
        elif button == 3:  # Right click cancels
            self.input_mode = 'SELECT'
            logger.debug("Input Mode: SELECT")
            return True
        return False

    def _handle_load_cargo_mode_click(self, mx: int, my: int, button: int) -> bool:
        """Handle click in LOAD_CARGO mode."""
        if button == 1:  # Left Click
            target_hex = self._resolve_click_target(mx, my)
            fleet = self.scene.selected_fleet
            self.scene.ui.open_cargo_quick_dialog(fleet, target_hex, 'load')
            self.input_mode = 'SELECT'
            return True
        elif button == 3:  # Right click cancels
            self.input_mode = 'SELECT'
            logger.debug("Input Mode: SELECT")
            return True
        return False

    def _handle_warp_target_click(self, mx: int, my: int, button: int) -> bool:
        """Handle click in WARP_TARGET mode — issue warp order to clicked warp point."""
        if button == 1:  # Left Click
            target_hex = self._resolve_click_target(mx, my)
            fleet = self.scene.selected_fleet
            if fleet:
                from game.strategy.engine.commands import IssueWarpCommand
                cmd = IssueWarpCommand(fleet.id, target_hex)
                result = self.scene.facade.handle_command(cmd)
                if result and result.is_valid:
                    self.input_mode = 'SELECT'
                    self.scene.on_ui_selection(fleet)
                else:
                    msg = result.error_message if result else "Unknown error"
                    logger.warning("Warp order failed: %s", msg)
            return True
        elif button == 3:  # Right click cancels
            self.input_mode = 'SELECT'
            logger.debug("Input Mode: SELECT")
            return True
        return False

    def _handle_implode_planet_click(self, mx: int, my: int, button: int) -> bool:
        """Handle click in IMPLODE_PLANET_TARGET mode."""
        if button == 1:  # Left Click
            result = self.scene._superweapons.handle_implode_planet_designation(
                mx, my, self.scene.selected_fleet
            )
            if result:
                self.input_mode = 'SELECT'
            return True
        elif button == 3:  # Right click cancels
            self.input_mode = 'SELECT'
            logger.debug("Input Mode: SELECT")
            return True
        return False

    def _handle_stellerate_star_click(self, mx: int, my: int, button: int) -> bool:
        """Handle click in STELLERATE_STAR_TARGET mode."""
        if button == 1:  # Left Click
            result = self.scene._superweapons.handle_stellerate_star_designation(
                mx, my, self.scene.selected_fleet
            )
            if result:
                self.input_mode = 'SELECT'
            return True
        elif button == 3:  # Right click cancels
            self.input_mode = 'SELECT'
            logger.debug("Input Mode: SELECT")
            return True
        return False

    def _handle_open_warp_click(self, mx: int, my: int, button: int) -> bool:
        """Handle click in OPEN_WARP_TARGET mode."""
        if button == 1:  # Left Click
            result = self.scene._superweapons.handle_open_warp_designation(
                mx, my, self.scene.selected_fleet
            )
            if result:
                self.input_mode = 'SELECT'
            return True
        elif button == 3:  # Right click cancels
            self.input_mode = 'SELECT'
            logger.debug("Input Mode: SELECT")
            return True
        return False

    def _handle_close_warp_click(self, mx: int, my: int, button: int) -> bool:
        """Handle click in CLOSE_WARP_TARGET mode."""
        if button == 1:  # Left Click
            result = self.scene._superweapons.handle_close_warp_designation(
                mx, my, self.scene.selected_fleet
            )
            if result:
                self.input_mode = 'SELECT'
            return True
        elif button == 3:  # Right click cancels
            self.input_mode = 'SELECT'
            logger.debug("Input Mode: SELECT")
            return True
        return False

    def _handle_dyson_sphere_click(self, mx: int, my: int, button: int) -> bool:
        """Handle click in DYSON_SPHERE_TARGET mode."""
        if button == 1:  # Left Click
            result = self.scene._superweapons.handle_dyson_sphere_designation(
                mx, my, self.scene.selected_fleet
            )
            if result:
                self.input_mode = 'SELECT'
            return True
        elif button == 3:  # Right click cancels
            self.input_mode = 'SELECT'
            logger.debug("Input Mode: SELECT")
            return True
        return False

    def _handle_select_mode_click(self, mx: int, my: int, button: int) -> bool:
        """Handle click in SELECT mode."""
        if button == 1:  # Left Click: Select
            self._handle_picking(mx, my)
            return True

        elif button == 3:  # Right Click: Quick Move
            if self.scene.selected_fleet:
                result = self.scene._fleet_ops.handle_move_designation(
                    mx, my, self.scene.selected_fleet
                )
                if result and result.get('type') == 'choice':
                    target_hex = result['target_hex']
                    target_fleet = result['target_fleet']

                    def on_move():
                        res = self.scene._fleet_ops.execute_move(
                            self.scene.selected_fleet, target_hex
                        )
                        if res and res.get('type') == 'success':
                            self._handler._fleet_router.finish_move_action(res['fleet'])

                    def on_intercept():
                        res = self.scene._fleet_ops.execute_intercept(
                            self.scene.selected_fleet, target_fleet
                        )
                        if res and res.get('type') == 'success':
                            self._handler._fleet_router.finish_move_action(res['fleet'])

                    self.scene.ui.prompt_move_choice(
                        target_fleet, target_hex, on_move, on_intercept
                    )
                elif result and result.get('type') == 'success':
                    self._handler._fleet_router.finish_move_action(result['fleet'])
                return True

        return False

    # =========================================================================
    # Picking / Hit Testing Methods
    # =========================================================================

    def _hit_test_planets(self, mx: int, my: int, system) -> Optional[object]:
        """Hit-test click against expanded planet positions when zoomed in.

        Args:
            mx: Screen x coordinate of click.
            my: Screen y coordinate of click.
            system: StarSystem to check planets in.

        Returns:
            Planet if clicked, None otherwise.
        """
        from game.core.hex_math import hex_to_pixel

        # Group planets by hex (same as renderer)
        hex_groups = {}
        for p in system.planets:
            key = (p.location.q, p.location.r)
            if key not in hex_groups:
                hex_groups[key] = []
            hex_groups[key].append(p)

        camera = self.scene.camera
        hex_size = self.scene.hex_size

        # Same expansion parameters as renderer
        EXPAND_START = 1.5
        EXPAND_END = 2.0
        expansion_t = max(0.0, min(1.0, (camera.zoom - EXPAND_START) / (EXPAND_END - EXPAND_START)))

        hex_px_radius = hex_size * camera.zoom

        sys_hx, sys_hy = hex_to_pixel(system.global_location, hex_size)
        sys_world_pos = pygame.math.Vector2(sys_hx, sys_hy)

        for key, planets in hex_groups.items():
            coord = planets[0].location
            px, py = hex_to_pixel(coord, hex_size)
            hex_center_world = pygame.math.Vector2(sys_world_pos.x + px, sys_world_pos.y + py)
            hex_center_screen = camera.world_to_screen(hex_center_world)

            if len(planets) > 1:
                planets_sorted = sorted(planets, key=lambda x: x.mass, reverse=True)
                largest = planets_sorted[0]

                largest_draw_r = hex_px_radius * 0.5
                largest_diameter = largest_draw_r * 2
                group_offset_x = -largest_diameter * 0.20

                # Angles for smaller planets (must match strategy_renderer.py Rev 5 values)
                smaller_count = len(planets_sorted) - 1
                if smaller_count == 1:
                    smaller_angles = [0]  # Right of largest
                elif smaller_count == 2:
                    smaller_angles = [40, -40]  # 40° above and below horizontal
                elif smaller_count == 3:
                    smaller_angles = [46, 0, -46]  # 46° up, horizontal, 46° down
                elif smaller_count == 4:
                    smaller_angles = [58, 23, -23, -58]  # Even spread
                elif smaller_count == 5:
                    smaller_angles = [63, 31, 0, -31, -63]  # Even spread
                else:
                    # 6+ planets: spread evenly from 70° to -80° (150° arc)
                    smaller_angles = [70 - i * (150 / max(1, smaller_count - 1)) for i in range(smaller_count)]

                for i, p in enumerate(planets_sorted):
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
                        idx = planets_sorted.index(p) - 1
                        angle = smaller_angles[idx] if idx < len(smaller_angles) else 0
                        dist = largest_draw_r * 1.5
                        final_offset = pygame.math.Vector2(group_offset_x + dist, 0).rotate(-angle)

                    current_offset = final_offset * expansion_t
                    p_screen = hex_center_screen + current_offset

                    # Hit test: check if click is within planet's drawn radius
                    dx = mx - p_screen.x
                    dy = my - p_screen.y
                    dist_sq = dx * dx + dy * dy
                    # Add small margin for easier clicking
                    click_radius = draw_r + 4
                    if dist_sq <= click_radius * click_radius:
                        return p
            else:
                # Single planet - check centered position
                p = planets[0]
                base_r = 5 * camera.zoom
                if 'Giant' in p.planet_type.name:
                    base_r *= 1.5

                dx = mx - hex_center_screen.x
                dy = my - hex_center_screen.y
                dist_sq = dx * dx + dy * dy
                click_radius = base_r + 4
                if dist_sq <= click_radius * click_radius:
                    return p

        return None

    def _resolve_click_target(self, mx: int, my: int):
        """Smartly resolve the hex coordinate from a mouse click.

        Handles visual offsets of planets when zoomed in, ensuring we return
        the logical hex of a clicked planet, rather than the raw pixel-to-hex result.

        Args:
            mx: Screen x coordinate of click.
            my: Screen y coordinate of click.

        Returns:
            HexCoord: The logical hex coordinate to use for targeting.
        """
        # 1. Raw conversion
        world_pos = self.scene.camera.screen_to_world((mx, my))
        raw_hex = pixel_to_hex(world_pos.x, world_pos.y, self.scene.hex_size)

        # 2. Check for system context
        # Use existing logic to find system (handles radius search)
        system = self.scene._get_system_at_hex(raw_hex)

        if system and self.scene.camera.zoom >= 0.5:
            # 3. Hit test visual planets (if zoomed enough to see them)
            # _hit_test_planets handles the visual offset logic
            hit_planet = self._hit_test_planets(mx, my, system)
            if hit_planet:
                # Return the true logical location of the planet
                return system.global_location + hit_planet.location

        return raw_hex

    def _handle_picking(self, mx: int, my: int) -> None:
        """Raycast from screen to galaxy objects.

        Args:
            mx: Screen x coordinate of click.
            my: Screen y coordinate of click.
        """
        world_pos = self.scene.camera.screen_to_world((mx, my))
        hex_clicked = pixel_to_hex(world_pos.x, world_pos.y, self.scene.hex_size)

        clicked_system = self.scene._get_system_at_hex(hex_clicked)
        sector_contents = []

        # Check Fleets (All Empires)
        for emp in self.scene.empires:
            for f in emp.fleets:
                if f.location == hex_clicked:
                    sector_contents.append(f)

        # When zoomed in, use hit-testing against planet screen positions
        clicked_planet = None
        if clicked_system and self.scene.camera.zoom >= 1.5:
            clicked_planet = self._hit_test_planets(mx, my, clicked_system)

        if clicked_system:
            for p in clicked_system.planets:
                p_global = clicked_system.global_location + p.location
                if p_global == hex_clicked:
                    # If we hit-tested a specific planet, put it first
                    if clicked_planet == p:
                        sector_contents.insert(0, p)
                    else:
                        sector_contents.append(p)

            for wp in clicked_system.warp_points:
                wp_global = clicked_system.global_location + wp.location
                if wp_global == hex_clicked:
                    sector_contents.append(wp)

            for star in clicked_system.stars:
                s_global = clicked_system.global_location + star.location
                if s_global == hex_clicked:
                    sector_contents.append(star)

            # Always include Environmental Data (Radiation)

        # PROJ-139: Check zone registry for multi-hex objects (stars, Dyson Spheres)
        # Zone objects may be found even without a clicked_system match
        if self.scene.galaxy:
            zone_objects = self.scene.galaxy.get_zones_at_global_hex(hex_clicked)
            for zone_obj in zone_objects:
                if zone_obj not in sector_contents:
                    sector_contents.append(zone_obj)

        if clicked_system:
            from game.strategy.data.physics import SectorEnvironment
            local_hex = hex_clicked - clicked_system.global_location
            env = SectorEnvironment(local_hex, clicked_system)
            sector_contents.append(env)

        # Update System Panel
        if clicked_system:
            sys_contents = [clicked_system]
            sys_contents.extend(clicked_system.stars)
            sys_contents.extend(clicked_system.planets)
            sys_contents.extend(clicked_system.warp_points)
            self.scene.ui.show_system_info(clicked_system, sys_contents)
            # Track this system for Shift+S zoom
            self.scene.last_selected_system = clicked_system
        else:
            self.scene.ui.show_system_info(None, [])

        # Update Sector Panel
        self.scene.ui.show_sector_info(hex_clicked, sector_contents)

        # Determine best pick
        best_pick = None
        if sector_contents:
            best_pick = sector_contents[0]

        if best_pick:
            self.scene.on_ui_selection(best_pick)
            self.scene.selected_object = best_pick
        elif clicked_system:
            self.scene.on_ui_selection(clicked_system)
            self.scene.selected_object = clicked_system
        else:
            self.scene.selected_object = None
            self.scene.ui.show_detailed_report(None, None)
