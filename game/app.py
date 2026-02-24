"""Main game entry point - coordinates scenes and game loop."""
import argparse
import pygame
import pygame_gui
import os

from game.core.logger import log_debug, log_info, log_error
from game.core.config import DisplayConfig
from game.core.paths import Paths
from game.ui.utils import create_centered_rect
from game.simulation.components.component import load_components, load_modifiers
from game.core.resources import load_resources_data
from game.core.registry import GameRegistries, set_default_registries, RegistryManager
from pygame_gui.elements import UIButton
from game.ui.screens.workshop_screen import DesignWorkshopScreen
from game.ui.screens.workshop_context import WorkshopContext
from game.ui.renderer.sprites import SpriteManager
from game.ui.screens.battle_screen import BattleScreen
from game.ui.screens.setup_screen import BattleSetupScreen
from game.ui.screens.strategy_screen import StrategyScreen
from game.ui.screens.new_game_setup_screen import NewGameSetupScreen
from game.ui.screens.formation_editor import FormationEditorScreen
from game.ui.screens.test_lab import TestLabScreen
from game.ui.screens.galaxy_test import GalaxyTestScreen
from game.ui.screens.menu_scene import MenuScene
from game.core.profiling import Profiler, profile_action
from game.core.protocols import IScene
from game.ui.services.input_mapper import InputMapper
from game.core.input_actions import InputAction
from game.exit_dialog import (
    draw_exit_dialog, handle_exit_dialog_click, handle_exit_dialog_cancel
)

# Constants
DEFAULT_WIDTH, DEFAULT_HEIGHT = DisplayConfig.default_resolution()
FPS = 60
BG_COLOR = (10, 10, 20)

# Scene States
from game.core.constants import GameState


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Starship Battles")
    parser.add_argument('--force-resolution', action='store_true',
                        help='Force 2560x1600 resolution regardless of monitor size')
    args, _ = parser.parse_known_args()
    return args


