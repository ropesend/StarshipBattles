"""
StrategyScreen - Main coordinator for strategy layer.

This is the central hub that manages the strategy game state and delegates
to specialized modules for rendering, input handling, and game operations.

Refactored from 1,568 lines to ~350 lines by extracting:
- StrategyRenderer: All drawing logic (~580 lines)
- InputHandler: Event and click routing (~180 lines)
- CameraNavigator: Camera focus and zoom (~90 lines)
- FleetOperations: Fleet movement commands (~130 lines)
- ColonizationSystem: Colonization workflow (~175 lines)

PROJ-40: Use protocol type guards instead of isinstance for cross-layer checks.
"""
from __future__ import annotations

import logging

import pygame
from typing import TYPE_CHECKING, Any
from game.ui.config import UIConfig
from game.core.protocols import is_star, is_planet, is_fleet, is_warp_point, is_star_system

logger = logging.getLogger(__name__)
from game.core.hex_math import hex_to_pixel, HexCoord
from game.strategy.data.order_types import OrderType
from game.ui.renderer.camera import Camera
from game.ui.screens.strategy_ui import StrategyUI

if TYPE_CHECKING:
    from game.strategy.data.galaxy import StarSystem
    from game.strategy.data.fleet import Fleet

# Extracted modules
from game.ui.screens.strategy_renderer import StrategyRenderer
from game.ui.screens.strategy_camera_nav import CameraNavigator
from game.ui.screens.strategy_fleet_ops import FleetOperations
from game.ui.screens.strategy_colonization import ColonizationSystem
from game.ui.screens.strategy_superweapons import SuperweaponOperations
from game.ui.screens.strategy_input_handler import StrategyInputHandler
from game.ui.screens.strategy_build_queue_manager import StrategyBuildQueueManager
from game.ui.screens.strategy_game_state_manager import StrategyGameStateManager
from game.strategy.systems.save_game_service import SaveGameService
from game.strategy.facade.strategy_session_facade import StrategySessionFacade
from game.ui.screens.race_asset_loader import RaceAssetLoader
from game.ui.colors import BG_BATTLE


