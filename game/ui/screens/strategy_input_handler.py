"""
Input handling for strategy scene.
Routes keyboard and mouse events to appropriate handlers.

Extracted from StrategyScreen to reduce file size and improve testability.
PROJ-71: Refactored to use InputMapper for data-driven keybinding resolution.
"""
from __future__ import annotations

import logging
import pygame
import pygame_gui

logger = logging.getLogger(__name__)
from game.ui.config import UIConfig
from game.ui.screens.strategy_fleet_command_router import FleetCommandRouter
from game.ui.screens.strategy_click_dispatcher import ClickModeDispatcher
from game.ui.screens.strategy_ui_action_router import UIActionRouter
from game.core.hex_math import pixel_to_hex

class StrategyInputHandler:
    """Routes input events for strategy scene.

    Keyboard events are resolved through the centralized InputMapper binding
    table (PROJ-71). An InputMapper must be provided for keyboard input to work.
    """

    def __init__(self, scene, input_mapper=None):
        """Initialize input handler.

        Args:
            scene: StrategyScreen instance providing state and sub-modules.
            input_mapper: InputMapper for centralized keybinding resolution.
                         Required for keyboard input to function.
        """
        self.scene = scene
        self._mapper = input_mapper
        self.input_mode = 'SELECT'
        self._fleet_router = FleetCommandRouter(self)
        self._click_dispatch = ClickModeDispatcher(self)
        self._ui_router = UIActionRouter(self)

    def handle_event(self, event):
        """
        Process pygame events.

        Handles all event types through IScene.handle_event() instead of
        requiring separate dispatch from app.py (PROJ-88 Phase 5).

        Args:
            event: Pygame event to process
        """
        # If build queue screen is open, route events to it first
        if self.scene.build_queue_screen is not None:
            self.scene.build_queue_screen.handle_event(event)
            return

        # If planet list window is open, let pygame_gui handle it (skip our F11/F12)
        # BUG FIX PROJ-198 Phase 4: planet_list_window is on window_manager, not ui
        if self.scene.ui.window_manager.planet_list_window is not None:
            self.scene.ui.handle_event(event)
            return

        self.scene.ui.handle_event(event)

        # Button Events
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            self._handle_button_press(event)

        # Keyboard Events
        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event)

        # Mouse Click Events (PROJ-88: moved from app.py)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            self.handle_click(mx, my, event.button)

        # Mouse Wheel Events (PROJ-88: moved from app.py)
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
        elif event.ui_element == ui.btn_abilities:
            current_sel = getattr(self.scene.ui, 'current_selection', None)
            if current_sel:
                self.scene.ui.open_planet_abilities_window(current_sel)
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
        """Handle keyboard input via InputMapper."""
        if self._mapper:
            self._handle_keydown_mapped(event)
        # No mapper = no keyboard input (mapper is required)

    def _handle_keydown_mapped(self, event):
        """Handle keyboard input using InputMapper (PROJ-71)."""
        # Build context list based on current state
        contexts = ["strategy", "global", "detail_panel"]
        if self.scene.selected_fleet or self.input_mode in ('MOVE', 'JOIN', 'COLONIZE_TARGET', 'TRANSFER', 'DROP_CARGO', 'LOAD_CARGO',
                                                                'WARP_TARGET', 'IMPLODE_PLANET_TARGET', 'STELLERATE_STAR_TARGET',
                                                                'OPEN_WARP_TARGET', 'CLOSE_WARP_TARGET', 'DYSON_SPHERE_TARGET',
                                                                'EDIT_MOVE'):
            contexts.append("fleet")
        # PROJ-238: Add planet context when planet is selected
        from game.core.protocols import is_planet
        current_sel = getattr(self.scene.ui, 'current_selection', None)
        if current_sel and is_planet(current_sel):
            contexts.append("planet")

        action = self._mapper.resolve(event, contexts)
        if action is None:
            return

        # Try each category handler in order
        if self._fleet_router.handle_fleet_action(action):
            return
        if self._fleet_router.handle_superweapon_action(action):
            return
        if self._ui_router.handle_ui_action(action):
            return
        if self._fleet_router.handle_detail_action(action):
            return

    def handle_click(self, mx, my, button):
        """Handle mouse clicks.

        Args:
            mx, my: Mouse screen coordinates.
            button: Mouse button (1=left, 3=right).

        Returns:
            True if click was handled, False otherwise.
        """
        ui_handled = self.scene.ui.handle_click(mx, my, button)
        if ui_handled:
            return True
        return self._click_dispatch.dispatch_click(mx, my, button)

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
        # StrategyScreen.ui always has _has_modal_open method
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
        # PROJ-CAMERA: Disable WASD panning in strategy layer to avoid command conflicts
        self.scene.camera.update_input(dt, cam_events, allow_wasd=False)

        # Hover Logic
        mx, my = pygame.mouse.get_pos()
        world_pos = self.scene.camera.screen_to_world((mx, my))
        self.scene.hover_hex = pixel_to_hex(world_pos.x, world_pos.y, self.scene.hex_size)
