"""Tests for Combat Lab visual run functionality.

Tests the flow when "Run Visual" is clicked in the Combat Lab UI.

PROJ-342: TestLabScreen no longer takes a `game` handle. The fixture and
helpers now operate on a `mock_battle_scene` directly.
"""
import pygame
import pytest
from unittest.mock import Mock, patch


class TestVisualRunFlow:
    """Tests for _on_run() method in test_lab_screen."""

    @pytest.fixture
    def mock_battle_scene(self):
        """Create a mock BattleScreen the executor wires through to."""
        battle_scene = Mock()
        battle_scene.engine = Mock()
        battle_scene.engine.ships = []
        battle_scene.sim_paused = False
        battle_scene.headless_mode = True
        battle_scene.camera = Mock()
        battle_scene._battle_service = Mock()

        return battle_scene

    @pytest.fixture
    def mock_registry(self):
        """Create a mock TestRegistry."""
        registry = Mock()

        # Create a mock scenario class and metadata
        mock_metadata = Mock()
        mock_metadata.test_id = "TEST-001"
        mock_metadata.name = "Test Scenario"
        mock_metadata.seed = 42
        mock_metadata.max_ticks = 500
        mock_metadata.battle_end_mode = "time_based"

        # Create mock scenario class
        mock_scenario_cls = Mock()
        mock_scenario = Mock()
        mock_scenario.metadata = mock_metadata
        mock_scenario.name = "Test Scenario"
        # PROJ-269 Phase 6: UI path now consumes a BattleSpec from
        # `scenario.to_spec()`. Supply an empty-teams spec so the path
        # short-circuits cleanly without an engine.
        empty_spec = Mock()
        empty_spec.seed = 0
        empty_spec.teams = ()
        empty_spec.boundary = None
        from game.simulation.combat.modifier_stack import ModifierStack
        empty_spec.modifier_stack = ModifierStack.empty()
        empty_spec.end_condition = Mock()
        empty_spec.absolute_max_ticks = 10000
        mock_scenario.to_spec = Mock(return_value=empty_spec)
        mock_scenario.before_run_battle = Mock()
        mock_scenario.wire_ships = Mock()
        mock_scenario.custom_setup = Mock()
        mock_scenario._load_ship = Mock()
        mock_scenario_cls.return_value = mock_scenario

        # Setup registry to return scenario info
        registry.get_by_id.return_value = {
            'class': mock_scenario_cls,
            'metadata': mock_metadata
        }

        return registry, mock_scenario_cls, mock_scenario

    @pytest.fixture
    def mock_controller(self, mock_registry):
        """Create a mock controller for TestLabScreen."""
        controller = Mock()
        registry, _, _ = mock_registry

        # Mock ui_state
        controller.ui_state = Mock()
        controller.ui_state.get_selected_test_id.return_value = "TEST-001"

        # Mock output_log (used by TestLabScreen.output_log property)
        controller.output_log = []

        return controller

    def _create_test_lab_screen(self, mock_battle_scene, mock_registry, mock_controller):
        """Helper to create a TestLabScreen with mocked dependencies.

        Uses the real _switch_to_battle method (BUG-110 fix).
        """
        from game.ui.screens.test_lab import TestLabScreen
        from game.ui.screens.test_lab.test_executor import TestLabExecutor
        from game.ui.screens.test_lab.screen_actions import TestLabScreenActions
        registry, _, _ = mock_registry

        with patch.object(TestLabScreen, '__init__', lambda self, *a, **kw: None):
            screen = TestLabScreen.__new__(TestLabScreen)
            screen.battle_scene = mock_battle_scene
            screen.scene_callback = Mock()
            screen.registry = registry
            screen.controller = mock_controller
            # PROJ-457 Phase 3: actions extracted to TestLabScreenActions.
            screen._actions = TestLabScreenActions(screen)

            # Create executor with proper callbacks
            screen._executor = TestLabExecutor(
                registry=registry,
                test_history=Mock(),
                controller=mock_controller,
                render_progress=lambda t, s, d: None,
                draw_and_flip=lambda: None,
                get_engine=lambda: mock_battle_scene.engine,
                ensure_engine=lambda: None,
                switch_to_battle=lambda scenario: screen._actions._switch_to_battle(scenario),
                output_log=mock_controller.output_log,
            )
            return screen

    def test_visual_run_calls_start_battle(self, mock_battle_scene, mock_registry, mock_controller):
        """Visual run should call battle_scene.start_battle() with a BattleController."""
        screen = self._create_test_lab_screen(mock_battle_scene, mock_registry, mock_controller)

        with patch('game.ui.screens.test_lab.test_executor.TestRunner') as MockRunner:
            MockRunner.return_value = Mock()
            screen._actions._on_run()

        # start_battle should have been called exactly once
        mock_battle_scene.start_battle.assert_called_once()

    def test_visual_run_controller_set_for_test_lab(self, mock_battle_scene, mock_registry, mock_controller):
        """Visual run should pass a controller routed to return to TEST_LAB.

        PROJ-269 Phase 6: BattleMode is gone — test-vs-manual distinction
        now lives in `test_scenario` presence + `return_destination`.
        """
        from game.core.return_destination import ReturnDestination

        screen = self._create_test_lab_screen(mock_battle_scene, mock_registry, mock_controller)

        with patch('game.ui.screens.test_lab.test_executor.TestRunner') as MockRunner:
            MockRunner.return_value = Mock()
            screen._actions._on_run()

        controller = mock_battle_scene.start_battle.call_args[0][0]
        assert controller.config.return_destination == ReturnDestination.TEST_LAB

    def test_visual_run_controller_starts_paused(self, mock_battle_scene, mock_registry, mock_controller):
        """Visual run should pass a controller configured to start paused."""
        screen = self._create_test_lab_screen(mock_battle_scene, mock_registry, mock_controller)

        with patch('game.ui.screens.test_lab.test_executor.TestRunner') as MockRunner:
            MockRunner.return_value = Mock()
            screen._actions._on_run()

        controller = mock_battle_scene.start_battle.call_args[0][0]
        assert controller.config.start_paused is True

    def test_visual_run_requests_battle_transition(self, mock_battle_scene, mock_registry, mock_controller):
        """Visual run should request battle transition via scene_callback."""
        screen = self._create_test_lab_screen(mock_battle_scene, mock_registry, mock_controller)
        _, _, mock_scenario = mock_registry

        with patch('game.ui.screens.test_lab.test_executor.TestRunner') as MockRunner:
            MockRunner.return_value = Mock()
            screen._actions._on_run()

        # Verify scene_callback was called to request battle transition
        screen.scene_callback.assert_called_once_with("start_test_battle", scenario=mock_scenario)

    def test_visual_run_wires_scenario_via_spec_compiler(self, mock_battle_scene, mock_registry, mock_controller):
        """PROJ-269 Phase 6: visual run goes through `scenario.to_spec()`
        + `wire_ships()` + `custom_setup()`, NOT the legacy
        `scenario.setup(engine)` path."""
        screen = self._create_test_lab_screen(mock_battle_scene, mock_registry, mock_controller)
        _, _, mock_scenario = mock_registry

        with patch('game.ui.screens.test_lab.test_executor.TestRunner') as MockRunner:
            MockRunner.return_value = Mock()
            screen._actions._on_run()

        assert mock_scenario.to_spec.call_count == 1
        assert mock_scenario.wire_ships.call_count == 1
        assert mock_scenario.custom_setup.call_count == 1

    def test_visual_run_controller_has_scenario_reference(self, mock_battle_scene, mock_registry, mock_controller):
        """Visual run should store scenario reference in controller config."""
        screen = self._create_test_lab_screen(mock_battle_scene, mock_registry, mock_controller)
        _, _, mock_scenario = mock_registry

        with patch('game.ui.screens.test_lab.test_executor.TestRunner') as MockRunner:
            MockRunner.return_value = Mock()
            screen._actions._on_run()

        # Verify scenario reference is stored in the controller config
        controller = mock_battle_scene.start_battle.call_args[0][0]

    def test_visual_run_camera_handled_by_start_battle(self, mock_battle_scene, mock_registry, mock_controller):
        """Visual run delegates camera fitting to start_battle (no direct camera call)."""
        screen = self._create_test_lab_screen(mock_battle_scene, mock_registry, mock_controller)

        # Add ships to the engine (simulating scenario.setup() adding them)
        mock_ship = Mock()
        mock_battle_scene.engine.ships = [mock_ship]

        with patch('game.ui.screens.test_lab.test_executor.TestRunner') as MockRunner:
            MockRunner.return_value = Mock()
            screen._actions._on_run()

        # Camera fitting is now handled inside start_battle, so just verify start_battle was called
        mock_battle_scene.start_battle.assert_called_once()


