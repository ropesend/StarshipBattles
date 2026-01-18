"""
StrategyScene - Main coordinator for strategy layer.

This is the central hub that manages the strategy game state and delegates
to specialized modules for rendering, input handling, and game operations.

Refactored from 1,568 lines to ~350 lines by extracting:
- StrategyRenderer: All drawing logic (~580 lines)
- InputHandler: Event and click routing (~180 lines)
- CameraNavigator: Camera focus and zoom (~90 lines)
- FleetOperations: Fleet movement commands (~130 lines)
- ColonizationSystem: Colonization workflow (~175 lines)
"""
import os
import pygame
from game.core.config import UIConfig
from game.core.logger import log_debug, log_info, log_warning
from game.strategy.data.galaxy import StarSystem
from game.strategy.data.fleet import Fleet
from game.strategy.data.hex_math import hex_to_pixel
from game.ui.renderer.camera import Camera
from game.ui.screens.strategy_screen import StrategyInterface

# Extracted modules
from game.ui.screens.strategy_renderer import StrategyRenderer
from game.ui.screens.strategy_camera_nav import CameraNavigator
from game.ui.screens.strategy_fleet_ops import FleetOperations
from game.ui.screens.strategy_colonization import ColonizationSystem
from game.ui.screens.strategy_input_handler import InputHandler


