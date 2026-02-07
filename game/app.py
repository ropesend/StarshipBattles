"""Main game entry point - coordinates scenes and game loop."""
import argparse
import pygame
import pygame_gui
import os

from game.core.logger import log_debug, log_info, log_error
from game.core.config import DisplayConfig
from game.core.paths import Paths
from game.ui.utils import create_centered_rect

# Parse command line arguments
parser = argparse.ArgumentParser(description="Starship Battles")
parser.add_argument('--force-resolution', action='store_true',
                    help='Force 2560x1600 resolution regardless of monitor size')
args, _ = parser.parse_known_args()

from game.simulation.components.component import load_components, load_modifiers
from game.core.resources import load_resources
from game.core.registry import GameRegistries, set_default_registries, RegistryManager
from pygame_gui.elements import UIButton
from game.ui.screens.workshop_screen import DesignWorkshopScreen
from game.ui.screens.workshop_context import WorkshopContext
from game.ui.renderer.sprites import SpriteManager
from game.ui.screens.battle_screen import BattleScreen
from game.ui.screens.setup_screen import BattleSetupScreen
from game.ui.screens.strategy_screen import StrategyScreen
from game.ui.screens.new_game_setup_screen import NewGameSetupScreen
from Tools.formation_editor import FormationEditorScreen
from game.ui.screens.test_lab import TestLabScreen
from game.ui.screens.galaxy_test import GalaxyTestScreen
from game.core.profiling import PROFILER, profile_action
from game.battle_coordinator import (
    update_battle_headless, update_battle_visual,
    draw_battle_hud, update_tick_rate
)
from game.exit_dialog import (
    draw_exit_dialog, handle_exit_dialog_click, handle_exit_dialog_cancel
)

# Constants
DEFAULT_WIDTH, DEFAULT_HEIGHT = DisplayConfig.default_resolution()
WIDTH, HEIGHT = DEFAULT_WIDTH, DEFAULT_HEIGHT
FPS = 60
BG_COLOR = (10, 10, 20)

# Scene States
from game.core.constants import GameState
from game.ui.screens.battle_input_handler import BattleInputHandler


# Initialize fonts
pygame.font.init()
font_small = pygame.font.SysFont("arial", 12)
font_med = pygame.font.SysFont("arial", 20)
font_large = pygame.font.SysFont("arial", 32)