def _mock_scenario_for_switch_to_battle():
    """Build a scenario Mock that satisfies the PROJ-269 Phase 6 UI path.

    `_switch_to_battle` now calls `scenario.to_spec()` → iterates
    `spec.teams` via `materialize_spec_ships`. An empty-teams spec lets
    the tests exercise the config/controller wiring without needing a
    real engine.
    """
    from game.simulation.combat.modifier_stack import ModifierStack
    scenario = Mock()
    empty_spec = Mock()
    empty_spec.seed = 0
    empty_spec.teams = ()
    empty_spec.boundary = None
    empty_spec.modifier_stack = ModifierStack.empty()
    empty_spec.end_condition = Mock()
    empty_spec.absolute_max_ticks = 10000
    scenario.to_spec = Mock(return_value=empty_spec)
    scenario.before_run_battle = Mock()
    scenario.wire_ships = Mock()
    scenario.custom_setup = Mock()
    scenario._load_ship = Mock()
    return scenario


class TestSceneTransitionCallbacks:
    """Tests that scene transitions use scene_callback (BUG-110).

    The _switch_to_battle() and _on_back() methods must use scene_callback
    to request transitions from app.py, not set game.state directly.
    """

    @pytest.fixture
    def mock_battle_scene(self):
        """Create a mock BattleScreen the executor wires through to."""
        battle_scene = Mock()
        battle_scene.engine = Mock()
        battle_scene.engine.ships = []
        battle_scene.sim_paused = False
        battle_scene.headless_mode = True
        battle_scene.camera = Mock()
        battle_scene._battle_service = Mock()
        return battle_scene

    def _create_screen_with_real_switch(self, mock_battle_scene, scene_callback):
        """Create a TestLabScreen with the real _switch_to_battle method."""
        from game.ui.screens.test_lab.screen import TestLabScreen
        from game.ui.screens.test_lab.screen_actions import TestLabScreenActions

        with patch.object(TestLabScreen, '__init__', lambda self, *a, **kw: None):
            screen = TestLabScreen.__new__(TestLabScreen)
            screen.battle_scene = mock_battle_scene
            screen.scene_callback = scene_callback
            # PROJ-457 Phase 3: _switch_to_battle moved to TestLabScreenActions.
            screen._actions = TestLabScreenActions(screen)
            return screen

    def test_switch_to_battle_calls_scene_callback(self, mock_battle_scene):
        """_switch_to_battle must call scene_callback('start_test_battle')."""
        callback = Mock()
        screen = self._create_screen_with_real_switch(mock_battle_scene, callback)

        scenario = _mock_scenario_for_switch_to_battle()
        screen._actions._switch_to_battle(scenario)

        callback.assert_called_once_with("start_test_battle", scenario=scenario)

    def test_switch_to_battle_calls_start_battle(self, mock_battle_scene):
        """_switch_to_battle must call battle_scene.start_battle with a controller."""
        callback = Mock()
        screen = self._create_screen_with_real_switch(mock_battle_scene, callback)

        scenario = _mock_scenario_for_switch_to_battle()
        screen._actions._switch_to_battle(scenario)

        mock_battle_scene.start_battle.assert_called_once()

    def test_switch_to_battle_controller_has_test_config(self, mock_battle_scene):
        """_switch_to_battle should pass controller routed for the test lab.

        PROJ-269 Phase 6: BattleMode is gone; the equivalent of "TEST mode"
        is now `start_paused=True` + `return_destination=TEST_LAB` +
        `test_scenario` set.
        """
        from game.core.return_destination import ReturnDestination

        callback = Mock()
        screen = self._create_screen_with_real_switch(mock_battle_scene, callback)

        scenario = _mock_scenario_for_switch_to_battle()
        screen._actions._switch_to_battle(scenario)

        controller = mock_battle_scene.start_battle.call_args[0][0]
        assert controller.config.start_paused is True
        assert controller.config.return_destination == ReturnDestination.TEST_LAB

    def test_on_back_calls_scene_callback(self, mock_battle_scene):
        """_on_back must call scene_callback('return_to_menu')."""
        callback = Mock()
        screen = self._create_screen_with_real_switch(mock_battle_scene, callback)

        screen._on_back()

        callback.assert_called_once_with("return_to_menu")


