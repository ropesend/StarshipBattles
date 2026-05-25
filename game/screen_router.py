"""Scene lifecycle, transitions, and overlay-dialog routing.

PROJ-309 sub-phase 3.9: extracted from `game/app.py`. Owns every
`start_*` / `on_*_return` method and the long-lived scene instances.
(`_handle_*_action` methods stay on `Game` because tests mock them on the
Game instance; `_create_workshop_context` stays on `Game` because it's a
pure builder reading `Game.registries` with no router state involvement.)

The router is constructed by `Game.__init__` after `bootstrap()` returns
and is the single source of truth for "which scene is active right now".
The run loop reads `router.active_scene` per frame.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Optional

import pygame

from game.core.constants import GameState
from game.core.profiling import profile_action
from game.core.protocols import IScene
from game.core.registry import get_default_registry_provider
from game.ui.screens.battle_screen import BattleScreen
from game.ui.screens.battle_setup.screen import (
    FleetBattleSetupScreen as BattleSetupScreen,
)
from game.ui.screens.galaxy_test import GalaxyTestScreen
from game.ui.screens.menu_scene import MenuScene
from game.ui.screens.new_game_setup_screen import NewGameSetupScreen
from game.ui.screens.strategy_screen import StrategyScreen
from game.ui.screens.test_lab import TestLabScreen
from game.ui.screens.workshop_context import WorkshopContext
from game.ui.screens.workshop_screen import DesignWorkshopScreen
from game.ui.utils import create_centered_rect

if TYPE_CHECKING:
    from game.app_bootstrap import BootstrapResult
    from game.core.state_machine import ScreenStateMachine


@dataclass(frozen=True)
class SceneCallbacks:
    """Bound callbacks scenes invoke. Owned by `Game` so test mocks on the
    Game instance (e.g. `game._handle_strategy_action = MagicMock()`) win.
    """
    battle_setup: Callable[..., None]
    battle: Callable[..., None]
    strategy: Callable[..., None]
    test_lab: Callable[..., None]

logger = logging.getLogger(__name__)


class ScreenRouter:
    """All scene lifecycle and inter-scene routing logic.

    Owns the long-lived scene instances (menu, workshop, battle setup,
    battle, strategy, test lab) and creates the dynamic ones on demand
    (research tree, galaxy test, keybindings, race setup, new-game setup,
    save selection).

    The router is given a `request_shutdown` hook so handlers like
    `_handle_strategy_action("quit_game")` can flag the run loop to stop
    without coupling back to `Game`.
    """

    def __init__(
        self,
        boot: "BootstrapResult",
        state_machine: "ScreenStateMachine",
        request_shutdown: Callable[[], None],
        menu_button_config: list[tuple[str, Any]],
        scene_callbacks: "SceneCallbacks",
    ):
        self._boot = boot
        self._state_machine = state_machine
        self._request_shutdown = request_shutdown
        self._scene_callbacks = scene_callbacks

        # Convenient aliases (read-only views into BootstrapResult).
        self.width = boot.width
        self.height = boot.height
        self.registries = boot.registries
        self.input_mapper = boot.input_mapper

        # Overlay-dialog state. `_forward_event_to_scene` (in RunLoop)
        # reads these to gate event dispatch.
        self.show_exit_dialog = False
        self.showing_load_menu = False
        self.showing_race_setup = False
        self.showing_new_game_setup: bool = False  # PROJ-199: lazy init elimination
        self.race_setup_window: Any = None
        self.new_game_setup_window: Any = None
        self.save_selection_window: Any = None

        # Menu scene (PROJ-65: unified scene dispatch).
        self._menu_scene = MenuScene(self.width, self.height, menu_button_config)
        self.menu_ui_manager = self._menu_scene.get_ui_manager()

        # Active scene for unified dispatch (PROJ-65).
        self.active_scene: IScene = self._menu_scene

        # Scene objects.
        # PROJ-211: pass registries explicitly (no fallback).
        context = WorkshopContext.standalone(
            tech_preset_name="default", registries=self.registries
        )
        context.on_return = self.on_builder_return
        self.builder_scene = DesignWorkshopScreen(self.width, self.height, context)
        self.battle_setup = BattleSetupScreen(
            self.width, self.height, scene_callbacks.battle_setup
        )
        self.battle_scene = BattleScreen(
            self.width, self.height, scene_callbacks.battle
        )
        self.strategy_scene = StrategyScreen(
            self.width, self.height,
            scene_callback=scene_callbacks.strategy,
            input_mapper=self.input_mapper,
        )
        self.test_lab_scene = TestLabScreen(
            self.width,
            self.height,
            battle_scene=self.battle_scene,
            scene_callback=scene_callbacks.test_lab,
        )

        # Optionally-instantiated scenes (created on demand).
        self.research_tree_scene: Any = None
        self.galaxy_test_scene: Any = None
        self.keybindings_scene: Any = None

    def _switch_scene(self, state: GameState, scene: IScene) -> None:
        """Switch to a new scene with validated transition (PROJ-259)."""
        self._state_machine.transition(state)
        self.active_scene = scene

    def update_resolution(self, w: int, h: int) -> None:
        """Called by RunLoop on VIDEORESIZE — keep router in sync."""
        self.width = w
        self.height = h
        self.menu_ui_manager.set_window_resolution((self.width, self.height))

    @profile_action("App: Start Builder")
    def start_builder(self, return_to: Any = None,
                      context: Optional[WorkshopContext] = None) -> None:
        """Enter design workshop. Uses state stack for return-to-previous.

        Standalone entries (Workshop launched directly from main menu)
        load the default game data set before constructing the screen so
        the component palette is populated. Integrated entries (Workshop
        launched from inside a running strategy session) inherit that
        session's already-loaded data and skip the load.
        """
        if context is None:
            from game.core.paths import Paths
            from game.data_loader import load_data_from_path

            load_data_from_path(Paths.DEFAULT_GAME_DATA_DIR)
            context = WorkshopContext.standalone(
                tech_preset_name="default", registries=self.registries
            )
        context.on_return = self.on_builder_return
        self.builder_scene = DesignWorkshopScreen(self.width, self.height, context)
        # PROJ-259: push current state so pop_and_return goes back to caller.
        self._state_machine.push_and_transition(GameState.BUILDER)
        self.active_scene = self.builder_scene

    def on_builder_return(self, custom_ship: Any = None) -> None:
        """Return from design workshop to caller (via state stack).

        When returning to the main menu (standalone Workshop session), the
        data set the Workshop loaded on entry is cleared so the menu has
        no data loaded. When returning to a strategy session, leave the
        registry alone — strategy still owns it.
        """
        if hasattr(self, 'builder_scene') and hasattr(self.builder_scene, 'cleanup'):
            self.builder_scene.cleanup()

        return_state = self._state_machine.pop_and_return()
        if return_state == GameState.STRATEGY:
            if hasattr(self.strategy_scene, 'handle_resize'):
                self.strategy_scene.handle_resize(self.width, self.height)
            self.active_scene = self.strategy_scene
        else:
            from game.data_loader import unload_data
            unload_data()
            self.active_scene = self._menu_scene

    @profile_action("App: Start Battle Setup")
    def start_battle_setup(self, preserve_teams: bool = False) -> None:
        """Enter battle setup screen."""
        self.return_state = GameState.BATTLE_SETUP
        self.battle_setup.start(preserve_teams=preserve_teams)
        self._switch_scene(GameState.BATTLE_SETUP, self.battle_setup)

    def start_strategy_layer(self) -> None:
        """Show new game setup screen."""
        logger.info("Opening new game setup")

        # Font preloading is handled in MenuScene/StrategyUI UIManager init.

        # Create new game setup window (expanded for race selection UI).
        window_rect = create_centered_rect(650, 600, self.width, self.height)

        self.new_game_setup_window = NewGameSetupScreen(
            window_rect,
            self.menu_ui_manager,
            on_start_callback=self._on_new_game_start,
            on_cancel_callback=self._on_new_game_cancel,
        )

        # Set flag to render window.
        self.showing_new_game_setup = True

    def _on_new_game_start(self, config: Any) -> None:
        """Handle new game start from setup screen."""
        from game.ai.ai_factory import AIControllerFactory
        from game.core.paths import Paths
        from game.data_loader import load_data_from_path
        from game.strategy.engine.game_session import GameSession
        from game.strategy.systems.save_game_service import SaveGameService

        logger.info(
            f"Starting new game: {config.save_name} with {len(config.players)} players"
        )
        # Mode-scoped data lifecycle: load the game data set into the
        # global registry BEFORE constructing GameSession. Today every
        # new game uses the default data path; a future mod-selection
        # UI can supply `getattr(config, 'data_path', None)` to drive
        # the same load against an alternative path.
        data_path = getattr(config, "data_path", None) or Paths.DEFAULT_GAME_DATA_DIR
        load_data_from_path(data_path)
        # PROJ-239: AI factory created here (UI layer) and injected into strategy layer.
        # PROJ-466 Phase 4: do NOT catch SessionInitializationError here. The
        # new-game path runs inside NewGameSetupController.on_start_clicked,
        # which owns the recoverable failure UX (keep the setup window alive +
        # set its error label). Catching here would make that handler dead and
        # still kill the window via the controller's unconditional kill().
        # (The quickstart path below has no controller and keeps its own guard.)
        session = GameSession(config=config, ai_factory=AIControllerFactory())
        success, message, save_path = SaveGameService.save_game(session, config.save_name)
        if success:
            session.save_path = save_path
            logger.info(f"Initial save created: {save_path}")
            # Pre-build homeworld complexes (same as quickstart).
            from game.strategy.quickstart_builder import QuickstartBuilder
            empire_ids = [e.id for e in session.empires]
            empire_themes = {e.id: e.empire_theme_id for e in session.empires}
            QuickstartBuilder.copy_quickstart_designs(
                save_path, empire_ids, empire_themes=empire_themes
            )
            QuickstartBuilder.spawn_initial_complexes(save_path, session)
            self.strategy_scene = StrategyScreen(
                self.width, self.height, session=session,
                scene_callback=self._scene_callbacks.strategy,
                input_mapper=self.input_mapper,
            )
            self._switch_scene(GameState.STRATEGY, self.strategy_scene)
            self.showing_new_game_setup = False
        else:
            logger.error(f"Failed to create initial save: {message}")
            import pygame_gui.windows
            error_rect = pygame.Rect(0, 0, 400, 200)
            error_rect.center = (self.width // 2, self.height // 2)
            pygame_gui.windows.UIMessageWindow(
                rect=error_rect,
                html_message=f"<b>Save Failed</b><br><br>{message}",
                manager=self.menu_ui_manager,
                window_title="Error",
            )

    def _on_new_game_cancel(self) -> None:
        """Cancel new game setup."""
        self.showing_new_game_setup = False
        logger.debug("New game setup cancelled")

    def _show_session_init_error(self, error: Exception) -> None:
        """Surface a recoverable error dialog for a session-init failure.

        PROJ-466: galaxy generation can fail (e.g. planet shortage after
        all retries) and raise ``SessionInitializationError``. Rather than
        letting it propagate to the top-level crash handler, show a
        ``UIMessageWindow`` so the player can pick a different seed / config.
        """
        import pygame_gui.windows

        error_rect = pygame.Rect(0, 0, 400, 200)
        error_rect.center = (self.width // 2, self.height // 2)
        pygame_gui.windows.UIMessageWindow(
            rect=error_rect,
            html_message=(
                "<b>Could Not Start Game</b><br><br>"
                "Galaxy generation failed. Try a different seed or "
                f"fewer/larger systems.<br><br>{error}"
            ),
            manager=self.menu_ui_manager,
            window_title="Error",
        )

    def _start_quickstart(self, player_count: int) -> None:
        """Start a quickstart game with the specified number of players.

        Args:
            player_count: Number of players (1 or 2).
        """
        from game.core.exceptions import SessionInitializationError
        from game.core.paths import Paths
        from game.data_loader import load_data_from_path
        from game.strategy.engine.game_session import GameSession
        from game.strategy.quickstart_builder import QuickstartBuilder
        from game.strategy.systems.save_game_service import SaveGameService

        logger.info(f"Starting Quickstart {player_count}P")

        # Mode-scoped data lifecycle: load the default game data set
        # into the global registry before constructing GameSession.
        load_data_from_path(Paths.DEFAULT_GAME_DATA_DIR)

        # Build config based on player count.
        if player_count == 1:
            config = QuickstartBuilder.build_1p_config()
            empire_ids = [0]
        else:
            config = QuickstartBuilder.build_2p_config()
            empire_ids = [0, 1]

        # PROJ-466: guard galaxy-generation failure on the quickstart path too.
        try:
            session = GameSession(config=config)
        except SessionInitializationError as e:
            logger.error("Quickstart session initialization failed: %s", e)
            self._show_session_init_error(e)
            return

        success, message, save_path = SaveGameService.save_game(session, config.save_name)

        if success:
            session.save_path = save_path
            logger.info(f"Quickstart {player_count}P save created: {save_path}")

            # Copy quickstart designs for empires (BUG-102: apply empire themes).
            empire_themes = {e.id: e.empire_theme_id for e in session.empires}
            QuickstartBuilder.copy_quickstart_designs(
                save_path, empire_ids, empire_themes=empire_themes
            )

            # Spawn initial complexes on home planets.
            QuickstartBuilder.spawn_initial_complexes(save_path, session)

            self.strategy_scene = StrategyScreen(
                self.width, self.height, session=session,
                scene_callback=self._scene_callbacks.strategy,
                input_mapper=self.input_mapper,
            )
            self._switch_scene(GameState.STRATEGY, self.strategy_scene)
        else:
            logger.error(f"Quickstart {player_count}P failed: {message}")

    def start_quickstart_1p(self) -> None:
        """Start a single-player quickstart game."""
        self._start_quickstart(player_count=1)

    def start_quickstart_2p(self) -> None:
        """Start a two-player quickstart game."""
        self._start_quickstart(player_count=2)

    def show_load_menu(self) -> None:
        """Show load game menu."""
        from game.ui.screens.save_selection_window import SaveSelectionWindow

        logger.info("Opening load game menu")

        # Font preloading is handled in MenuScene/StrategyUI UIManager init.

        # Create save selection window.
        window_rect = create_centered_rect(600, 500, self.width, self.height)

        self.save_selection_window = SaveSelectionWindow(
            window_rect,
            self.menu_ui_manager,
            on_load_callback=self._on_load_game,
            on_cancel_callback=self._on_load_cancel,
        )

        # Set flag to render window.
        self.showing_load_menu = True

    def _on_load_game(self, save_path: Any, turn_number: Any = None) -> None:
        """Load the selected save game."""
        from game.ai.ai_factory import AIControllerFactory
        from game.strategy.systems.save_game_service import SaveGameService

        logger.info(f"Loading game from: {save_path}, turn: {turn_number}")

        # Load game session (optionally at specific turn).
        # PROJ-239: AI factory created here (UI layer) and injected into strategy layer.
        game_session, message = SaveGameService.load_game(
            save_path, turn_number=turn_number, ai_factory=AIControllerFactory()
        )

        if game_session:
            # Create new strategy scene with loaded session.
            self.strategy_scene = StrategyScreen(
                self.width, self.height, session=game_session,
                scene_callback=self._scene_callbacks.strategy,
                input_mapper=self.input_mapper,
            )
            self._switch_scene(GameState.STRATEGY, self.strategy_scene)
            self.showing_load_menu = False
            logger.info(f"Game loaded successfully: {message}")
        else:
            logger.error(f"Failed to load game: {message}")
            # Show error dialog.
            import pygame_gui.windows
            error_rect = pygame.Rect(0, 0, 400, 200)
            error_rect.center = (self.width // 2, self.height // 2)
            pygame_gui.windows.UIMessageWindow(
                rect=error_rect,
                html_message=f"<b>Load Failed</b><br><br>{message}",
                manager=self.menu_ui_manager,
                window_title="Error",
            )

    def _on_load_cancel(self) -> None:
        """Cancel load game."""
        self.showing_load_menu = False
        logger.debug("Load game cancelled")

    def start_test_lab(self) -> None:
        """Enter Combat Lab.

        Loads the Combat Lab data set into the global registry on entry.
        TestRunner.load_data_for_scenario may later re-load a per-scenario
        subset; either way the matching ``unload_data()`` on return-to-menu
        clears the registry so no test fixtures leak into a subsequent
        New Game or Load Game session.
        """
        from game.core.paths import Paths
        from game.data_loader import load_data_from_path

        load_data_from_path(Paths.COMBAT_LAB_DATA_DIR)
        self.return_state = GameState.TEST_LAB
        self._switch_scene(GameState.TEST_LAB, self.test_lab_scene)

    def start_research_tree(self) -> None:
        """Enter Research Tree sandbox."""
        from game.ui.research.research_scene import ResearchTreeScene

        logger.info("Starting Research Tree sandbox")
        self.research_tree_scene = ResearchTreeScene(
            self.width, self.height,
            on_close_callback=self.on_research_tree_return,
        )
        self._switch_scene(GameState.RESEARCH_TREE, self.research_tree_scene)

    def on_research_tree_return(self) -> None:
        """Return from Research Tree to menu."""
        self.research_tree_scene = None
        self._switch_scene(GameState.MENU, self._menu_scene)

    def start_galaxy_test(self) -> None:
        """Enter Galaxy Test screen."""
        logger.info("Starting Galaxy Test screen")
        self.galaxy_test_scene = GalaxyTestScreen(
            self.width, self.height,
            on_close_callback=self.on_galaxy_test_return,
        )
        self._switch_scene(GameState.GALAXY_TEST, self.galaxy_test_scene)

    def on_galaxy_test_return(self) -> None:
        """Return from Galaxy Test to menu."""
        self.galaxy_test_scene = None
        self._switch_scene(GameState.MENU, self._menu_scene)

    def start_keybindings(self) -> None:
        """Open the keybindings editor scene (PROJ-71 Phase 4)."""
        from game.ui.screens.keybindings_scene import KeybindingsScene

        logger.info("Opening keybindings editor")
        self.keybindings_scene = KeybindingsScene(
            self.width, self.height,
            self.input_mapper,
            on_close_callback=self.on_keybindings_return,
        )
        # PROJ-259: push current state for return-to-previous.
        self._state_machine.push_and_transition(GameState.KEYBINDINGS)
        self.active_scene = self.keybindings_scene

    def on_keybindings_return(self) -> None:
        """Return from keybindings editor to previous scene (via state stack)."""
        logger.info("Returning from keybindings editor")
        return_state = self._state_machine.pop_and_return()

        if return_state == GameState.STRATEGY:
            if hasattr(self.strategy_scene, '_ui') and \
                    hasattr(self.strategy_scene._ui, '_apply_tooltips'):
                self.strategy_scene._ui._apply_tooltips()
            self.active_scene = self.strategy_scene
        else:
            self.active_scene = self._menu_scene

    def start_race_setup(self) -> None:
        """Open race setup wizard."""
        logger.info("Opening race setup wizard")

        # Font preloading is handled in MenuScene/StrategyUI UIManager init.

        # Create race setup window (larger for 2560x1600 displays).
        window_rect = create_centered_rect(1800, 1200, self.width, self.height)

        # Import here to avoid circular imports.
        from game.ui.screens.race_setup.screen import RaceSetupScreen

        self.race_setup_window = RaceSetupScreen(
            window_rect,
            self.menu_ui_manager,
            on_complete_callback=self._on_race_setup_complete,
            on_cancel_callback=self._on_race_setup_cancel,
        )

        self.showing_race_setup = True

    def _on_race_setup_complete(self, race_config: Any) -> None:
        """Handle race setup completion."""
        logger.info(f"Race setup complete: {race_config.name}")
        self.showing_race_setup = False
        self.race_setup_window = None

    def _on_race_setup_cancel(self) -> None:
        """Cancel race setup."""
        self.showing_race_setup = False
        self.race_setup_window = None
        logger.debug("Race setup cancelled")

    def start_battle(
        self,
        spec: Any,
        *,
        headless: bool = False,
        config: Optional[Any] = None,
        ship_builder: Optional[Any] = None,
    ) -> None:
        """Start a battle from a compiled `BattleSpec` (PROJ-270 Phase 3).

        FEAT-26: ``config`` (optional) lets callers thread a pre-built
        ``BattleConfig`` — used by the replay-launch path on the Event
        Log to set ``replay_mode=True`` + ``replay_id`` + the captured
        telemetry level. When ``config`` is supplied, ``headless`` is
        ignored (the caller has already set the right operational
        flags). When omitted, the original default-config build path
        runs unchanged.

        PROJ-368: ``ship_builder`` (optional) lets the replay-launch path
        supply a snapshot-backed materializer for replay specs whose
        ``ShipSpec.instance_ref`` is ``None``. When omitted, the
        controller falls back to the context materializer (the live
        path used by manual battles and quickstart).
        """
        from game.ai.ai_factory import AIControllerFactory
        from game.simulation.battle_config import BattleConfig
        from game.simulation.battle_controller import BattleController

        if (self.battle_scene.screen_width != self.width
                or self.battle_scene.screen_height != self.height):
            self.battle_scene.handle_resize(self.width, self.height)

        if config is None:
            config = BattleConfig(
                headless=headless,
                seed=spec.seed,
                end_condition=spec.end_condition,
                absolute_max_ticks=spec.absolute_max_ticks,
            )

        # PROJ-270 Phase 10 + PROJ-274: single spec-in path. Compiler
        # (build_manual_battle_spec) sets ship_spec.instance_ref so the
        # default InstanceBackedMaterializer in ApplicationContext handles
        # materialization. PROJ-306: pass registry_provider explicitly —
        # game/app.py is outside the Simulation layer and may call
        # get_default_registry_provider().
        controller = BattleController()
        controller.start_from_spec(
            spec,
            ai_factory=AIControllerFactory(),
            ship_builder=ship_builder,
            registry_provider=get_default_registry_provider(),
            config=config,
        )

        self.battle_scene.start_battle(controller)
        self._switch_scene(GameState.BATTLE, self.battle_scene)

    # Action handlers (_handle_*_action / _return_to) live on `Game`,
    # not the router, because tests mock them via `game._handle_X = MagicMock()`
    # and assert `self.X` references resolve to those mocks. Scene callbacks
    # wired in __init__ point at Game-side handlers via SceneCallbacks.