class StrategyScreen:
    """Manages strategy layer simulation, rendering, and UI.

    Implements IScene protocol for standardized scene handling.
    """

    TOP_BAR_HEIGHT = 50

    def __init__(self, screen_width: int, screen_height: int, session=None, scene_callback=None, input_mapper=None):
        """Initialize strategy screen.

        Args:
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels
            session: Optional GameSession to use (creates new if None)
            scene_callback: Callback function for scene transitions.
                           Called with (action, **kwargs) where action is:
                           - "open_builder": Open design workshop with context kwarg
            input_mapper: Optional InputMapper for centralized keybinding resolution.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.scene_callback = scene_callback
        self.input_mapper = input_mapper

        # Session Management
        if session:
            self.session = session
        else:
            from game.strategy.engine.game_session import GameSession
            from game.ai.ai_factory import AIControllerFactory
            self.session = GameSession(ai_factory=AIControllerFactory())

        # Create facade for UI-to-engine communication
        self._facade = StrategySessionFacade(self.session)

        # Camera
        self.camera = Camera(
            screen_width - UIConfig.STRATEGY_SIDEBAR_WIDTH,
            screen_height - self.TOP_BAR_HEIGHT,
            offset_x=0,
            offset_y=self.TOP_BAR_HEIGHT
        )
        self.camera.max_zoom = 25.0
        self.camera.zoom = 2.0  # Start Zoomed In

        # Focus on Player Home
        self._focus_on_player_home()

        # UI
        self.ui = StrategyUI(self, screen_width, screen_height, input_mapper=input_mapper)

        # State
        self.hover_hex = None
        self.hex_size = 10
        self.detail_zoom_level = 3.0

        self.selected_fleet = None
        self.selected_object = None
        self.last_selected_system = None

        self.turn_processing = False
        self.current_player_index = 0
        self._quit_confirm_dialog = None
        self.build_queue_screen = None

        # FEAT-20: Dev "Run 10 Turns" cancel flag — set by Esc-pump during loop
        self.dev_run_cancel_requested = False
        # FEAT-20: progress text shown by the "PROCESSING TURN..." overlay
        # during dev `run_n_turns`. None means default message.
        self.turn_processing_message: str | None = None

        # Assets
        self.empire_assets = {}
        self._race_loader = RaceAssetLoader()
        self._load_assets()

        # Initialize sub-modules
        self._renderer = StrategyRenderer(self)
        self._camera_nav = CameraNavigator(self)
        self._fleet_ops = FleetOperations(self, self._facade)
        self._colonization = ColonizationSystem(self, self._facade)
        self._superweapons = SuperweaponOperations(self, self._facade)
        self._build_queue = StrategyBuildQueueManager(self)
        self._game_state = StrategyGameStateManager(self)
        self._input = StrategyInputHandler(self, input_mapper=input_mapper)

    # =========================================================================
    # Properties (delegate to session for internal convenience)
    # External callers should use the facade for cross-layer communication.
    # =========================================================================

    @property
    def galaxy(self) -> Any:
        return self.session.galaxy

    @property
    def empires(self) -> Any:
        return self.session.empires

    @property
    def systems(self) -> Any:
        return self.session.systems

    @property
    def active_empire(self) -> Any:
        """The empire whose turn it currently is.

        BUG-125: renamed from `player_empire` (which never rotated and
        silently broke authorization in hot-seat). Delegates to
        `session.active_empire`, which is rotated by
        `StrategyGameStateManager.advance_turn`.
        """
        return self.session.active_empire

    @property
    def enemy_empire(self) -> Any:
        return self.session.enemy_empire

    @property
    def human_player_ids(self) -> Any:
        return self.session.human_player_ids

    @property
    def current_empire(self) -> Any:
        """Get the empire for the current player (supports N players)."""
        current_player_id = self.human_player_ids[self.current_player_index]
        return next((e for e in self.empires if e.id == current_player_id), self.empires[0])

    @property
    def facade(self) -> Any:
        """Public accessor for the strategy session facade.

        Used by dialogs and child components that need to issue commands
        or query game state through the facade pattern.
        """
        return self._facade

    @property
    def input_mode(self) -> Any:
        return self._input.input_mode

    @input_mode.setter
    def input_mode(self, value) -> None:
        self._input.input_mode = value

    # =========================================================================
    # Lifecycle Methods
    # =========================================================================

    def update(self, dt) -> None:
        """Update scene state."""
        self.camera.update(dt)
        self._renderer.update(dt)
        self.ui.update(dt)

    def draw(self, screen) -> None:
        """Render the scene."""
        # Always fill entire screen first to prevent remnants from other screens
        screen.fill(BG_BATTLE)

        self._renderer.draw(screen)

        if self.turn_processing:
            # FEAT-20: dev `run_n_turns` overrides the message with progress text.
            message = getattr(self, 'turn_processing_message', None) or "PROCESSING TURN..."
            self._renderer.draw_processing_overlay(screen, message)

        self.ui.draw(screen)

        # Draw build queue screen overlay (including drag preview)
        if self.build_queue_screen is not None:
            self.build_queue_screen.draw(screen)

    def handle_resize(self, width, height) -> None:
        """Handle window resize."""
        self.screen_width = width
        self.screen_height = height
        self.camera.width = width - UIConfig.STRATEGY_SIDEBAR_WIDTH
        self.camera.height = height - self.TOP_BAR_HEIGHT
        self.camera.offset_y = self.TOP_BAR_HEIGHT
        self.ui.handle_resize(width, height)

    # =========================================================================
    # Event Handling (delegates to InputHandler)
    # =========================================================================

    def handle_event(self, event) -> None:
        """Process pygame events."""
        self._input.handle_event(event)

    def handle_click(self, mx, my, button) -> Any:
        """Handle mouse clicks."""
        return self._input.handle_click(mx, my, button)

    def update_input(self, dt, events) -> None:
        """Update input state."""
        self._input.update_input(dt, events)

    # =========================================================================
    # Navigation (delegates to CameraNavigator)
    # =========================================================================

    def center_camera_on(self, obj) -> None:
        """Center camera on a game object."""
        self._camera_nav.center_on(obj)

    def cycle_selection(self, obj_type, direction) -> None:
        """Cycle selection through colonies or fleets."""
        new_obj = self._camera_nav.cycle_selection(obj_type, direction)
        if new_obj:
            self.on_ui_selection(new_obj)
            self.center_camera_on(new_obj)

    # =========================================================================
    # Colonization (delegates to ColonizationSystem)
    # =========================================================================

    def on_colonize_click(self) -> None:
        """Handle colonize action — always opens load transfer dialog first.

        Flow:
        1. Open transfer dialog to load cargo/population (queues TRANSFER orders)
        2. After dialog closes, input mode enters COLONIZE_TARGET (handled by fleet_command_router)
        3. Player clicks destination → drop dialog opens → colonize + TRANSFER(unload) queued

        The transfer will execute at whatever location the fleet is at when
        the order reaches the front of the queue. If the fleet is not at a
        colony when the transfer executes, the transfer will fail gracefully
        and the fleet continues with remaining orders.
        """
        fleet = self.selected_fleet
        if not fleet:
            return

        # Always open load dialog — player manages logistics
        self.ui.open_transfer_dialog(fleet, fleet.location)
        # Input mode is set to COLONIZE_TARGET by the fleet_command_router
        # regardless of whether the load dialog was opened

    def _on_colonize_planet_selected(self, planet) -> None:
        """Handle planet selection — issue colonize command, then open drop dialog.

        Orders queued: MOVE + COLONIZE, then TRANSFER(unload) from drop dialog.
        """
        fleet = self.selected_fleet
        result = self._colonization.issue_colonize_order(fleet, planet)
        if result and result.get('type') == 'success':
            # Find planet's global hex for the drop transfer dialog
            planet_global_hex = None
            for sys in self.systems:
                if planet in sys.planets:
                    planet_global_hex = sys.global_location + planet.location
                    break
            if planet_global_hex:
                self.ui.open_transfer_dialog(fleet, planet_global_hex)
            self.on_ui_selection(fleet)

    def request_colonize_order(self, fleet, planet=None) -> None:
        """Handle colonize request from UI."""
        # BUG-125: gate against active empire — never select an opponent's
        # fleet for command issuance.
        active = self.session.active_empire
        if active is not None and fleet.owner_id != active.id:
            return
        self.selected_fleet = fleet
        result = self._colonization.request_colonize_order(fleet, planet)
        if result and result.get('type') == 'success':
            self.on_ui_selection(fleet)

    # =========================================================================
    # Order Editing
    # =========================================================================

    # State for EDIT_MOVE mode: ghost hex of old destination
    _edit_move_ghost_hex = None
    _edit_move_order_index = None
    _edit_move_fleet = None

    def on_edit_order(self, entity, order_index, order) -> None:
        """Handle edit request for an order in the queue.

        Args:
            entity: Fleet or planet that owns the order.
            order_index: Index of the order in the queue.
            order: The Order object being edited.
        """
        if order.type == OrderType.MOVE:
            self._start_edit_move(entity, order_index, order)
        elif order.type in (OrderType.TRANSFER, OrderType.LOAD_POPULATION, OrderType.UNLOAD_POPULATION):
            self._start_edit_transfer(entity, order_index, order)

    def _start_edit_move(self, fleet, order_index, order) -> None:
        """Enter EDIT_MOVE mode: pan to old destination, show ghost, wait for new click."""
        old_hex = order.target
        if not isinstance(old_hex, HexCoord):
            return

        # BUG-125: gate against active empire — opponent fleets are
        # informational only (read-only via on_ui_selection's gate).
        active = self.session.active_empire
        if active is not None and fleet.owner_id != active.id:
            return

        self._edit_move_ghost_hex = old_hex
        self._edit_move_order_index = order_index
        self._edit_move_fleet = fleet
        self.selected_fleet = fleet

        # Pan camera to the old destination so the user can see the ghost
        self._camera_nav.center_on_hex(old_hex)
        self.input_mode = 'EDIT_MOVE'

    def complete_edit_move(self, new_hex) -> None:
        """Finalize MOVE order edit: update the order target in-place.

        Args:
            new_hex: The new destination HexCoord selected by the user.
        """
        fleet = self._edit_move_fleet
        idx = self._edit_move_order_index
        if fleet and idx is not None and 0 <= idx < len(fleet.orders):
            order = fleet.orders[idx]
            order.target = new_hex
            # Invalidate path if editing the active (first) order
            if idx == 0:
                fleet.path = []
        # Clear edit state
        self._edit_move_ghost_hex = None
        self._edit_move_order_index = None
        self._edit_move_fleet = None
        self.input_mode = 'SELECT'
        # Refresh the orders window
        if hasattr(self.ui, 'window_manager') and self.ui.window_manager.fleet_orders_window:
            self.ui.window_manager.fleet_orders_window.rebuild_list()
        self.on_ui_selection(fleet)

    def _start_edit_transfer(self, fleet, order_index, order) -> None:
        """Re-open transfer dialog pre-populated with current order amounts."""
        # Determine the hex where this transfer will occur
        # Walk orders up to this index to find the last MOVE destination
        transfer_hex = fleet.location
        for i in range(order_index):
            prev = fleet.orders[i]
            if prev.type == OrderType.MOVE and isinstance(prev.target, HexCoord):
                transfer_hex = prev.target
            elif prev.type == OrderType.WARP and isinstance(prev.target, HexCoord):
                transfer_hex = prev.target

        # Delete the old order, then open transfer dialog at the resolved hex
        # The new dialog will create replacement order(s)
        if 0 <= order_index < len(fleet.orders):
            fleet.orders.pop(order_index)
        self.ui.open_transfer_dialog(fleet, transfer_hex)

    # =========================================================================
    # Turn Management (delegates to GameStateManager)
    # =========================================================================

    def advance_turn(self) -> None:
        """End current player's order phase. Process turn when all humans ready."""
        self._game_state.advance_turn()

    def run_n_turns(self, n: int = 10) -> int:
        """Dev-mode: run N full game turns sequentially (FEAT-20).

        Each iteration runs the full end-turn flow for every player. Esc cancels
        between iterations (never mid-turn — auto-save runs at the end of each
        turn). Per-turn event-log popups are suppressed during the loop and a
        single combined log is surfaced at the end.

        Args:
            n: Number of full turns to run.

        Returns:
            Number of turns actually completed (may be < n if cancelled).
        """
        return self._game_state.run_n_turns(n)

    # =========================================================================
    # Selection
    # =========================================================================

    def on_ui_selection(self, obj) -> None:
        """Called when user selects an item in the UI list."""
        self.selected_object = obj

        # Track last selected system - PROJ-40: Use protocol type guard
        if is_star_system(obj):
            self.last_selected_system = obj
        elif is_planet(obj) or is_warp_point(obj):
            # Planets and warp points have location - find their containing system
            parent_sys = next((s for s in self.systems if obj in s.planets or obj in s.warp_points), None)
            if parent_sys:
                self.last_selected_system = parent_sys

        # Update fleet selection - PROJ-40: Use protocol type guard
        current_player_id = self.human_player_ids[self.current_player_index]
        if is_fleet(obj) and obj.owner_id == current_player_id:
            self.selected_fleet = obj
        else:
            if not is_fleet(obj):
                self.selected_fleet = None

        # Update UI
        img = self._get_object_asset(obj)
        self.ui.show_detailed_report(obj, img)
        
        # PROJ-NEW: If TransferDialog is open, update its selection
        if self.ui.window_manager.transfer_dialog:
            self.ui.window_manager.transfer_dialog.handle_external_selection(obj)

    # =========================================================================
    # Actions
    # =========================================================================

    def on_build_yard_click(self) -> None:
        """Open build queue screen for selected planet."""
        self._build_queue.on_build_yard_click()

    def on_navigate_to_hex_build(self, hex_coord, source) -> None:
        """Navigate to the build queue screen for a specific hex and source."""
        self._build_queue.on_navigate_to_hex_build(hex_coord, source)

    def on_fleet_build_click(self) -> None:
        """Open build queue screen for selected fleet (PROJ-67: Fleet Space Yards)."""
        self._build_queue.on_fleet_build_click()

    def on_design_click(self) -> None:
        """Handle 'Design' button click - opens Design Workshop."""
        logger.debug("Design button clicked - opening Design Workshop")

        # Gather context data for integrated mode
        context_data = {
            'empire': self.session.active_empire,
            'game_session': self.session
        }

        if self.scene_callback:
            self.scene_callback("open_builder", context_data=context_data)

    def on_menu_option(self, option: str) -> None:
        """Dispatch menu option from the strategy menu panel.

        Args:
            option: Option identifier string from StrategyMenuPanel.
        """
        if option == "save_game":
            self.on_save_game_click()
        elif option == "load_game":
            self._show_load_game_dialog()
        elif option == "settings":
            self.ui.window_manager.open_settings()
        elif option == "controls":
            if self.scene_callback:
                self.scene_callback("open_keybindings")
        elif option == "quit_to_menu":
            self._confirm_quit_to_menu()
        elif option == "quit_game":
            if self.scene_callback:
                self.scene_callback("quit_game")

    def _show_load_game_dialog(self) -> None:
        """Open the save selection window for loading a game."""
        from game.ui.screens.save_selection_window import SaveSelectionWindow
        from game.ui.utils import create_centered_rect

        window_rect = create_centered_rect(600, 500, self.screen_width, self.screen_height)
        SaveSelectionWindow(
            window_rect,
            self.ui.manager,
            on_load_callback=self._on_load_selected,
            on_cancel_callback=lambda: None
        )

    def _on_load_selected(self, save_path, turn_number=None) -> None:
        """Handle save selection from load dialog.

        Args:
            save_path: Path to the selected save file.
            turn_number: Optional turn number to load.
        """
        if self.scene_callback:
            self.scene_callback("load_game", save_path=save_path, turn_number=turn_number)

    def _confirm_quit_to_menu(self) -> None:
        """Show confirmation dialog before quitting to main menu."""
        import pygame_gui.windows

        dialog_rect = pygame.Rect(0, 0, UIConfig.CONFIRM_DIALOG_WIDTH, UIConfig.CONFIRM_DIALOG_HEIGHT)
        dialog_rect.center = (self.screen_width // 2, self.screen_height // 2)
        self._quit_confirm_dialog = pygame_gui.windows.UIConfirmationDialog(
            rect=dialog_rect,
            action_long_desc="Unsaved progress will be lost. Return to main menu?",
            manager=self.ui.manager,
            window_title="Quit to Menu"
        )

    def _handle_quit_confirmed(self) -> None:
        """Handle quit-to-menu confirmation dialog result."""
        self._quit_confirm_dialog = None
        if self.scene_callback:
            self.scene_callback("quit_to_menu")

    def _show_coming_soon(self, feature_name: str) -> None:
        """Show a 'Coming Soon' placeholder dialog.

        Args:
            feature_name: Name of the feature to show in the dialog.
        """
        import pygame_gui.windows

        dialog_rect = pygame.Rect(0, 0, UIConfig.CONFIRM_DIALOG_WIDTH, UIConfig.CONFIRM_DIALOG_HEIGHT)
        dialog_rect.center = (self.screen_width // 2, self.screen_height // 2)
        pygame_gui.windows.UIMessageWindow(
            rect=dialog_rect,
            html_message=f"<b>{feature_name}</b><br><br>Coming Soon!",
            manager=self.ui.manager,
            window_title=feature_name
        )

    def on_save_game_click(self) -> None:
        """Handle 'Save Game' button click."""
        from game.strategy.systems.save_game_service import SaveGameService
        import pygame_gui.windows

        logger.info("Saving game...")

        # Save the game
        success, message, save_path = SaveGameService.save_game(self.session)

        # Show confirmation dialog
        if success:
            dialog_rect = pygame.Rect(0, 0, UIConfig.CONFIRM_DIALOG_WIDTH, UIConfig.CONFIRM_DIALOG_HEIGHT)
            dialog_rect.center = (self.screen_width // 2, self.screen_height // 2)
            pygame_gui.windows.UIMessageWindow(
                rect=dialog_rect,
                html_message=f"<b>Game Saved Successfully!</b><br><br>{message}",
                manager=self.ui.manager,
                window_title="Save Game"
            )
            logger.info(f"Game saved: {message}")
        else:
            dialog_rect = pygame.Rect(0, 0, UIConfig.CONFIRM_DIALOG_WIDTH, UIConfig.CONFIRM_DIALOG_HEIGHT)
            dialog_rect.center = (self.screen_width // 2, self.screen_height // 2)
            pygame_gui.windows.UIMessageWindow(
                rect=dialog_rect,
                html_message=f"<b>Save Failed</b><br><br>{message}",
                manager=self.ui.manager,
                window_title="Save Game Error"
            )
            logger.warning(f"Save failed: {message}")

    # =========================================================================
    # Pathfinding (for external access)
    # =========================================================================

    def calculate_hybrid_path(self, start_hex, end_hex) -> Any:
        """Calculate path combining local hex movement and warp jumps."""
        from game.strategy.data.pathfinding import find_hybrid_path
        return find_hybrid_path(self.galaxy, start_hex, end_hex)

    def _get_system_at_hex(self, hex_c) -> Any:
        """Find which system owns this hex."""
        from game.strategy.data.pathfinding import get_system_at_hex
        return get_system_at_hex(self.galaxy, hex_c)

    def _find_nearest_system(self, hex_c) -> Any:
        """Find the nearest system to a hex coordinate."""
        from game.strategy.data.pathfinding import find_nearest_system
        return find_nearest_system(self.galaxy, hex_c)

    # =========================================================================
    # Private Helpers
    # =========================================================================

    def _focus_on_player_home(self) -> None:
        """Focus camera on player's home colony at startup."""
        if self.active_empire.colonies:
            home_colony = self.active_empire.colonies[0]
            home_sys = next((s for s in self.systems if home_colony in s.planets), None)
            if home_sys:
                target_hex = home_sys.global_location + home_colony.location
                fx, fy = hex_to_pixel(target_hex, 10)
                self.camera.position = pygame.math.Vector2(fx, fy)

    def _load_assets(self) -> None:
        """Load visual assets using AssetManager and RaceAssetLoader."""
        from game.assets.asset_manager import get_asset_manager

        am = get_asset_manager()
        am.load_manifest()

        for emp in self.empires:
            self.empire_assets[emp.id] = self._race_loader.load_all_empire_assets(emp)

    def _get_object_asset(self, obj) -> Any:
        """Resolve the visual asset for a data object."""
        from game.assets.asset_manager import get_asset_manager
        am = get_asset_manager()

        if is_star(obj):
            if obj.image_id:
                img = am.load_star_image(obj.image_id, requested_size=512)
                if img and img != am.get_missing_texture():
                    return img
            return None

        elif is_planet(obj):
            if obj.image_id:
                try:
                    # Load planet image at 512px resolution (optimal for portraits)
                    # AssetManager handles fallback chain and caching (PROJ-54 Phase 10)
                    img = am.load_planet_image(obj.image_id, requested_size=512)
                    if img and img != am.get_missing_texture():
                        # Apply rotation for visual variety
                        if obj.image_rotation and obj.image_rotation != 0.0:
                            img = pygame.transform.rotate(img, obj.image_rotation)
                        return img
                except (FileNotFoundError, OSError, pygame.error, AttributeError) as e:
                    # Log error and fall through to None
                    logger.warning(f"Could not load planet image {obj.image_id}: {e}")
            return None  # PlanetReportPanel will create gradient placeholder

        elif is_warp_point(obj):
            return am.get_random_from_group('warp_points', 'default', seed_id=id(obj))

        elif is_fleet(obj):
            emp_assets = self.empire_assets.get(obj.owner_id)
            if emp_assets and 'fleet' in emp_assets:
                return emp_assets['fleet']

        return None