class Game:
    """Main game class coordinating scenes and game loop."""

    def __init__(self, args=None):
        pygame.init()

        # Initialize fonts
        pygame.font.init()
        self.font_small = pygame.font.SysFont("arial", 12)
        self.font_med = pygame.font.SysFont("arial", 20)
        self.font_large = pygame.font.SysFont("arial", 32)

        # Monitor detection and resolution setup
        info = pygame.display.Info()
        monitor_w = info.current_w
        monitor_h = info.current_h

        force_resolution = args.force_resolution if args else False
        if force_resolution:
            self.width, self.height = DisplayConfig.default_resolution()
        elif monitor_w >= 3840 and monitor_h >= 2160:
            self.width, self.height = 3840, 2160
        elif monitor_w >= 2560 and monitor_h >= 1600:
            self.width, self.height = 2560, 1600
        else:
            self.width, self.height = int(monitor_w * 0.9), int(monitor_h * 0.9)

        if not pygame.display.get_surface():
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        else:
            self.screen = pygame.display.get_surface()

        pygame.display.set_caption(f"Starship Battles ({self.width}x{self.height})")

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
        # PROJ-121: Use DI-friendly load_resources_data() directly
        resources_registry = RegistryManager.instance().resources
        resources_registry.update(load_resources_data(Paths.RESOURCES_FILE))

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

        # Initialize input mapper (PROJ-71: centralized keybindings)
        self.input_mapper = InputMapper()
        self.input_mapper.load(Paths.DEFAULT_KEYBINDINGS_FILE, Paths.USER_KEYBINDINGS_FILE)

        # Load sprites
        sprite_mgr = SpriteManager.instance()
        sprite_mgr.load_sprites(Paths.ROOT_DIR)

        # Menu scene (PROJ-65: unified scene dispatch)
        self._menu_scene = MenuScene(self.width, self.height, self._get_menu_button_config())
        self.menu_ui_manager = self._menu_scene.get_ui_manager()

        # Active scene for unified dispatch (PROJ-65)
        self.active_scene: IScene = self._menu_scene

        # Scene objects
        context = WorkshopContext.standalone(tech_preset_name="default")
        context.on_return = self.on_builder_return
        self.builder_scene = DesignWorkshopScreen(self.width, self.height, context)
        self.battle_setup = BattleSetupScreen(self.width, self.height, self._handle_battle_setup_action)
        self.battle_scene = BattleScreen(self.width, self.height, self._handle_battle_action)
        self.strategy_scene = StrategyScreen(self.width, self.height, scene_callback=self._handle_strategy_action, input_mapper=self.input_mapper)
        self.formation_scene = FormationEditorScreen(self.width, self.height, self.on_formation_return)
        self.test_lab_scene = TestLabScreen(self, scene_callback=self._handle_test_lab_action)

    def _get_menu_button_config(self):
        """Get button configuration for MenuScene."""
        return [
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

    def _switch_scene(self, state: GameState, scene: IScene) -> None:
        """Switch to a new scene with unified dispatch (PROJ-65)."""
        self.state = state
        self.active_scene = scene

    @profile_action("App: Start Builder")
    def start_builder(self, return_to=None, context=None):
        """
        Enter design workshop.

        Args:
            return_to: State to return to (MENU or STRATEGY)
            context: Optional WorkshopContext for integrated mode
        """
        self.builder_return_state = return_to
        # Use provided context or create default standalone context
        if context is None:
            context = WorkshopContext.standalone(tech_preset_name="default")
        context.on_return = self.on_builder_return
        self.builder_scene = DesignWorkshopScreen(self.width, self.height, context)
        self._switch_scene(GameState.BUILDER, self.builder_scene)

    def on_builder_return(self, custom_ship=None):
        """Return from design workshop to caller or main menu."""
        # Clean up workshop UI elements before switching state
        if hasattr(self, 'builder_scene') and hasattr(self.builder_scene, 'cleanup'):
            self.builder_scene.cleanup()

        if self.builder_return_state == GameState.STRATEGY:
            if hasattr(self.strategy_scene, 'handle_resize'):
                self.strategy_scene.handle_resize(self.width, self.height)
            self._switch_scene(GameState.STRATEGY, self.strategy_scene)
        else:
            self._switch_scene(GameState.MENU, self._menu_scene)
        self.builder_return_state = None

    @profile_action("App: Start Battle Setup")
    def start_battle_setup(self, preserve_teams=False):
        """Enter battle setup screen."""
        self.return_state = GameState.BATTLE_SETUP
        self.battle_setup.start(preserve_teams=preserve_teams)
        self._switch_scene(GameState.BATTLE_SETUP, self.battle_setup)

    def start_strategy_layer(self):
        """Show new game setup screen."""
        import pygame_gui

        log_info("Opening new game setup")

        # Font preloading is handled in MenuScene/StrategyUI UIManager init

        # Create new game setup window (expanded for race selection UI)
        window_rect = create_centered_rect(650, 600, self.width, self.height)

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

            # Pre-build homeworld complexes (same as quickstart)
            from game.strategy.quickstart_builder import QuickstartBuilder
            empire_ids = [e.id for e in session.empires]
            QuickstartBuilder.copy_quickstart_designs(save_path, empire_ids)
            QuickstartBuilder.spawn_initial_complexes(save_path, session)

            # Create strategy scene with new session
            self.strategy_scene = StrategyScreen(self.width, self.height, session=session, scene_callback=self._handle_strategy_action, input_mapper=self.input_mapper)
            self._switch_scene(GameState.STRATEGY, self.strategy_scene)
            self.showing_new_game_setup = False
        else:
            log_error(f"Failed to create initial save: {message}")
            # Show error dialog
            import pygame_gui.windows
            error_rect = pygame.Rect(0, 0, 400, 200)
            error_rect.center = (self.width // 2, self.height // 2)
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

            # Spawn initial complexes on home planets
            QuickstartBuilder.spawn_initial_complexes(save_path, session)

            self.strategy_scene = StrategyScreen(self.width, self.height, session=session, scene_callback=self._handle_strategy_action, input_mapper=self.input_mapper)
            self._switch_scene(GameState.STRATEGY, self.strategy_scene)
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

        # Font preloading is handled in MenuScene/StrategyUI UIManager init

        # Create save selection window
        window_rect = create_centered_rect(600, 500, self.width, self.height)

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
            self.strategy_scene = StrategyScreen(self.width, self.height, session=game_session, scene_callback=self._handle_strategy_action, input_mapper=self.input_mapper)
            self._switch_scene(GameState.STRATEGY, self.strategy_scene)
            self.showing_load_menu = False
            log_info(f"Game loaded successfully: {message}")
        else:
            log_error(f"Failed to load game: {message}")
            # Show error dialog
            import pygame_gui.windows
            error_rect = pygame.Rect(0, 0, 400, 200)
            error_rect.center = (self.width // 2, self.height // 2)
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
        self.formation_scene.handle_resize(self.width, self.height)
        self._switch_scene(GameState.FORMATION, self.formation_scene)

    def on_formation_return(self):
        """Return from formation editor."""
        self._switch_scene(GameState.MENU, self._menu_scene)

    def start_test_lab(self):
        """Enter Combat Lab."""
        self.return_state = GameState.TEST_LAB
        self._switch_scene(GameState.TEST_LAB, self.test_lab_scene)

    def start_research_tree(self):
        """Enter Research Tree sandbox."""
        from game.ui.research.research_scene import ResearchTreeScene

        log_info("Starting Research Tree sandbox")
        self.research_tree_scene = ResearchTreeScene(
            self.width, self.height,
            on_close_callback=self.on_research_tree_return
        )
        self._switch_scene(GameState.RESEARCH_TREE, self.research_tree_scene)

    def on_research_tree_return(self):
        """Return from Research Tree to menu."""
        self.research_tree_scene = None
        self._switch_scene(GameState.MENU, self._menu_scene)

    def start_galaxy_test(self):
        """Enter Galaxy Test screen."""
        log_info("Starting Galaxy Test screen")
        self.galaxy_test_scene = GalaxyTestScreen(
            self.width, self.height,
            on_close_callback=self.on_galaxy_test_return
        )
        self._switch_scene(GameState.GALAXY_TEST, self.galaxy_test_scene)

    def on_galaxy_test_return(self):
        """Return from Galaxy Test to menu."""
        self.galaxy_test_scene = None
        self._switch_scene(GameState.MENU, self._menu_scene)

    def start_keybindings(self):
        """Open the keybindings editor scene (PROJ-71 Phase 4)."""
        from game.ui.screens.keybindings_scene import KeybindingsScene

        log_info("Opening keybindings editor")
        self._keybindings_return_state = self.state
        self.keybindings_scene = KeybindingsScene(
            self.width, self.height,
            self.input_mapper,
            on_close_callback=self.on_keybindings_return,
        )
        self._switch_scene(GameState.KEYBINDINGS, self.keybindings_scene)

    def on_keybindings_return(self):
        """Return from keybindings editor to previous scene."""
        log_info("Returning from keybindings editor")
        return_state = getattr(self, '_keybindings_return_state', GameState.MENU)

        if return_state == GameState.STRATEGY:
            # Refresh tooltips on strategy UI with possibly changed bindings
            if hasattr(self.strategy_scene, '_ui') and hasattr(self.strategy_scene._ui, '_apply_tooltips'):
                self.strategy_scene._ui._apply_tooltips()
            self._switch_scene(GameState.STRATEGY, self.strategy_scene)
        else:
            self._switch_scene(GameState.MENU, self._menu_scene)

        self._keybindings_return_state = None

    def start_race_setup(self):
        """Open race setup wizard."""
        import pygame_gui

        log_info("Opening race setup wizard")

        # Font preloading is handled in MenuScene/StrategyUI UIManager init

        # Create race setup window (larger for 2560x1600 displays)
        window_rect = create_centered_rect(1800, 1200, self.width, self.height)

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
        if self.battle_scene.screen_width != self.width or self.battle_scene.screen_height != self.height:
            self.battle_scene.handle_resize(self.width, self.height)
        self.battle_scene.start(team1_ships, team2_ships, headless=headless)
        self._switch_scene(GameState.BATTLE, self.battle_scene)

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
        """Handle events during normal gameplay.

        PROJ-88 Phase 5: Removed legacy MOUSEBUTTONDOWN/MOUSEWHEEL dispatch.
        These events now flow through _forward_event_to_scene() to each scene's
        handle_event() method, completing the IScene migration.
        """
        for event in events:
            state_before = self.state

            if event.type == pygame.QUIT:
                self.show_exit_dialog = True
            elif event.type == pygame.KEYDOWN:
                action = self.input_mapper.resolve(event, contexts=["global"])
                if action == InputAction.GLOBAL_EXIT:
                    self.show_exit_dialog = True
                elif action == InputAction.GLOBAL_TOGGLE_PROFILER:
                    active = Profiler.instance().toggle()
                    log_info(f"Profiling {'ENABLED' if active else 'DISABLED'}")
            elif event.type == pygame.VIDEORESIZE:
                self._handle_resize(event.w, event.h)

            # Forward events to current scene only if state didn't change
            if self.state != state_before:
                log_debug(f"State changed from {state_before} to {self.state}")
                continue

            self._forward_event_to_scene(event)

    def _forward_event_to_scene(self, event):
        """Forward event to the current active scene (PROJ-65: unified dispatch)."""
        # Handle overlay dialogs on menu - these use the menu's ui_manager
        if self.state == GameState.MENU:
            if hasattr(self, 'showing_new_game_setup') and self.showing_new_game_setup:
                self.menu_ui_manager.process_events(event)
                return
            if self.showing_load_menu:
                self.menu_ui_manager.process_events(event)
                return
            if self.showing_race_setup:
                self.menu_ui_manager.process_events(event)
                return

        # Unified dispatch to active scene
        self.active_scene.handle_event(event)

    def _handle_resize(self, w, h):
        """Handle window resize (PROJ-65: unified dispatch)."""
        self.width, self.height = w, h
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)

        # Update menu UIManager resolution (needed for overlay dialogs)
        self.menu_ui_manager.set_window_resolution((self.width, self.height))

        # Unified dispatch to active scene
        self.active_scene.handle_resize(w, h)

    def _handle_battle_action(self, action: str, **kwargs):
        """Handle scene actions from BattleScreen."""
        if action == "return_to_test_lab":
            log_debug("Returning to Combat Lab from test")
            self.battle_scene.test_mode = False
            self.test_lab_scene.reset_selection()
            self.start_test_lab()
        elif action == "return_to_setup":
            log_debug("Returning to battle setup")
            if hasattr(self, 'return_state') and self.return_state == GameState.TEST_LAB:
                self.start_test_lab()
            else:
                self.start_battle_setup(preserve_teams=True)

    def _handle_strategy_action(self, action: str, **kwargs):
        """Handle scene actions from StrategyScreen."""
        if action == "open_builder":
            context_data = kwargs.get("context_data", {})
            context = self._create_workshop_context(context_data)
            self.start_builder(return_to=GameState.STRATEGY, context=context)
        elif action == "load_game":
            save_path = kwargs.get("save_path")
            turn_number = kwargs.get("turn_number")
            if save_path:
                self._on_load_game(save_path, turn_number)
        elif action == "open_keybindings":
            self.start_keybindings()
        elif action == "quit_to_menu":
            log_info("Returning to main menu from strategy")
            self._switch_scene(GameState.MENU, self._menu_scene)
        elif action == "quit_game":
            log_info("Quitting game from strategy menu")
            self.running = False

    def _create_workshop_context(self, context_data: dict):
        """Create WorkshopContext from strategy scene context data."""
        empire = context_data.get('empire')
        game_session = context_data.get('game_session')

        if not empire or not game_session:
            return None

        from game.ui.screens.workshop_context import WorkshopContext

        # Get empire tech (placeholder for now - will be implemented when tech tree exists)
        available_tech_ids = []  # TODO: Replace with empire.available_tech or similar

        # Get savegame path (may be None for new games - that's OK!)
        savegame_path = game_session.save_path if hasattr(game_session, 'save_path') else None

        # Get empire theme
        empire_theme_id = empire.empire_theme_id if hasattr(empire, 'empire_theme_id') else None
        log_debug(f"Creating WorkshopContext with empire_theme_id={empire_theme_id}")

        # Create integrated context regardless of save_path
        return WorkshopContext.integrated(
            empire_id=empire.id,
            savegame_path=savegame_path,
            available_tech_ids=available_tech_ids,
            built_designs=empire.built_ship_designs if hasattr(empire, 'built_ship_designs') else set(),
            empire_theme_id=empire_theme_id
        )

    def _handle_test_lab_action(self, action: str, **kwargs):
        """Handle scene actions from TestLabScreen."""
        if action == "return_to_menu":
            self._switch_scene(GameState.MENU, self._menu_scene)

    def _update_and_draw(self, frame_time, events):
        """Update logic and draw current scene (PROJ-65: unified dispatch).

        PROJ-88 Phase 5: StrategyScreen event dispatch is now fully through
        handle_event(). The update_input() call remains for per-frame keyboard
        polling (arrow keys for panning) and hover logic.
        """
        # Per-frame input handling (keyboard polling, hover)
        if self.state == GameState.STRATEGY:
            self.strategy_scene.update_input(frame_time, events)
        # Legacy scenes that haven't migrated to IScene event handling
        elif self.state == GameState.RESEARCH_TREE and hasattr(self.active_scene, 'handle_input'):
            self.active_scene.handle_input(frame_time, events)
        elif self.state == GameState.GALAXY_TEST and hasattr(self.active_scene, 'handle_input'):
            self.active_scene.handle_input(frame_time, events)

        # Unified update dispatch
        self.active_scene.update(frame_time)

        # Unified draw dispatch (some scenes have special draw logic)
        if self.state == GameState.BATTLE:
            # BattleScreen handles headless mode internally
            if not self.battle_scene.headless_mode:
                self.active_scene.draw(self.screen)
                self.battle_scene.draw_hud(self.screen, self.font_med, Profiler.instance().is_active())
        else:
            self.active_scene.draw(self.screen)

        if self.show_exit_dialog:
            draw_exit_dialog(self.screen, self.font_large, self.font_med)

    def _handle_battle_setup_action(self, action: str, **kwargs):
        """Handle scene actions from BattleSetupScreen."""
        if action == "start_battle":
            self.start_battle(kwargs["team1"], kwargs["team2"])
        elif action == "start_headless":
            team1, team2 = kwargs["team1"], kwargs["team2"]
            log_info(f"Team 1: {len(team1)} ships ({sum(s.max_hp for s in team1):.0f} total HP)")
            log_info(f"Team 2: {len(team2)} ships ({sum(s.max_hp for s in team2):.0f} total HP)")
            log_info("Running simulation...")
            self.start_battle(team1, team2, headless=True)
        elif action == "return_to_menu":
            self._switch_scene(GameState.MENU, self._menu_scene)


def main():
    args = parse_args()
    game = Game(args)

    from game.core.registry import freeze_registry
    freeze_registry()

    try:
        game.run()
    except Exception as e:  # Intentional broad catch: top-level crash handler, logs and re-raises
        import traceback
        error_msg = traceback.format_exc()
        log_error("CRITICAL CRASH CAUGHT:")
        log_error(error_msg)
        with open(Paths.CRASH_LOG, "w") as f:
            f.write(error_msg)
        raise e

    Profiler.instance().save_history()


if __name__ == "__main__":
    main()
