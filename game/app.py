"""Main game entry point — composition root coordinating bootstrap,
screen-routing, and the run loop.

PROJ-309 sub-phase 3.9: this module is now a slim shell. The historical
~850-LOC `Game` class was decomposed into:

- `game.app_bootstrap` — pygame init + services wiring (returns
  `BootstrapResult`).
- `game.screen_router` — scene lifecycle + transitions + overlay dialogs.
- `game.run_loop` — per-frame event/draw dispatch + shutdown.

`Game` retains the public method/attribute surface that callers
(`launcher.py` + 4 test files) depend on, but the actual work is
delegated to the helper modules.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional

from game.app_bootstrap import (
    BootstrapResult,
    bootstrap,
    configure_logging,
    parse_args,
)
from game.core.constants import GameState
from game.core.paths import Paths
from game.core.state_machine import ScreenStateMachine
from game.run_loop import RunLoop
from game.screen_router import SceneCallbacks, ScreenRouter
from game.strategy.services.replay_ship_builder import build_replay_ship_builder

if TYPE_CHECKING:
    from game.ui.screens.workshop_context import WorkshopContext

logger = logging.getLogger(__name__)


# PROJ-259: Valid screen transitions (from_state, to_state).
_SCREEN_TRANSITIONS = frozenset({
    (GameState.MENU, GameState.BUILDER),
    (GameState.MENU, GameState.BATTLE_SETUP),
    (GameState.MENU, GameState.STRATEGY),
    (GameState.MENU, GameState.TEST_LAB),
    (GameState.MENU, GameState.RESEARCH_TREE),
    (GameState.MENU, GameState.GALAXY_TEST),
    (GameState.BUILDER, GameState.MENU),
    (GameState.BUILDER, GameState.STRATEGY),
    (GameState.BATTLE, GameState.BATTLE_SETUP),
    (GameState.BATTLE, GameState.TEST_LAB),
    (GameState.BATTLE, GameState.STRATEGY),
    (GameState.BATTLE_SETUP, GameState.MENU),
    (GameState.BATTLE_SETUP, GameState.BATTLE),
    (GameState.TEST_LAB, GameState.MENU),
    (GameState.TEST_LAB, GameState.BATTLE),
    (GameState.RESEARCH_TREE, GameState.MENU),
    (GameState.GALAXY_TEST, GameState.MENU),
    (GameState.STRATEGY, GameState.BUILDER),
    (GameState.STRATEGY, GameState.MENU),
    (GameState.STRATEGY, GameState.KEYBINDINGS),
    (GameState.STRATEGY, GameState.BATTLE),
    (GameState.KEYBINDINGS, GameState.STRATEGY),
    (GameState.KEYBINDINGS, GameState.MENU),
})


class Game:
    """Composition root.

    Holds the BootstrapResult, ScreenRouter, RunLoop, and the
    ScreenStateMachine. Public methods are thin delegators kept here for
    test-asserted callers (see PROJ-309 sub-phase 3.9 design doc §"Method-
    delegation contract").
    """

    def __init__(self, args: Any = None):
        # Phase A: bootstrap services + pygame + registries (single linear
        # init sequence with documented ordering invariants).
        self._boot: BootstrapResult = bootstrap(args)

        # Convenience aliases — many tests/scenes read these directly.
        self.ctx = self._boot.ctx
        self.screen = self._boot.screen
        self.width = self._boot.width
        self.height = self._boot.height
        self.clock = self._boot.clock
        self.font_small = self._boot.font_small
        self.font_med = self._boot.font_med
        self.font_large = self._boot.font_large
        self.registries = self._boot.registries
        self.input_mapper = self._boot.input_mapper

        # PROJ-259: Screen state machine with validated transitions.
        self.state_machine = ScreenStateMachine(
            initial_state=GameState.MENU,
            transitions=_SCREEN_TRANSITIONS,
        )

        # Phase B: screen router (owns scene instances + transitions).
        # Scene callbacks point back to Game's `_handle_*_action` methods
        # so test mocks on the Game instance win over router internals.
        scene_callbacks = SceneCallbacks(
            battle_setup=self._handle_battle_setup_action,
            battle=self._handle_battle_action,
            strategy=self._handle_strategy_action,
            test_lab=self._handle_test_lab_action,
        )
        self._router = ScreenRouter(
            boot=self._boot,
            state_machine=self.state_machine,
            request_shutdown=self._request_shutdown,
            menu_button_config=self._get_menu_button_config(),
            scene_callbacks=scene_callbacks,
        )

        # Phase C: run loop (per-frame pump).
        self._loop = RunLoop(
            boot=self._boot,
            router=self._router,
            state_machine=self.state_machine,
        )

        # NOTE (2026-04-27 merge resolution): the `ensure_component_derivatives()`
        # call and `sprite_mgr.load_sprites(...)` from branch 8ec8eafe9 were
        # MOVED into `app_bootstrap.bootstrap()`, where sprite loading already
        # lives (Invariant 5). Asset-derivative generation must precede sprite
        # loading because the sprite manager reads files this step generates;
        # both are deterministic init work and belong in the single linear
        # bootstrap rather than `Game.__init__`.

    # ------------------------------------------------------------------
    # Menu-button wiring
    # ------------------------------------------------------------------

    def _get_menu_button_config(self) -> list[tuple[str, Any]]:
        """Get button configuration for MenuScene."""
        return [
            ("Quickstart 1P", self.start_quickstart_1p),
            ("Quickstart 2P", self.start_quickstart_2p),
            ("New Game", self.start_strategy_layer),
            ("Load Game", self.show_load_menu),
            ("Race Setup", self.start_race_setup),
            ("Design Workshop", self.start_builder),
            ("Battle Setup", self.start_battle_setup),
            ("Combat Lab", self.start_test_lab),
            ("Research Tree", self.start_research_tree),
            ("Galaxy Test", self.start_galaxy_test),
        ]

    # ------------------------------------------------------------------
    # State proxy
    # ------------------------------------------------------------------

    @property
    def state(self) -> GameState:
        """Current game state — delegates to state machine."""
        return self.state_machine.state

    @state.setter
    def state(self, value: GameState) -> None:
        """Direct state assignment — only for initial setup. Use _switch_scene for transitions."""
        # During init, state_machine may not exist yet.
        if hasattr(self, 'state_machine'):
            self.state_machine._state = value
        # No-op before state_machine is created (handled by state_machine init).

    def _switch_scene(self, state: GameState, scene: Any) -> None:
        """Switch to a new scene with validated transition (PROJ-259)."""
        self._router._switch_scene(state, scene)

    # ------------------------------------------------------------------
    # Scene attribute proxies — properties that delegate to the router
    # when present, otherwise fall through to `__dict__` so tests can
    # bypass `__init__` (`Game.__new__(Game)`) and assign attributes
    # directly. The router is the canonical owner in production; tests
    # see plain instance attributes.
    # ------------------------------------------------------------------

    def _route_get(self, name: str) -> Any:
        router = self.__dict__.get('_router')
        if router is not None:
            return getattr(router, name)
        # Test path: bypass init, attribute lives in __dict__.
        try:
            return self.__dict__[name]
        except KeyError as e:
            raise AttributeError(name) from e

    def _route_set(self, name: str, value: Any) -> None:
        router = self.__dict__.get('_router')
        if router is not None:
            setattr(router, name, value)
        else:
            self.__dict__[name] = value

    @property
    def active_scene(self) -> Any: return self._route_get('active_scene')
    @active_scene.setter
    def active_scene(self, value: Any) -> None: self._route_set('active_scene', value)

    @property
    def battle_scene(self) -> Any: return self._route_get('battle_scene')
    @battle_scene.setter
    def battle_scene(self, value: Any) -> None: self._route_set('battle_scene', value)

    @property
    def battle_setup(self) -> Any: return self._route_get('battle_setup')
    @battle_setup.setter
    def battle_setup(self, value: Any) -> None: self._route_set('battle_setup', value)

    @property
    def strategy_scene(self) -> Any: return self._route_get('strategy_scene')
    @strategy_scene.setter
    def strategy_scene(self, value: Any) -> None: self._route_set('strategy_scene', value)

    @property
    def builder_scene(self) -> Any: return self._route_get('builder_scene')
    @builder_scene.setter
    def builder_scene(self, value: Any) -> None: self._route_set('builder_scene', value)

    @property
    def test_lab_scene(self) -> Any: return self._route_get('test_lab_scene')
    @test_lab_scene.setter
    def test_lab_scene(self, value: Any) -> None: self._route_set('test_lab_scene', value)

    @property
    def menu_scene(self) -> Any: return self._route_get('_menu_scene')
    @menu_scene.setter
    def menu_scene(self, value: Any) -> None: self._route_set('_menu_scene', value)

    @property
    def menu_ui_manager(self) -> Any: return self._route_get('menu_ui_manager')

    @property
    def show_exit_dialog(self) -> bool: return self._route_get('show_exit_dialog')
    @show_exit_dialog.setter
    def show_exit_dialog(self, value: bool) -> None: self._route_set('show_exit_dialog', value)

    @property
    def showing_load_menu(self) -> bool: return self._route_get('showing_load_menu')
    @showing_load_menu.setter
    def showing_load_menu(self, value: bool) -> None: self._route_set('showing_load_menu', value)

    @property
    def showing_race_setup(self) -> bool: return self._route_get('showing_race_setup')
    @showing_race_setup.setter
    def showing_race_setup(self, value: bool) -> None: self._route_set('showing_race_setup', value)

    @property
    def showing_new_game_setup(self) -> bool: return self._route_get('showing_new_game_setup')
    @showing_new_game_setup.setter
    def showing_new_game_setup(self, value: bool) -> None: self._route_set('showing_new_game_setup', value)

    # ------------------------------------------------------------------
    # Shutdown bridge
    # ------------------------------------------------------------------

    def _request_shutdown(self) -> None:
        """Hook passed to ScreenRouter so handlers can stop the loop."""
        if hasattr(self, '_loop'):
            self._loop.request_shutdown()

    # ------------------------------------------------------------------
    # Scene lifecycle delegators
    # ------------------------------------------------------------------

    def start_builder(self, return_to: Any = None,
                      context: Optional["WorkshopContext"] = None) -> None:
        self._router.start_builder(return_to=return_to, context=context)

    def on_builder_return(self, custom_ship: Any = None) -> None:
        self._router.on_builder_return(custom_ship=custom_ship)

    def start_battle_setup(self, preserve_teams: bool = False) -> None:
        self._router.start_battle_setup(preserve_teams=preserve_teams)

    def start_strategy_layer(self) -> None:
        self._router.start_strategy_layer()

    def _on_new_game_start(self, config: Any) -> None:
        self._router._on_new_game_start(config)

    def _on_new_game_cancel(self) -> None:
        self._router._on_new_game_cancel()

    def _start_quickstart(self, player_count: int) -> None:
        self._router._start_quickstart(player_count)

    def start_quickstart_1p(self) -> None:
        self._router.start_quickstart_1p()

    def start_quickstart_2p(self) -> None:
        self._router.start_quickstart_2p()

    def show_load_menu(self) -> None:
        self._router.show_load_menu()

    def _on_load_game(self, save_path: Any, turn_number: Any = None) -> None:
        self._router._on_load_game(save_path, turn_number)

    def _on_load_cancel(self) -> None:
        self._router._on_load_cancel()

    def start_test_lab(self) -> None:
        self._router.start_test_lab()

    def start_research_tree(self) -> None:
        self._router.start_research_tree()

    def on_research_tree_return(self) -> None:
        self._router.on_research_tree_return()

    def start_galaxy_test(self) -> None:
        self._router.start_galaxy_test()

    def on_galaxy_test_return(self) -> None:
        self._router.on_galaxy_test_return()

    def start_keybindings(self) -> None:
        self._router.start_keybindings()

    def on_keybindings_return(self) -> None:
        self._router.on_keybindings_return()

    def start_race_setup(self) -> None:
        self._router.start_race_setup()

    def _on_race_setup_complete(self, race_config: Any) -> None:
        self._router._on_race_setup_complete(race_config)

    def _on_race_setup_cancel(self) -> None:
        self._router._on_race_setup_cancel()

    def start_battle(
        self,
        spec: Any,
        *,
        headless: bool = False,
        config: Optional[Any] = None,
        ship_builder: Optional[Any] = None,
    ) -> None:
        self._router.start_battle(
            spec, headless=headless, config=config, ship_builder=ship_builder
        )

    def start_replay(self, record: Any) -> None:
        """FEAT-26 / PROJ-368: launch a captured replay in the BattleScreen.

        Reconstructs the playable ``BattleSpec`` from a ``ReplayRecord``
        (PROJ-312 Phase 5's ``replay_record_to_spec``), builds a
        ``BattleConfig`` with ``replay_mode=True`` so the BattleScreen
        renders the REPLAY MODE badge, and dispatches through the
        standard ``start_battle`` entry. Capture is intentionally skipped
        for replay playback (no recursion).

        PROJ-368: replays' ``ShipSpec.instance_ref`` is intentionally
        ``None`` (see ``replay_record_to_spec`` docstring). We supply a
        snapshot-backed ``ship_builder`` from
        ``build_replay_ship_builder`` so the materializer reconstructs
        each ship from its captured ``ShipInstance`` snapshot rather
        than failing in ``InstanceBackedMaterializer``.
        """
        from game.core.registry import get_default_registry_provider
        from game.core.return_destination import ReturnDestination
        from game.simulation.battle_config import BattleConfig
        from game.simulation.replay.replay_player import replay_record_to_spec

        spec = replay_record_to_spec(record)
        config = BattleConfig(
            seed=spec.seed,
            end_condition=spec.end_condition,
            absolute_max_ticks=spec.absolute_max_ticks,
            replay_mode=True,
            replay_id=record.replay_id,
            captured_telemetry_level=getattr(spec, "telemetry_level", None),
            # PROJ-368 (post-r001): the only caller today is the strategy
            # Event Log; on exit we must land back on the strategy scene
            # rather than the BattleConfig default of BATTLE_SETUP.
            return_destination=ReturnDestination.STRATEGY,
        )
        ship_builder = build_replay_ship_builder(
            record, registry_provider=get_default_registry_provider()
        )
        self.start_battle(spec, config=config, ship_builder=ship_builder)

    # ------------------------------------------------------------------
    # Action handler dispatch (kept on `Game` for test-mockability:
    # tests substitute `game._switch_scene = MagicMock()` etc. and expect
    # the dispatch body to call those `self.X` attributes).
    # ------------------------------------------------------------------

    def _handle_battle_action(self, action: str, **kwargs: Any) -> None:
        """Handle scene actions from BattleScreen or BattleResultsScreen."""
        if action == "show_results":
            results = kwargs.get("results")
            if results:
                from game.ui.screens.battle_results_screen import BattleResultsScreen
                results_screen = BattleResultsScreen(
                    self.width, self.height, results,
                    scene_callback=self._handle_battle_action,
                )
                self.active_scene = results_screen
                logger.info("Showing battle results screen")
        elif action == "return_to_destination":
            dest = kwargs.get("destination", "battle_setup")
            self._return_to(dest)
        elif action == "return_to_test_lab":
            self._return_to("test_lab")
        elif action == "return_to_setup":
            self._return_to("battle_setup")

    def _return_to(self, destination: str) -> None:
        """Navigate to the specified destination after a battle."""
        logger.debug(f"Returning to: {destination}")
        if destination == "test_lab":
            self.test_lab_scene.reset_selection()
            self.start_test_lab()
        elif destination == "battle_setup":
            self.start_battle_setup(preserve_teams=True)
        elif destination == "strategy":
            self._switch_scene(GameState.STRATEGY, self.strategy_scene)

    def _handle_strategy_action(self, action: str, **kwargs: Any) -> None:
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
        elif action == "launch_replay":
            record = kwargs.get("record")
            if record is not None:
                self.start_replay(record)
        elif action == "quit_to_menu":
            logger.info("Returning to main menu from strategy")
            self._switch_scene(GameState.MENU, self.menu_scene)
        elif action == "quit_game":
            logger.info("Quitting game from strategy menu")
            self._request_shutdown()

    def _create_workshop_context(self, context_data: dict) -> Optional["WorkshopContext"]:
        """Create WorkshopContext from strategy scene context data."""
        empire = context_data.get('empire')
        game_session = context_data.get('game_session')

        if not empire or not game_session:
            return None

        from game.ui.screens.workshop_context import WorkshopContext

        # Get empire tech (placeholder for now - will be implemented when tech tree exists)
        available_tech_ids: list[str] = []  # TODO: Replace with empire.available_tech or similar

        # Get savegame path (may be None for new games - that's OK!)
        savegame_path = game_session.save_path if hasattr(game_session, 'save_path') else None

        # Get empire theme
        empire_theme_id = empire.empire_theme_id if hasattr(empire, 'empire_theme_id') else None
        logger.debug(f"Creating WorkshopContext with empire_theme_id={empire_theme_id}")

        # PROJ-211: Pass registries explicitly (no fallback)
        # Create integrated context regardless of save_path
        return WorkshopContext.integrated(
            empire_id=empire.id,
            savegame_path=savegame_path,
            available_tech_ids=available_tech_ids,
            built_designs=empire.built_ship_designs if hasattr(empire, 'built_ship_designs') else set(),
            empire_theme_id=empire_theme_id,
            registries=self.registries,
        )

    def _handle_test_lab_action(self, action: str, **kwargs: Any) -> None:
        """Handle scene actions from TestLabScreen."""
        if action == "return_to_menu":
            self._switch_scene(GameState.MENU, self.menu_scene)
        elif action == "start_test_battle":
            self._switch_scene(GameState.BATTLE, self.battle_scene)

    def _handle_battle_setup_action(self, action: str, **kwargs: Any) -> None:
        """Handle scene actions from BattleSetupScreen."""
        self._router._handle_battle_setup_action(action, **kwargs)

    # ------------------------------------------------------------------
    # Run loop
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Main game loop."""
        self._loop.run()


def main() -> None:
    configure_logging()
    args = parse_args()
    game = Game(args)

    from game.core.registry import freeze_registry
    freeze_registry()

    try:
        game.run()
    except Exception as e:  # Intentional broad catch: top-level crash handler, logs and re-raises
        import traceback
        error_msg = traceback.format_exc()
        logger.error("CRITICAL CRASH CAUGHT:")
        logger.error(error_msg)
        with open(Paths.CRASH_LOG, "w") as f:
            f.write(error_msg)
        raise

    game.ctx.profiler.save_history()


if __name__ == "__main__":
    main()