class Game:
    """Main game class coordinating scenes and game loop."""

    def __init__(self):
        pygame.init()

        # Monitor detection and resolution setup
        info = pygame.display.Info()
        monitor_w = info.current_w
        monitor_h = info.current_h

        global WIDTH, HEIGHT

        if args.force_resolution:
            WIDTH, HEIGHT = DisplayConfig.default_resolution()
        elif monitor_w >= 3840 and monitor_h >= 2160:
            WIDTH, HEIGHT = 3840, 2160
        elif monitor_w >= 2560 and monitor_h >= 1600:
            WIDTH, HEIGHT = 2560, 1600
        else:
            WIDTH, HEIGHT = int(monitor_w * 0.9), int(monitor_h * 0.9)

        if not pygame.display.get_surface():
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        else:
            self.screen = pygame.display.get_surface()

        pygame.display.set_caption(f"Starship Battles ({WIDTH}x{HEIGHT})")

        # pygame_gui UIManager for main menu buttons
        self.menu_ui_manager = pygame_gui.UIManager((WIDTH, HEIGHT))
        self._menu_button_callbacks = {}  # Maps UIButton -> callback function

        self.clock = pygame.time.Clock()
        self.running = True
        self.show_exit_dialog = False
        self.showing_load_menu = False
        self.showing_race_setup = False
        self.race_setup_window = None
        self.state = GameState.MENU

        # Load game data
        load_components(Paths.COMPONENTS_FILE)
        load_modifiers(Paths.MODIFIERS_FILE)
        load_resources(Paths.RESOURCES_FILE)

        # Initialize ship data
        from game.simulation.entities.ship_loader import initialize_ship_data
        initialize_ship_data(Paths.ROOT_DIR)

        # Create GameRegistries container for DI (PROJ-38)
        registry = RegistryManager.instance()
        self.registries = GameRegistries(
            components=registry.components,
            modifiers=registry.modifiers,
            vehicle_classes=registry.vehicle_classes,
            resources=registry.resources
        )
        set_default_registries(self.registries)

        # Load sprites
        sprite_mgr = SpriteManager.instance()
        sprite_mgr.load_sprites(Paths.ROOT_DIR)

        # Menu UI
        self.update_menu_buttons()

        # Scene objects
        context = WorkshopContext.standalone(tech_preset_name="default")
        context.on_return = self.on_builder_return
        self.builder_scene = DesignWorkshopScreen(WIDTH, HEIGHT, context)
        self.battle_setup = BattleSetupScreen()
        self.battle_scene = BattleScreen(WIDTH, HEIGHT)
        self.strategy_scene = StrategyScreen(WIDTH, HEIGHT)
        self.formation_scene = FormationEditorScreen(WIDTH, HEIGHT, self.on_formation_return)
        self.test_lab_scene = TestLabScreen(self)

    def update_menu_buttons(self):
        # Clear old buttons if they exist
        for btn in getattr(self, 'menu_buttons', []):
            btn.kill()
        self._menu_button_callbacks.clear()

        self.menu_buttons = []
        button_data = [
            ("Quickstart 1P", self.start_quickstart_1p),
            ("Quickstart 2P", self.start_quickstart_2p),
            ("New Game", self.start_strategy_layer),
            ("Load Game", self.show_load_menu),
            ("Race Setup", self.start_race_setup),
            ("Design Workshop", self.start_builder),
            ("Battle Setup", self.start_battle_setup),
            ("Formation Editor", self.start_formation_editor),
            ("Combat Lab", self.start_test_lab),
            ("Research Tree", self.start_research_tree),
            ("Galaxy Test", self.start_galaxy_test),
        ]

        for i, (text, callback) in enumerate(button_data):
            btn = UIButton(
                relative_rect=pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 320 + i * 70, 200, 50),
                text=text,
                manager=self.menu_ui_manager
            )
            self.menu_buttons.append(btn)
            self._menu_button_callbacks[btn] = callback

    @profile_action("App: Start Builder")
    def start_builder(self, return_to=None, context=None):
        """
        Enter design workshop.

        Args:
            return_to: State to return to (MENU or STRATEGY)
            context: Optional WorkshopContext for integrated mode
        """
        self.state = GameState.BUILDER
        self.builder_return_state = return_to
        # Use provided context or create default standalone context
        if context is None:
            context = WorkshopContext.standalone(tech_preset_name="default")
        context.on_return = self.on_builder_return
        self.builder_scene = DesignWorkshopScreen(WIDTH, HEIGHT, context)

    def on_builder_return(self, custom_ship=None):
        """Return from design workshop to caller or main menu."""
        # Clean up workshop UI elements before switching state
        if hasattr(self, 'builder_scene') and hasattr(self.builder_scene, 'cleanup'):
            self.builder_scene.cleanup()

        if self.builder_return_state == GameState.STRATEGY:
            self.state = GameState.STRATEGY
            if hasattr(self.strategy_scene, 'handle_resize'):
                self.strategy_scene.handle_resize(WIDTH, HEIGHT)
        else:
            self.state = GameState.MENU
        self.builder_return_state = None

    @profile_action("App: Start Battle Setup")
    def start_battle_setup(self, preserve_teams=False):
        """Enter battle setup screen."""
        self.state = GameState.BATTLE_SETUP
        self.return_state = GameState.BATTLE_SETUP
        self.battle_setup.start(preserve_teams=preserve_teams)

    def start_strategy_layer(self):
        """Show new game setup screen."""
        import pygame_gui

        log_info("Opening new game setup")

        # Create UI manager if needed
        if not hasattr(self, 'menu_ui_manager'):
            self.menu_ui_manager = pygame_gui.UIManager((WIDTH, HEIGHT))

        # Create new game setup window (expanded for race selection UI)
        window_rect = create_centered_rect(650, 600, WIDTH, HEIGHT)

        self.new_game_setup_window = NewGameSetupScreen(
            window_rect,
            self.menu_ui_manager,
            on_start_callback=self._on_new_game_start,
            on_cancel_callback=self._on_new_game_cancel
        )

        # Set flag to render window
        self.showing_new_game_setup = True

    def _on_new_game_start(self, config):
        """Handle new game start from setup screen."""
        from game.strategy.engine.game_session import GameSession
        from game.strategy.systems.save_game_service import SaveGameService

        log_info(f"Starting new game: {config.save_name} with {len(config.players)} players")

        # Create game session
        session = GameSession(config=config)

        # Save initial state
        success, message, save_path = SaveGameService.save_game(session, config.save_name)

        if success:
            session.save_path = save_path
            log_info(f"Initial save created: {save_path}")

            # Create strategy scene with new session
            self.strategy_scene = StrategyScreen(WIDTH, HEIGHT, session=session)
            self.state = GameState.STRATEGY
            self.showing_new_game_setup = False
        else:
            log_error(f"Failed to create initial save: {message}")
            # Show error dialog
            import pygame_gui.windows
            error_rect = pygame.Rect(0, 0, 400, 200)
            error_rect.center = (WIDTH // 2, HEIGHT // 2)
            pygame_gui.windows.UIMessageWindow(
                rect=error_rect,
                html_message=f"<b>Save Failed</b><br><br>{message}",
                manager=self.menu_ui_manager,
                window_title="Error"
            )

    def _on_new_game_cancel(self):
        """Cancel new game setup."""
        self.showing_new_game_setup = False
        log_debug("New game setup cancelled")

    def _start_quickstart(self, player_count: int):
        """
        Start a quickstart game with the specified number of players.

        Args:
            player_count: Number of players (1 or 2)
        """
        from game.strategy.quickstart_builder import QuickstartBuilder
        from game.strategy.engine.game_session import GameSession
        from game.strategy.systems.save_game_service import SaveGameService

        log_info(f"Starting Quickstart {player_count}P")

        # Build config based on player count
        if player_count == 1:
            config = QuickstartBuilder.build_1p_config()
            empire_ids = [0]
        else:
            config = QuickstartBuilder.build_2p_config()
            empire_ids = [0, 1]

        session = GameSession(config=config)

        success, message, save_path = SaveGameService.save_game(session, config.save_name)

        if success:
            session.save_path = save_path
            log_info(f"Quickstart {player_count}P save created: {save_path}")

            # Copy quickstart designs for empires
            QuickstartBuilder.copy_quickstart_designs(save_path, empire_ids)

            self.strategy_scene = StrategyScreen(WIDTH, HEIGHT, session=session)
            self.state = GameState.STRATEGY
        else:
            log_error(f"Quickstart {player_count}P failed: {message}")

    def start_quickstart_1p(self):
        """Start a single-player quickstart game."""
        self._start_quickstart(player_count=1)

    def start_quickstart_2p(self):
        """Start a two-player quickstart game."""
        self._start_quickstart(player_count=2)

    def show_load_menu(self):
        """Show load game menu."""
        from game.ui.screens.save_selection_window import SaveSelectionWindow
        import pygame_gui

        log_info("Opening load game menu")

        # Create UI manager if needed
        if not hasattr(self, 'menu_ui_manager'):
            self.menu_ui_manager = pygame_gui.UIManager((WIDTH, HEIGHT))

        # Create save selection window
        window_rect = create_centered_rect(600, 500, WIDTH, HEIGHT)

        self.save_selection_window = SaveSelectionWindow(
            window_rect,
            self.menu_ui_manager,
            on_load_callback=self._on_load_game,
            on_cancel_callback=self._on_load_cancel
        )

        # Set flag to render window
        self.showing_load_menu = True

    def _on_load_game(self, save_path, turn_number=None):
        """Load the selected save game."""
        from game.strategy.systems.save_game_service import SaveGameService

        log_info(f"Loading game from: {save_path}, turn: {turn_number}")

        # Load game session (optionally at specific turn)
        game_session, message = SaveGameService.load_game(save_path, turn_number=turn_number)

        if game_session:
            # Create new strategy scene with loaded session
            self.strategy_scene = StrategyScreen(WIDTH, HEIGHT, session=game_session)
            self.state = GameState.STRATEGY
            self.showing_load_menu = False
            log_info(f"Game loaded successfully: {message}")
        else:
            log_error(f"Failed to load game: {message}")
            # Show error dialog
            import pygame_gui.windows
            error_rect = pygame.Rect(0, 0, 400, 200)
            error_rect.center = (WIDTH // 2, HEIGHT // 2)
            pygame_gui.windows.UIMessageWindow(
                rect=error_rect,
                html_message=f"<b>Load Failed</b><br><br>{message}",
                manager=self.menu_ui_manager,
                window_title="Error"
            )

    def _on_load_cancel(self):
        """Cancel load game."""
        self.showing_load_menu = False
        log_debug("Load game cancelled")

    @profile_action("App: Start Formation Editor")
    def start_formation_editor(self):
        """Enter formation editor."""
        self.state = GameState.FORMATION
        self.formation_scene.handle_resize(WIDTH, HEIGHT)

    def on_formation_return(self):
        """Return from formation editor."""
        self.state = GameState.MENU

    def start_test_lab(self):
        """Enter Combat Lab."""
        self.state = GameState.TEST_LAB
        self.return_state = GameState.TEST_LAB

    def start_research_tree(self):
        """Enter Research Tree sandbox."""
        from game.research.ui.research_scene import ResearchTreeScene

        log_info("Starting Research Tree sandbox")
        self.state = GameState.RESEARCH_TREE
        self.research_tree_scene = ResearchTreeScene(
            WIDTH, HEIGHT,
            on_close_callback=self.on_research_tree_return
        )

    def on_research_tree_return(self):
        """Return from Research Tree to menu."""
        self.state = GameState.MENU
        self.research_tree_scene = None

    def start_galaxy_test(self):
        """Enter Galaxy Test screen."""
        log_info("Starting Galaxy Test screen")
        self.state = GameState.GALAXY_TEST
        self.galaxy_test_scene = GalaxyTestScreen(
            WIDTH, HEIGHT,
            on_close_callback=self.on_galaxy_test_return
        )

    def on_galaxy_test_return(self):
        """Return from Galaxy Test to menu."""
        self.state = GameState.MENU
        self.galaxy_test_scene = None

    def start_race_setup(self):
        """Open race setup wizard."""
        import pygame_gui

        log_info("Opening race setup wizard")

        # Create UI manager if needed
        if not hasattr(self, 'menu_ui_manager'):
            self.menu_ui_manager = pygame_gui.UIManager((WIDTH, HEIGHT))

        # Create race setup window (larger for 2560x1600 displays)
        window_rect = create_centered_rect(1800, 1200, WIDTH, HEIGHT)

        # Import here to avoid circular imports
        from game.ui.screens.race_setup_screen import RaceSetupScreen

        self.race_setup_window = RaceSetupScreen(
            window_rect,
            self.menu_ui_manager,
            on_complete_callback=self._on_race_setup_complete,
            on_cancel_callback=self._on_race_setup_cancel
        )

        self.showing_race_setup = True

    def _on_race_setup_complete(self, race_config):
        """Handle race setup completion."""
        log_info(f"Race setup complete: {race_config.name}")
        self.showing_race_setup = False
        self.race_setup_window = None

    def _on_race_setup_cancel(self):
        """Cancel race setup."""
        self.showing_race_setup = False
        self.race_setup_window = None
        log_debug("Race setup cancelled")

    def start_battle(self, team1_ships, team2_ships, headless=False):
        """Start a battle with the given ships."""
        self.state = GameState.BATTLE
        if self.battle_scene.screen_width != WIDTH or self.battle_scene.screen_height != HEIGHT:
            self.battle_scene.handle_resize(WIDTH, HEIGHT)
        self.battle_scene.start(team1_ships, team2_ships, headless=headless)

    def run(self):
        """Main game loop."""
        while self.running:
            frame_time = self.clock.tick(0) / 1000.0
            if frame_time > 0.1:
                frame_time = 0.1

            events = pygame.event.get()

            if self.show_exit_dialog:
                self._handle_exit_dialog_events(events)
            else:
                self._handle_normal_events(events)

            self._update_and_draw(frame_time, events)
            pygame.display.flip()

        pygame.quit()

    def _handle_exit_dialog_events(self, events):
        """Handle events when exit dialog is shown."""
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.show_exit_dialog = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if handle_exit_dialog_click(event.pos):
                    self.running = False
                elif handle_exit_dialog_cancel(event.pos):
                    self.show_exit_dialog = False

    def _handle_normal_events(self, events):
        """Handle events during normal gameplay."""
        for event in events:
            state_before = self.state

            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_x and (event.mod & pygame.KMOD_ALT):
                self.show_exit_dialog = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F9:
                active = PROFILER.toggle()
                log_info(f"Profiling {'ENABLED' if active else 'DISABLED'}")
            elif event.type == pygame.VIDEORESIZE:
                self._handle_resize(event.w, event.h)
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_click(event)
            elif event.type == pygame.MOUSEWHEEL:
                self._handle_scroll(event)

            # Forward events to current scene only if state didn't change
            if self.state != state_before:
                log_debug(f"State changed from {state_before} to {self.state}")
                continue

            self._forward_event_to_scene(event)

    def _forward_event_to_scene(self, event):
        """Forward event to the current active scene."""
        # Handle new game setup if showing
        if hasattr(self, 'showing_new_game_setup') and self.showing_new_game_setup and hasattr(self, 'menu_ui_manager'):
            self.menu_ui_manager.process_events(event)
            return

        # Handle load menu if showing
        if self.showing_load_menu and hasattr(self, 'menu_ui_manager'):
            self.menu_ui_manager.process_events(event)
            return

        # Handle race setup if showing
        if self.showing_race_setup and hasattr(self, 'menu_ui_manager'):
            self.menu_ui_manager.process_events(event)
            return

        if self.state == GameState.MENU:
            self.menu_ui_manager.process_events(event)
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                callback = self._menu_button_callbacks.get(event.ui_element)
                if callback:
                    callback()
                    return  # Event consumed
        elif self.state == GameState.BUILDER:
            self.builder_scene.handle_event(event)
        elif self.state == GameState.BATTLE_SETUP:
            self.battle_setup.update([event], self.screen.get_size())
        elif self.state == GameState.FORMATION:
            self.formation_scene.handle_event(event)
        elif self.state == GameState.STRATEGY:
            self.strategy_scene.handle_event(event)
        elif self.state == GameState.TEST_LAB:
            self.test_lab_scene.handle_input([event])
        elif self.state == GameState.RESEARCH_TREE:
            if hasattr(self, 'research_tree_scene') and self.research_tree_scene:
                self.research_tree_scene.handle_event(event)
        elif self.state == GameState.GALAXY_TEST:
            if hasattr(self, 'galaxy_test_scene') and self.galaxy_test_scene:
                self.galaxy_test_scene.handle_event(event)

    def _handle_resize(self, w, h):
        """Handle window resize."""
        global WIDTH, HEIGHT
        WIDTH, HEIGHT = w, h
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

        # Update menu UIManager resolution
        self.menu_ui_manager.set_window_resolution((WIDTH, HEIGHT))

        if self.state == GameState.MENU:
            self.update_menu_buttons()
        elif self.state == GameState.BATTLE:
            self.battle_scene.handle_resize(w, h)
        elif self.state == GameState.BUILDER:
            if hasattr(self.builder_scene, 'handle_resize'):
                self.builder_scene.handle_resize(w, h)
        elif self.state == GameState.FORMATION:
            self.formation_scene.handle_resize(w, h)
        elif self.state == GameState.TEST_LAB:
            self.test_lab_scene._create_ui()
        elif self.state == GameState.STRATEGY:
            self.strategy_scene.handle_resize(w, h)
        elif self.state == GameState.RESEARCH_TREE:
            if hasattr(self, 'research_tree_scene') and self.research_tree_scene:
                self.research_tree_scene.handle_resize(w, h)
        elif self.state == GameState.GALAXY_TEST:
            if hasattr(self, 'galaxy_test_scene') and self.galaxy_test_scene:
                self.galaxy_test_scene.handle_resize(w, h)

    def _handle_keydown(self, event):
        """Handle key press events."""
        BattleInputHandler.handle_keydown(self, event)

    def _handle_click(self, event):
        """Handle mouse click events."""
        mx, my = event.pos

        if self.state == GameState.BATTLE:
            if self.battle_scene.handle_click(mx, my, event.button, self.screen.get_size()):
                self._handle_battle_actions()
        elif self.state == GameState.STRATEGY:
            self.strategy_scene.handle_click(mx, my, event.button)

    def _handle_battle_actions(self):
        """Handle action flags from battle scene."""
        if self.battle_scene.action_return_to_test_lab:
            log_debug("Returning to Combat Lab from test")
            self.battle_scene.action_return_to_test_lab = False
            self.battle_scene.test_mode = False
            self.test_lab_scene.reset_selection()
            self.start_test_lab()
        elif self.battle_scene.action_return_to_setup:
            log_debug("Returning to battle setup")
            self.battle_scene.action_return_to_setup = False
            if hasattr(self, 'return_state') and self.return_state == GameState.TEST_LAB:
                self.start_test_lab()
            else:
                self.start_battle_setup(preserve_teams=True)

    def _handle_scroll(self, event):
        """Handle mouse wheel events."""
        if self.state == GameState.BATTLE:
            mx, my = pygame.mouse.get_pos()
            sw = self.screen.get_size()[0]
            if mx >= sw - self.battle_scene.stats_panel_width or mx < self.battle_scene.ui.seeker_panel.rect.width:
                self.battle_scene.handle_scroll(event.y, self.screen.get_size()[1])
        elif self.state == GameState.STRATEGY and hasattr(self.strategy_scene, 'handle_scroll'):
            self.strategy_scene.handle_scroll(event.y, self.screen.get_size()[1])

    def _update_and_draw(self, frame_time, events):
        """Update logic and draw current scene."""
        if self.state == GameState.MENU:
            self._draw_menu()
        elif self.state == GameState.BUILDER:
            self.builder_scene.update(frame_time)
            self.builder_scene.draw(self.screen)
        elif self.state == GameState.BATTLE_SETUP:
            self._update_battle_setup()
        elif self.state == GameState.BATTLE:
            self._update_battle(frame_time, events)
        elif self.state == GameState.FORMATION:
            self.formation_scene.update(frame_time)
            self.formation_scene.draw(self.screen)
        elif self.state == GameState.STRATEGY:
            self.strategy_scene.update_input(frame_time, events)
            self.strategy_scene.update(frame_time)
            self.strategy_scene.draw(self.screen)
            if self.strategy_scene.action_open_design:
                self.strategy_scene.action_open_design = False

                # Create integrated context if launching from strategy
                context = None
                if hasattr(self.strategy_scene, 'workshop_context_data') and self.strategy_scene.workshop_context_data:
                    data = self.strategy_scene.workshop_context_data
                    empire = data.get('empire')
                    game_session = data.get('game_session')

                    if empire and game_session:
                        # Import here to avoid circular imports
                        from game.ui.screens.workshop_context import WorkshopContext

                        # Get empire tech (placeholder for now - will be implemented when tech tree exists)
                        available_tech_ids = []  # TODO: Replace with empire.available_tech or similar

                        # Get savegame path (may be None for new games - that's OK!)
                        savegame_path = game_session.save_path if hasattr(game_session, 'save_path') else None

                        # Get empire theme
                        empire_theme_id = empire.empire_theme_id if hasattr(empire, 'empire_theme_id') else None
                        log_debug(f"Creating WorkshopContext with empire_theme_id={empire_theme_id}")

                        # Create integrated context regardless of save_path
                        # If save_path is None, designs will use temp storage or in-memory
                        context = WorkshopContext.integrated(
                            empire_id=empire.id,
                            savegame_path=savegame_path,  # Can be None
                            available_tech_ids=available_tech_ids,
                            built_designs=empire.built_ship_designs if hasattr(empire, 'built_ship_designs') else set(),
                            empire_theme_id=empire_theme_id
                        )

                    # Clean up context data
                    self.strategy_scene.workshop_context_data = None

                self.start_builder(return_to=GameState.STRATEGY, context=context)
        elif self.state == GameState.TEST_LAB:
            self.test_lab_scene.update()
            self.test_lab_scene.draw(self.screen)
        elif self.state == GameState.RESEARCH_TREE:
            if hasattr(self, 'research_tree_scene') and self.research_tree_scene:
                self.research_tree_scene.handle_input(frame_time, events)
                self.research_tree_scene.update(frame_time)
                self.research_tree_scene.draw(self.screen)
        elif self.state == GameState.GALAXY_TEST:
            if hasattr(self, 'galaxy_test_scene') and self.galaxy_test_scene:
                self.galaxy_test_scene.handle_input(frame_time, events)
                self.galaxy_test_scene.update(frame_time)
                self.galaxy_test_scene.draw(self.screen)

        if self.show_exit_dialog:
            draw_exit_dialog(self.screen, font_large, font_med)

    def _draw_menu(self):
        """Draw main menu."""
        self.screen.fill((20, 20, 30))

        # Update and draw pygame_gui elements (menu buttons and dialogs)
        frame_time = self.clock.get_time() / 1000.0
        self.menu_ui_manager.update(frame_time)
        self.menu_ui_manager.draw_ui(self.screen)

    def _update_battle_setup(self):
        """Update and draw battle setup, handle actions."""
        self.battle_setup.draw(self.screen)

        if self.battle_setup.action_start_battle:
            self.battle_setup.action_start_battle = False
            team1, team2 = self.battle_setup.get_ships()
            self.start_battle(team1, team2)
        elif self.battle_setup.action_start_headless:
            self.battle_setup.action_start_headless = False
            team1, team2 = self.battle_setup.get_ships()
            log_info(f"Team 1: {len(team1)} ships ({sum(s.max_hp for s in team1):.0f} total HP)")
            log_info(f"Team 2: {len(team2)} ships ({sum(s.max_hp for s in team2):.0f} total HP)")
            log_info("Running simulation...")
            self.start_battle(team1, team2, headless=True)
        elif self.battle_setup.action_return_to_menu:
            self.battle_setup.action_return_to_menu = False
            self.state = GameState.MENU

    def _update_battle(self, frame_time, events):
        """Update and draw battle scene."""
        if self.battle_scene.headless_mode:
            update_battle_headless(self, self.battle_scene)
        else:
            update_battle_visual(self, self.battle_scene, frame_time, events)
            self.battle_scene.draw(self.screen)
            update_tick_rate(self.battle_scene, frame_time)
            draw_battle_hud(self.screen, self.battle_scene, font_med, PROFILER.is_active())


def main():
    game = Game()

    from game.core.registry import freeze_registry
    freeze_registry()

    try:
        game.run()
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        log_error("CRITICAL CRASH CAUGHT:")
        log_error(error_msg)
        with open(Paths.CRASH_LOG, "w") as f:
            f.write(error_msg)
        raise e

    PROFILER.save_history()


if __name__ == "__main__":
    main()