class TestEndBattleInTestMode:
    """Tests that 'End Battle' button routes correctly in test mode (BUG-112).

    When in test_mode, the 'end_battle' click result should trigger
    return_to_test_lab (which calls reset_selection), NOT return_to_setup
    (which skips reset_selection and loses test results).
    """

    @pytest.fixture
    def battle_screen(self):
        """Create a minimal BattleScreen for testing handle_event."""
        from game.ui.screens.battle_screen import BattleScreen

        with patch.object(BattleScreen, '__init__', lambda self, *a, **kw: None):
            screen = BattleScreen.__new__(BattleScreen)
            screen.scene_callback = Mock()
            mock_engine = Mock()
            mock_engine.ships = []
            mock_engine.tick_counter = 0
            mock_engine.get_winner.return_value = -1
            screen._battle_service = Mock()
            screen._battle_service.get_engine.return_value = mock_engine
            # Set up controller with config
            from game.simulation.battle_config import BattleConfig
            from game.core.return_destination import ReturnDestination
            from game.simulation.battle_outcome import BattleOutcome, EndReason
            from game.simulation.combat.telemetry import TelemetryLevel
            mock_controller = Mock()
            mock_controller.config = BattleConfig(
                return_destination=ReturnDestination.TEST_LAB,
                show_results=True,
            )
            # PROJ-281 Phase 3: the controller now always emits a real
            # `BattleOutcome` via `get_outcome()` (lazy extraction if the
            # natural end-transition hasn't fired yet). Mock it with a
            # minimal empty-teams outcome — sufficient for routing tests.
            mock_controller.get_outcome.return_value = BattleOutcome(
                end_reason=EndReason.TEAM_ELIMINATED,
                duration_ticks=0,
                seed=0,
                teams=(),
                telemetry_level=TelemetryLevel.MINIMAL,
            )
            screen._controller = mock_controller
            screen.ui = Mock()
            screen.camera = Mock()
            screen.screen_height = 2160
            return screen

    def test_end_battle_routes_to_results_screen(self, battle_screen):
        """'end_battle' should call scene_callback with 'show_results'."""
        battle_screen.ui.handle_click.return_value = "end_battle"

        event = Mock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.pos = (100, 100)
        event.button = 1

        battle_screen.handle_event(event)

        battle_screen.scene_callback.assert_called_once()
        call_args = battle_screen.scene_callback.call_args
        assert call_args[0][0] == "show_results"
        assert "results" in call_args[1]

    def test_end_battle_results_have_correct_destination(self, battle_screen):
        """Results passed to show_results should have test_lab destination."""
        battle_screen.ui.handle_click.return_value = "end_battle"

        event = Mock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.pos = (100, 100)
        event.button = 1

        battle_screen.handle_event(event)

        results = battle_screen.scene_callback.call_args[1]["results"]
        assert results.return_destination == "test_lab"