class StrategyScene:
    """Manages strategy layer simulation, rendering, and UI."""

    TOP_BAR_HEIGHT = 50

    def __init__(self, screen_width, screen_height, session=None):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Session Management
        if session:
            self.session = session
        else:
            from game.strategy.engine.game_session import GameSession
            self.session = GameSession()

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
        self.ui = StrategyInterface(self, screen_width, screen_height)

        # State
        self.hover_hex = None
        self.HEX_SIZE = 10
        self.DETAIL_ZOOM_LEVEL = 3.0

        self.selected_fleet = None
        self.selected_object = None
        self.last_selected_system = None

        self.turn_processing = False
        self.action_open_design = False
        self.current_player_index = 0

        # Assets
        self.empire_assets = {}
        self._load_assets()

        # Initialize sub-modules
        self._renderer = StrategyRenderer(self)
        self._camera_nav = CameraNavigator(self)
        self._fleet_ops = FleetOperations(self)
        self._colonization = ColonizationSystem(self)
        self._input = InputHandler(self)

    # =========================================================================
    # Properties (delegate to session)
    # =========================================================================

    @property
    def galaxy(self):
        return self.session.galaxy

    @property
    def empires(self):
        return self.session.empires

    @property
    def systems(self):
        return self.session.systems

    @property
    def turn_engine(self):
        return self.session.turn_engine

    @property
    def player_empire(self):
        return self.session.player_empire

    @property
    def enemy_empire(self):
        return self.session.enemy_empire

    @property
    def human_player_ids(self):
        return self.session.human_player_ids

    @property
    def current_empire(self):
        """Get the empire for the current player (supports N players)."""
        current_player_id = self.human_player_ids[self.current_player_index]
        return next((e for e in self.empires if e.id == current_player_id), self.empires[0])

    @property
    def input_mode(self):
        return self._input.input_mode

    @input_mode.setter
    def input_mode(self, value):
        self._input.input_mode = value

    # =========================================================================
    # Lifecycle Methods
    # =========================================================================

    def update(self, dt):
        """Update scene state."""
        self.camera.update(dt)
        self.ui.update(dt)

        # Update build queue screen if open
        if hasattr(self, 'build_queue_screen') and self.build_queue_screen is not None:
            self.build_queue_screen.update(dt)

    def draw(self, screen):
        """Render the scene."""
        self._renderer.draw(screen)

        if self.turn_processing:
            self._renderer.draw_processing_overlay(screen)

        self.ui.draw(screen)

        # Draw build queue screen if open (overlay on top)
        if hasattr(self, 'build_queue_screen') and self.build_queue_screen is not None:
            self.build_queue_screen.draw(screen)

    def handle_resize(self, width, height):
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

    def handle_event(self, event):
        """Process pygame events."""
        self._input.handle_event(event)

    def handle_click(self, mx, my, button):
        """Handle mouse clicks."""
        return self._input.handle_click(mx, my, button)

    def update_input(self, dt, events):
        """Update input state."""
        self._input.update_input(dt, events)

    # =========================================================================
    # Navigation (delegates to CameraNavigator)
    # =========================================================================

    def center_camera_on(self, obj):
        """Center camera on a game object."""
        self._camera_nav.center_on(obj)

    def cycle_selection(self, obj_type, direction):
        """Cycle selection through colonies or fleets."""
        new_obj = self._camera_nav.cycle_selection(obj_type, direction)
        if new_obj:
            self.on_ui_selection(new_obj)
            self.center_camera_on(new_obj)

    # =========================================================================
    # Colonization (delegates to ColonizationSystem)
    # =========================================================================

    def on_colonize_click(self):
        """Handle colonize action."""
        result = self._colonization.on_colonize_click(self.selected_fleet)
        if result and result.get('type') == 'prompt':
            self.ui.prompt_planet_selection(
                result['planets'],
                lambda p: self._on_colonize_planet_selected(p)
            )
        elif result and result.get('type') == 'success':
            self.on_ui_selection(self.selected_fleet)

    def _on_colonize_planet_selected(self, planet):
        """Handle planet selection from colonize prompt."""
        result = self._colonization.issue_colonize_order(self.selected_fleet, planet)
        if result and result.get('type') == 'success':
            self.on_ui_selection(self.selected_fleet)

    def request_colonize_order(self, fleet, planet=None):
        """Handle colonize request from UI."""
        self.selected_fleet = fleet
        result = self._colonization.request_colonize_order(fleet, planet)
        if result and result.get('type') == 'success':
            self.on_ui_selection(fleet)

    # =========================================================================
    # Turn Management
    # =========================================================================

    def advance_turn(self):
        """End current player's order phase. Process turn when all humans ready."""
        self.current_player_index += 1

        if self.current_player_index >= len(self.human_player_ids):
            # All humans ready - process the full turn
            self.current_player_index = 0
            self._process_full_turn()
            self._update_player_label()
        else:
            # Switch to next human player's view
            next_player_id = self.human_player_ids[self.current_player_index]
            log_info(f"Player {next_player_id + 1}'s turn to give orders.")
            self._update_player_label()
            # Center on their home colony
            next_empire = next((e for e in self.empires if e.id == next_player_id), None)
            if next_empire and next_empire.colonies:
                self.center_camera_on(next_empire.colonies[0])

    def _process_full_turn(self):
        """Process the turn for all empires simultaneously."""
        self.turn_processing = True
        log_info("Processing Turn...")

        # Force Render "Processing" state
        screen = pygame.display.get_surface()
        if screen:
            self.draw(screen)
            pygame.display.flip()

        # Process turn for all empires
        self.session.process_turn()

        # Re-center Camera on current player's home
        current_player_id = self.human_player_ids[self.current_player_index]
        current_empire = next((e for e in self.empires if e.id == current_player_id), self.player_empire)
        if current_empire.colonies:
            self.center_camera_on(current_empire.colonies[0])

        self.turn_processing = False

        # Refresh UI for currently selected object
        if self.selected_object:
            self.on_ui_selection(self.selected_object)

    def _update_player_label(self):
        """Update the player indicator label."""
        player_num = self.current_player_index + 1
        self.ui.lbl_current_player.set_text(f"Player {player_num}'s Turn")

    # =========================================================================
    # Selection
    # =========================================================================

    def on_ui_selection(self, obj):
        """Called when user selects an item in the UI list."""
        self.selected_object = obj

        # Track last selected system
        if isinstance(obj, StarSystem):
            self.last_selected_system = obj
        elif hasattr(obj, 'location'):
            parent_sys = next((s for s in self.systems if obj in s.planets or obj in s.warp_points), None)
            if parent_sys:
                self.last_selected_system = parent_sys

        # Update fleet selection
        current_player_id = self.human_player_ids[self.current_player_index]
        if isinstance(obj, Fleet) and obj.owner_id == current_player_id:
            self.selected_fleet = obj
        else:
            if not isinstance(obj, Fleet):
                self.selected_fleet = None

        # Update UI
        img = self._get_object_asset(obj)
        self.ui.show_detailed_report(obj, img)

    # =========================================================================
    # Actions
    # =========================================================================

    def on_build_yard_click(self):
        """Open build queue screen for selected planet."""
        from game.strategy.data.planet import Planet
        if isinstance(self.selected_object, Planet):
            planet = self.selected_object
            if planet.owner_id == self.current_empire.id:
                from game.ui.screens.build_queue_screen import BuildQueueScreen

                # Create screen
                self.build_queue_screen = BuildQueueScreen(
                    self.ui.manager,
                    planet,
                    self.session,
                    on_close_callback=self._on_build_queue_close
                )
                log_info(f"Opened build queue for {planet.name}")

    def _on_build_queue_close(self):
        """Handle build queue screen closing."""
        self.build_queue_screen = None
        # Refresh planet details to show updated queue/facilities
        if self.selected_object:
            img = self._get_object_asset(self.selected_object)
            self.ui.show_detailed_report(self.selected_object, img)

    def on_design_click(self):
        """Handle 'Design' button click - opens Design Workshop."""
        log_debug("Design button clicked - opening Design Workshop")

        # Gather context data for integrated mode
        self.workshop_context_data = {
            'empire': self.session.player_empire if hasattr(self, 'session') else None,
            'game_session': self.session if hasattr(self, 'session') else None
        }
        self.action_open_design = True

    def on_save_game_click(self):
        """Handle 'Save Game' button click."""
        from game.strategy.systems.save_game_service import SaveGameService
        import pygame_gui.windows

        log_info("Saving game...")

        # Save the game
        success, message, save_path = SaveGameService.save_game(self.session)

        # Show confirmation dialog
        if success:
            dialog_rect = pygame.Rect(0, 0, 400, 200)
            dialog_rect.center = (self.screen_width // 2, self.screen_height // 2)
            pygame_gui.windows.UIMessageWindow(
                rect=dialog_rect,
                html_message=f"<b>Game Saved Successfully!</b><br><br>{message}",
                manager=self.ui.manager,
                window_title="Save Game"
            )
            log_info(f"Game saved: {message}")
        else:
            dialog_rect = pygame.Rect(0, 0, 400, 200)
            dialog_rect.center = (self.screen_width // 2, self.screen_height // 2)
            pygame_gui.windows.UIMessageWindow(
                rect=dialog_rect,
                html_message=f"<b>Save Failed</b><br><br>{message}",
                manager=self.ui.manager,
                window_title="Save Game Error"
            )
            log_warning(f"Save failed: {message}")

    # =========================================================================
    # Pathfinding (for external access)
    # =========================================================================

    def calculate_hybrid_path(self, start_hex, end_hex):
        """Calculate path combining local hex movement and warp jumps."""
        from game.strategy.data.pathfinding import find_hybrid_path
        return find_hybrid_path(self.galaxy, start_hex, end_hex)

    def _get_system_at_hex(self, hex_c):
        """Find which system owns this hex."""
        from game.strategy.data.pathfinding import get_system_at_hex
        return get_system_at_hex(self.galaxy, hex_c)

    def _find_nearest_system(self, hex_c):
        """Find the nearest system to a hex coordinate."""
        from game.strategy.data.pathfinding import find_nearest_system
        return find_nearest_system(self.galaxy, hex_c)

    # =========================================================================
    # Private Helpers
    # =========================================================================

    def _focus_on_player_home(self):
        """Focus camera on player's home colony at startup."""
        if self.player_empire.colonies:
            home_colony = self.player_empire.colonies[0]
            home_sys = next((s for s in self.systems if home_colony in s.planets), None)
            if home_sys:
                target_hex = home_sys.global_location + home_colony.location
                fx, fy = hex_to_pixel(target_hex, 10)
                self.camera.position = pygame.math.Vector2(fx, fy)

    def _load_assets(self):
        """Load visual assets using AssetManager."""
        from game.assets.asset_manager import get_asset_manager

        am = get_asset_manager()
        am.load_manifest()

        for emp in self.empires:
            self.empire_assets[emp.id] = {}
            if emp.theme_path and os.path.exists(emp.theme_path):
                # Colony Flag
                colony_path = os.path.join(emp.theme_path, "Flags", "Colony_Flag.jpg")
                if os.path.exists(colony_path):
                    self.empire_assets[emp.id]['colony'] = am.load_external_image(colony_path)

                # Fleet Icon
                fleet_path = os.path.join(emp.theme_path, "Skins", "Battlecruiser.png")
                if os.path.exists(fleet_path):
                    self.empire_assets[emp.id]['fleet'] = am.load_external_image(fleet_path)

    def _get_object_asset(self, obj):
        """Resolve the visual asset for a data object."""
        from game.assets.asset_manager import get_asset_manager
        am = get_asset_manager()

        if hasattr(obj, 'color') and hasattr(obj, 'mass'):  # Star
            color = obj.color
            asset_key = 'yellow'
            if color[0] > 200 and color[1] < 100:
                asset_key = 'red'
            elif color[2] > 200 and color[0] < 100:
                asset_key = 'blue'
            elif color[0] > 200 and color[1] > 200 and color[2] > 200:
                asset_key = 'white'
            elif color[0] > 200 and color[1] > 150:
                asset_key = 'orange'
            return am.get_image('stars', asset_key)

        elif hasattr(obj, 'planet_type'):
            p_type_name = obj.planet_type.name.lower()
            cat = 'terran'
            if 'gas' in p_type_name:
                cat = 'gas'
            elif 'ice' in p_type_name:
                cat = 'ice'
            elif 'desert' in p_type_name or 'hot' in p_type_name:
                cat = 'venus'
            return am.get_random_from_group('planets', cat, seed_id=id(obj))

        elif hasattr(obj, 'destination_id'):  # Warp Point
            return am.get_random_from_group('warp_points', 'default', seed_id=id(obj))

        elif hasattr(obj, 'ships'):  # Fleet
            emp_assets = self.empire_assets.get(obj.owner_id)
            if emp_assets and 'fleet' in emp_assets:
                return emp_assets['fleet']

        return None
