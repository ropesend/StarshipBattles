"""
Input handling for strategy scene.
Routes keyboard and mouse events to appropriate handlers.

Extracted from StrategyScene to reduce file size and improve testability.
"""
import pygame
import pygame_gui
from game.core.logger import log_debug
from game.strategy.data.hex_math import pixel_to_hex
from game.strategy.data.fleet import Fleet


class InputHandler:
    """Routes input events for strategy scene."""

    def __init__(self, scene):
        """
        Initialize input handler.

        Args:
            scene: StrategyScene instance providing state and sub-modules
        """
        self.scene = scene
        self.input_mode = 'SELECT'

    def handle_event(self, event):
        """
        Process pygame events.

        Args:
            event: Pygame event to process
        """
        self.scene.ui.handle_event(event)

        # Button Events
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            self._handle_button_press(event)

        # Keyboard Events
        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event)

    def _handle_button_press(self, event):
        """Handle UI button presses."""
        ui = self.scene.ui

        if event.ui_element == ui.btn_next_turn:
            self.scene.advance_turn()
        elif event.ui_element == ui.btn_colonize:
            self.scene.on_colonize_click()
        elif event.ui_element == ui.btn_build_ship:
            self.scene.on_build_ship_click()
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
        """Handle keyboard input."""
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
            if self.input_mode in ('MOVE', 'COLONIZE_TARGET', 'JOIN'):
                self.input_mode = 'SELECT'
                log_debug("Input Mode: SELECT")

        elif event.key == pygame.K_c:
            if self.scene.selected_fleet:
                self.input_mode = 'COLONIZE_TARGET'
                log_debug("Input Mode: COLONIZE - Select target planet.")
            else:
                log_debug("Select a fleet first.")

        # Quick Zoom Shortcuts
        elif event.key == pygame.K_g and (event.mod & pygame.KMOD_SHIFT):
            self.scene._camera_nav.zoom_to_galaxy()
        elif event.key == pygame.K_s and (event.mod & pygame.KMOD_SHIFT):
            self.scene._camera_nav.zoom_to_system()

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

    def _handle_picking(self, mx, my):
        """Raycast from screen to galaxy objects."""
        world_pos = self.scene.camera.screen_to_world((mx, my))
        hex_clicked = pixel_to_hex(world_pos.x, world_pos.y, self.scene.HEX_SIZE)

        clicked_system = self.scene._get_system_at_hex(hex_clicked)
        sector_contents = []

        # Check Fleets (All Empires)
        for emp in self.scene.empires:
            for f in emp.fleets:
                if f.location == hex_clicked:
                    sector_contents.append(f)

        if clicked_system:
            for p in clicked_system.planets:
                p_global = clicked_system.global_location + p.location
                if p_global == hex_clicked:
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

    def update_input(self, dt, events):
        """
        Update camera input.

        Args:
            dt: Delta time
            events: List of pygame events
        """
        # Filter events for Camera: Block MouseWheel if over sidebar
        cam_events = []
        mx, my = pygame.mouse.get_pos()
        over_sidebar = (mx > self.scene.screen_width - self.scene.SIDEBAR_WIDTH)
        over_topbar = (my < self.scene.TOP_BAR_HEIGHT)

        for e in events:
            if e.type == pygame.MOUSEWHEEL:
                if over_sidebar or over_topbar:
                    continue
            cam_events.append(e)

        self.scene.camera.update_input(dt, cam_events)

        # Hover Logic
        world_pos = self.scene.camera.screen_to_world((mx, my))
        self.scene.hover_hex = pixel_to_hex(world_pos.x, world_pos.y, self.scene.HEX_SIZE)