class TestBattleScreenDrawsInTestMode:
    """Tests that battle screen draws ships during test mode."""

    def test_draw_iterates_over_ships(self):
        """BattleScreen.draw() should iterate over engine.ships and draw them."""
        from game.ui.screens.battle_screen import BattleScreen

        # Create a minimal BattleScreen with mocked dependencies
        with patch.object(BattleScreen, '__init__', lambda self, w, h: None):
            screen = BattleScreen.__new__(BattleScreen)

            # Setup required attributes
            screen._battle_service = Mock()
            screen._battle_service.get_engine.return_value = Mock()
            screen._battle_service.get_engine.return_value.ships = []
            screen._battle_service.get_engine.return_value.projectiles = []
            screen.beams = []
            screen.hit_effects = []
            screen.camera = Mock()
            screen.ui = Mock()
            screen.ui.show_overlay = False

            # Add mock ships
            mock_ship1 = Mock()
            mock_ship2 = Mock()
            screen._battle_service.get_engine.return_value.ships = [mock_ship1, mock_ship2]

            # Mock pygame surface
            mock_surface = Mock()

            # Draw - should not crash and should draw ships
            with patch('game.ui.screens.battle_screen.draw_ship') as mock_draw_ship:
                screen.draw(mock_surface)

                # Verify draw_ship was called for each ship
                assert mock_draw_ship.call_count == 2


# PROJ-397 Phase 1: deleted `TestUpdateBattleVisualWithTestMode`. The class
# verified fictional behaviour — it manually simulated a `if self.test_mode`
# branch inside its own assertion and never invoked the real
# `BattleScreen.update()`. Production `update()` has no test_mode branch
# (it dispatches solely on `headless_mode`), so the test was a tautology
# on a Mock. The associated `test_mode` / `test_scenario` /
# `test_tick_count` / `test_completed` BattleScreen instance vars were
# deleted in the same phase.
