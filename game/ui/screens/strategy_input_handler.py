"""
Input handling for strategy scene.
Routes keyboard and mouse events to appropriate handlers.

Extracted from StrategyScreen to reduce file size and improve testability.
PROJ-71: Refactored to use InputMapper for data-driven keybinding resolution.
"""
from __future__ import annotations

from typing import Optional

import pygame
import pygame_gui
from game.core.config import UIConfig
from game.core.input_actions import InputAction
from game.core.logger import log_debug, log_info, log_warning
from game.core.screenshot_manager import ScreenshotManager
from game.core.hex_math import pixel_to_hex


class StrategyInputHandler:
    """Routes input events for strategy scene.

    When an InputMapper is provided, keyboard events are resolved through
    the centralized binding table. Without a mapper, falls back to the
    original hardcoded pygame key checks (backward compat).
    """

    def __init__(self, scene, input_mapper=None):
        """Initialize input handler.

        Args:
            scene: StrategyScreen instance providing state and sub-modules.
            input_mapper: Optional InputMapper for centralized keybinding
                         resolution (PROJ-71).
        """
        self.scene = scene
        self._mapper = input_mapper
        self.input_mode = 'SELECT'

    def handle_event(self, event):
        """
        Process pygame events.

        Handles all event types through IScene.handle_event() instead of
        requiring separate dispatch from app.py (PROJ-88 Phase 5).

        Args:
            event: Pygame event to process
        """
        # If build queue screen is open, route events to it first
        if hasattr(self.scene, 'build_queue_screen') and self.scene.build_queue_screen is not None:
            self.scene.build_queue_screen.handle_event(event)
            return

        # If planet list window is open, let pygame_gui handle it (skip our F11/F12)
        if hasattr(self.scene, 'ui') and hasattr(self.scene.ui, 'planet_list_window') and self.scene.ui.planet_list_window is not None:
            self.scene.ui.handle_event(event)
            return

        self.scene.ui.handle_event(event)

        # Button Events
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            self._handle_button_press(event)

        # Keyboard Events
        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event)

        # Mouse Click Events (PROJ-88: folded from app.py legacy dispatch)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            self.handle_click(mx, my, event.button)

        # Mouse Wheel Events (PROJ-88: folded from app.py legacy dispatch)
        elif event.type == pygame.MOUSEWHEEL:
            self._handle_scroll(event)

    def _handle_button_press(self, event):
        """Handle UI button presses."""
        ui = self.scene.ui

        if event.ui_element == ui.btn_next_turn:
            self.scene.advance_turn()
        elif event.ui_element == ui.btn_colonize:
            self.scene.on_colonize_click()
        elif event.ui_element == ui.btn_build_yard:
            self.scene.on_build_yard_click()
        elif event.ui_element == ui.btn_build_fleet:
            self.scene.on_fleet_build_click()
        # Navigation
        elif event.ui_element == ui.btn_prev_colony:
            self.scene.cycle_selection('colony', -1)
        elif event.ui_element == ui.btn_next_colony:
            self.scene.cycle_selection('colony', 1)
        elif event.ui_element == ui.btn_prev_fleet:
            self.scene.cycle_selection('fleet', -1)
        elif event.ui_element == ui.btn_next_fleet:
            self.scene.cycle_selection('fleet', 1)

    def _handle_keydown(self, event):
        """Handle keyboard input via InputMapper or legacy fallback."""
        if self._mapper:
            self._handle_keydown_mapped(event)
        else:
            self._handle_keydown_legacy(event)

    def _handle_keydown_mapped(self, event):
        """Handle keyboard input using InputMapper (PROJ-71)."""
        # Build context list based on current state
        contexts = ["strategy", "global", "detail_panel"]
        if self.scene.selected_fleet or self.input_mode in ('MOVE', 'JOIN', 'COLONIZE_TARGET', 'TRANSFER', 'DROP_CARGO', 'LOAD_CARGO'):
            contexts.append("fleet")

        action = self._mapper.resolve(event, contexts)
        if action is None:
            return

        # --- Fleet mode commands ---
        if action == InputAction.FLEET_MOVE:
            if self.scene.selected_fleet:
                self.input_mode = 'MOVE'
                log_debug("Input Mode: MOVE - Click destination for fleet.")
            else:
                log_debug("Select a fleet first.")

        elif action == InputAction.FLEET_JOIN:
            if self.scene.selected_fleet:
                self.input_mode = 'JOIN'
                log_debug("Input Mode: JOIN - Select fleet to join.")
            else:
                log_debug("Select a fleet first.")

        elif action == InputAction.FLEET_COLONIZE:
            if self.scene.selected_fleet:
                self.input_mode = 'COLONIZE_TARGET'
                log_debug("Input Mode: COLONIZE - Select target planet.")
            else:
                log_debug("Select a fleet first.")

        elif action == InputAction.FLEET_TRANSFER:
            if self.scene.selected_fleet:
                self.input_mode = 'TRANSFER'
                log_debug("Input Mode: TRANSFER - Click destination hex for transfer.")
            else:
                log_debug("Select a fleet first for transfer.")

        elif action == InputAction.FLEET_DROP_CARGO:
            if self.scene.selected_fleet:
                self.input_mode = 'DROP_CARGO'
                log_debug("Input Mode: DROP_CARGO - Click target hex.")
            else:
                log_debug("Select a fleet first.")

        elif action == InputAction.FLEET_LOAD_CARGO:
            if self.scene.selected_fleet:
                self.input_mode = 'LOAD_CARGO'
                log_debug("Input Mode: LOAD_CARGO - Click target hex.")
            else:
                log_debug("Select a fleet first.")

        elif action == InputAction.FLEET_CANCEL_MODE:
            if self.input_mode in ('MOVE', 'COLONIZE_TARGET', 'JOIN', 'TRANSFER', 'DROP_CARGO', 'LOAD_CARGO'):
                self.input_mode = 'SELECT'
                log_debug("Input Mode: SELECT")

        # --- Zoom shortcuts ---
        elif action == InputAction.STRATEGY_ZOOM_GALAXY:
            self.scene._camera_nav.zoom_to_galaxy()
        elif action == InputAction.STRATEGY_ZOOM_SYSTEM:
            self.scene._camera_nav.zoom_to_system()

        # --- Screenshot shortcuts ---
        elif action == InputAction.GLOBAL_SCREENSHOT_FULL:
            self._take_screenshot_full()
        elif action == InputAction.GLOBAL_SCREENSHOT_VIEWPORT:
            self._take_screenshot_viewport()

        # --- Button-triggered actions (Task 2.5) ---
        elif action == InputAction.STRATEGY_NEXT_TURN:
            self.scene.advance_turn()
        elif action == InputAction.STRATEGY_OPEN_PLANETS:
            self.scene.ui.open_planet_list()
        elif action == InputAction.STRATEGY_OPEN_DESIGN:
            self.scene.on_design_click()
        elif action == InputAction.STRATEGY_OPEN_BUILD_QUEUES:
            self.scene.ui.open_build_queue_list()
        elif action == InputAction.STRATEGY_OPEN_EMPIRE:
            self.scene.ui.open_empire_panel()
        elif action == InputAction.STRATEGY_SAVE_GAME:
            self.scene.on_save_game_click()
        elif action == InputAction.STRATEGY_PREV_COLONY:
            self.scene.cycle_selection('colony', -1)
        elif action == InputAction.STRATEGY_NEXT_COLONY:
            self.scene.cycle_selection('colony', 1)
        elif action == InputAction.STRATEGY_PREV_FLEET:
            self.scene.cycle_selection('fleet', -1)
        elif action == InputAction.STRATEGY_NEXT_FLEET:
            self.scene.cycle_selection('fleet', 1)

        # --- Detail panel fleet commands ---
        elif action == InputAction.DETAIL_PANEL_ORDERS:
            if self.scene.selected_fleet:
                self.scene.ui.open_orders_window(self.scene.selected_fleet)
        elif action == InputAction.DETAIL_PANEL_FLEET_REPORT:
            if self.scene.selected_fleet:
                self.scene.ui.open_fleet_report_window(self.scene.selected_fleet)
        elif action == InputAction.DETAIL_PANEL_BUILD:
            if self.scene.selected_fleet:
                self.scene.on_fleet_build_click()

    def _handle_keydown_legacy(self, event):
        """Handle keyboard input with hardcoded keys (backward compat)."""
        if event.key == pygame.K_m:
            if self.scene.selected_fleet:
                self.input_mode = 'MOVE'
                log_debug("Input Mode: MOVE - Click destination for fleet.")
            else:
                log_debug("Select a fleet first.")

        elif event.key == pygame.K_j:
            if self.scene.selected_fleet:
                self.input_mode = 'JOIN'
                log_debug("Input Mode: JOIN - Select fleet to join.")
            else:
                log_debug("Select a fleet first.")

        elif event.key == pygame.K_ESCAPE:
            if self.input_mode in ('MOVE', 'COLONIZE_TARGET', 'JOIN', 'TRANSFER', 'DROP_CARGO', 'LOAD_CARGO'):
                self.input_mode = 'SELECT'
                log_debug("Input Mode: SELECT")

        elif event.key == pygame.K_c:
            if self.scene.selected_fleet:
                self.input_mode = 'COLONIZE_TARGET'
                log_debug("Input Mode: COLONIZE - Select target planet.")
            else:
                log_debug("Select a fleet first.")

        elif event.key == pygame.K_t:
            if self.scene.selected_fleet:
                self.input_mode = 'TRANSFER'
                log_debug("Input Mode: TRANSFER - Click destination hex for transfer.")
            else:
                log_debug("Select a fleet first for transfer.")

        # Quick Zoom Shortcuts
        elif event.key == pygame.K_g and (event.mod & pygame.KMOD_SHIFT):
            self.scene._camera_nav.zoom_to_galaxy()
        elif event.key == pygame.K_s and (event.mod & pygame.KMOD_SHIFT):
            self.scene._camera_nav.zoom_to_system()

        # Screenshot Shortcuts
        elif event.key == pygame.K_F12:
            self._take_screenshot_full()
        elif event.key == pygame.K_F11:
            self._take_screenshot_viewport()

    def handle_click(self, mx, my, button):
        """
        Handle mouse clicks.

        Args:
            mx, my: Mouse screen coordinates
            button: Mouse button (1=left, 3=right)

        Returns:
            True if click was handled, False otherwise
        """
        if self.scene.ui.handle_click(mx, my, button):
            return True

        if self.input_mode == 'MOVE':
            return self._handle_move_mode_click(mx, my, button)
        elif self.input_mode == 'JOIN':
            return self._handle_join_mode_click(mx, my, button)
        elif self.input_mode == 'COLONIZE_TARGET':
            return self._handle_colonize_mode_click(mx, my, button)
        elif self.input_mode == 'TRANSFER':
            return self._handle_transfer_mode_click(mx, my, button)
        elif self.input_mode == 'DROP_CARGO':
            return self._handle_drop_cargo_mode_click(mx, my, button)
        elif self.input_mode == 'LOAD_CARGO':
            return self._handle_load_cargo_mode_click(mx, my, button)
        elif self.input_mode == 'SELECT':
            return self._handle_select_mode_click(mx, my, button)

        return False

    def _handle_move_mode_click(self, mx, my, button):
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
                        self._finish_move_action(res['fleet'])

                def on_intercept():
                    res = self.scene._fleet_ops.execute_intercept(
                        self.scene.selected_fleet, target_fleet
                    )
                    if res and res.get('type') == 'success':
                        self._finish_move_action(res['fleet'])

                self.scene.ui.prompt_move_choice(
                    target_fleet, target_hex, on_move, on_intercept
                )
            elif result and result.get('type') == 'success':
                self._finish_move_action(result['fleet'])
            return True

        elif button == 3:  # Right click cancels
            self.input_mode = 'SELECT'
            log_debug("Input Mode: SELECT")
            return True

        return False

    def _handle_join_mode_click(self, mx, my, button):
        """Handle click in JOIN mode."""
        if button == 1:  # Left Click
            result = self.scene._fleet_ops.handle_join_designation(
                mx, my, self.scene.selected_fleet
            )
            if result and result.get('type') == 'success':
                self.input_mode = 'SELECT'
                self.scene.on_ui_selection(result['fleet'])
            return True

        elif button == 3:  # Right click cancels
            self.input_mode = 'SELECT'
            log_debug("Input Mode: SELECT")
            return True

        return False

    def _handle_colonize_mode_click(self, mx, my, button):
        """Handle click in COLONIZE_TARGET mode."""
        if button == 1:  # Left Click
            result = self.scene._colonization.handle_colonize_designation(
                mx, my, self.scene.selected_fleet
            )

            if result and result.get('type') == 'prompt':
                # Capture fleet reference for callback
                fleet_ref = self.scene.selected_fleet

                def on_selected(planet):
                    res = self.scene._colonization.queue_colonize_mission(
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
            log_debug("Input Mode: SELECT")
            return True

        return False

    def _handle_transfer_mode_click(self, mx, my, button):
        """Handle click in TRANSFER mode."""
        if button == 1:  # Left Click
            world_pos = self.scene.camera.screen_to_world((mx, my))
            target_hex = pixel_to_hex(world_pos.x, world_pos.y, self.scene.hex_size)
            fleet = self.scene.selected_fleet
            self.scene.ui.open_transfer_dialog(fleet, target_hex)
            self.input_mode = 'SELECT'
            return True
        elif button == 3:  # Right click cancels
            self.input_mode = 'SELECT'
            log_debug("Input Mode: SELECT")
            return True
        return False

    def _handle_drop_cargo_mode_click(self, mx, my, button):
        """Handle click in DROP_CARGO mode."""
        if button == 1:  # Left Click
            world_pos = self.scene.camera.screen_to_world((mx, my))
            target_hex = pixel_to_hex(world_pos.x, world_pos.y, self.scene.hex_size)
            fleet = self.scene.selected_fleet
            self.scene.ui.open_cargo_quick_dialog(fleet, target_hex, 'unload')
            self.input_mode = 'SELECT'
            return True
        elif button == 3:  # Right click cancels
            self.input_mode = 'SELECT'
            log_debug("Input Mode: SELECT")
            return True
        return False

    def _handle_load_cargo_mode_click(self, mx, my, button):
        """Handle click in LOAD_CARGO mode."""
        if button == 1:  # Left Click
            world_pos = self.scene.camera.screen_to_world((mx, my))
            target_hex = pixel_to_hex(world_pos.x, world_pos.y, self.scene.hex_size)
            fleet = self.scene.selected_fleet
            self.scene.ui.open_cargo_quick_dialog(fleet, target_hex, 'load')
            self.input_mode = 'SELECT'
            return True
        elif button == 3:  # Right click cancels
            self.input_mode = 'SELECT'
            log_debug("Input Mode: SELECT")
            return True
        return False

    def _handle_select_mode_click(self, mx, my, button):
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
                            self._finish_move_action(res['fleet'])

                    def on_intercept():
                        res = self.scene._fleet_ops.execute_intercept(
                            self.scene.selected_fleet, target_fleet
                        )
                        if res and res.get('type') == 'success':
                            self._finish_move_action(res['fleet'])

                    self.scene.ui.prompt_move_choice(
                        target_fleet, target_hex, on_move, on_intercept
                    )
                elif result and result.get('type') == 'success':
                    self._finish_move_action(result['fleet'])
                return True

        return False

    def _finish_move_action(self, fleet):
        """Common cleanup after move action."""
        keys = pygame.key.get_pressed()
        if not (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
            self.input_mode = 'SELECT'
        self.scene.on_ui_selection(fleet)

    def _hit_test_planets(self, mx, my, system):
        """
        Hit-test click against expanded planet positions when zoomed in.

        Args:
            mx, my: Screen coordinates of click
            system: StarSystem to check planets in

        Returns:
            Planet if clicked, None otherwise
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

    def _handle_picking(self, mx, my):
        """Raycast from screen to galaxy objects."""
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

    def _handle_scroll(self, event):
        """Handle mouse wheel scroll events (PROJ-88: folded from app.py).

        Forwards scroll events to the camera, filtering based on mouse position
        over UI elements (sidebar, top bar) and modal state.

        Args:
            event: pygame.MOUSEWHEEL event
        """
        mx, my = pygame.mouse.get_pos()
        over_sidebar = (mx > self.scene.screen_width - UIConfig.STRATEGY_SIDEBAR_WIDTH)
        over_topbar = (my < self.scene.TOP_BAR_HEIGHT)

        # Check if modal sub-panel is open (blocks scroll)
        modal_open = False
        if hasattr(self.scene, 'ui') and hasattr(self.scene.ui, '_has_modal_open'):
            modal_open = self.scene.ui._has_modal_open()

        # Block scroll over UI elements or when modal is open
        if over_sidebar or over_topbar or modal_open:
            return

        # Forward to camera as single-event list for its update_input processing
        self.scene.camera.update_input(0, [event])

    def update_input(self, dt, events):
        """
        Update per-frame input state (keyboard polling, hover).

        Note: MOUSEWHEEL events are now handled in handle_event() via _handle_scroll().
        This method handles per-frame keyboard state and hover logic only.

        Args:
            dt: Delta time
            events: List of pygame events (used for camera keyboard polling)
        """
        # Camera processes keyboard input (arrow keys, WASD, middle-mouse drag)
        # Note: MOUSEWHEEL is now filtered out since it's handled in handle_event()
        cam_events = [e for e in events if e.type != pygame.MOUSEWHEEL]
        self.scene.camera.update_input(dt, cam_events)

        # Hover Logic
        mx, my = pygame.mouse.get_pos()
        world_pos = self.scene.camera.screen_to_world((mx, my))
        self.scene.hover_hex = pixel_to_hex(world_pos.x, world_pos.y, self.scene.hex_size)

    # =========================================================================
    # Screenshot Methods
    # =========================================================================

    def _take_screenshot_full(self):
        """Take a full screenshot of the strategy layer including UI."""
        sm = ScreenshotManager.instance()
        sm.capture_strategy_layer(self.scene, include_ui=True, label="strategy_full")
        log_info("Screenshot: Full strategy layer captured (F12)")
        self._show_screenshot_toast("Screenshot saved (full view)")

    def _take_screenshot_viewport(self):
        """Take a screenshot of only the galaxy viewport (no UI)."""
        sm = ScreenshotManager.instance()
        sm.capture_strategy_layer(self.scene, include_ui=False, label="strategy_viewport")
        log_info("Screenshot: Galaxy viewport captured (F11)")
        self._show_screenshot_toast("Screenshot saved (viewport only)")

    def _show_screenshot_toast(self, message):
        """Show a brief toast notification for screenshot feedback."""
        try:
            import pygame_gui.windows
            toast_rect = pygame.Rect(0, 0, UIConfig.TOAST_WIDTH, UIConfig.TOAST_HEIGHT)
            toast_rect.center = (self.scene.screen_width // 2, 80)
            pygame_gui.windows.UIMessageWindow(
                rect=toast_rect,
                html_message=f"<b>{message}</b><br>Path copied to clipboard",
                manager=self.scene.ui.manager,
                window_title="Screenshot"
            )
        except (OSError, RuntimeError, TypeError, pygame.error) as e:
            log_warning(f"Failed to show screenshot toast notification: {e}")
