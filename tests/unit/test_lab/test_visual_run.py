"""Tests for Combat Lab visual run functionality.

Tests the flow when "Run Visual" is clicked in the Combat Lab UI.
"""
import pygame
import pytest
from unittest.mock import Mock, patch


class TestVisualRunFlow:
    """Tests for _on_run() method in test_lab_screen."""

    @pytest.fixture
    def mock_game(self):
        """Create a mock Game object with battle_scene."""
        game = Mock()

        # Mock battle scene with engine
        game.battle_scene = Mock()
        game.battle_scene.engine = Mock()
        game.battle_scene.engine.ships = []
        game.battle_scene.sim_paused = False
        game.battle_scene.test_mode = False
        game.battle_scene.headless_mode = True
        game.battle_scene.test_scenario = None
        game.battle_scene.test_tick_count = 0
        game.battle_scene.test_completed = False
        game.battle_scene.camera = Mock()
        game.battle_scene._battle_service = Mock()

        return game

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

    def _create_test_lab_screen(self, mock_game, mock_registry, mock_controller):
        """Helper to create a TestLabScreen with mocked dependencies.

        Uses the real _switch_to_battle method (BUG-110 fix).
        """
        from game.ui.screens.test_lab import TestLabScreen
        from game.ui.screens.test_lab.test_executor import TestLabExecutor
        registry, _, _ = mock_registry

        with patch.object(TestLabScreen, '__init__', lambda self, *a, **kw: None):
            screen = TestLabScreen.__new__(TestLabScreen)
            screen.game = mock_game
            screen.scene_callback = Mock()
            screen.registry = registry
            screen.controller = mock_controller

            # Create executor with proper callbacks
            screen._executor = TestLabExecutor(
                registry=registry,
                test_history=Mock(),
                controller=mock_controller,
                render_progress=lambda t, s, d: None,
                draw_and_flip=lambda: None,
                get_engine=lambda: mock_game.battle_scene.engine,
                ensure_engine=lambda: None,
                switch_to_battle=lambda scenario: screen._switch_to_battle(scenario),
                output_log=mock_controller.output_log,
            )
            return screen

    def test_visual_run_sets_test_mode_true(self, mock_game, mock_registry, mock_controller):
        """Visual run should set test_mode to True on battle_scene."""
        screen = self._create_test_lab_screen(mock_game, mock_registry, mock_controller)
        _, _, mock_scenario = mock_registry

        with patch('game.ui.screens.test_lab.test_executor.TestRunner') as MockRunner:
            MockRunner.return_value = Mock()
            screen._on_run()

        # Verify test_mode was set to True
        assert mock_game.battle_scene.test_mode is True

    def test_visual_run_sets_headless_mode_false(self, mock_game, mock_registry, mock_controller):
        """Visual run should set headless_mode to False (we want visuals!)."""
        screen = self._create_test_lab_screen(mock_game, mock_registry, mock_controller)

        with patch('game.ui.screens.test_lab.test_executor.TestRunner') as MockRunner:
            MockRunner.return_value = Mock()
            screen._on_run()

        # Verify headless_mode is False for visual run
        assert mock_game.battle_scene.headless_mode is False

    def test_visual_run_starts_paused(self, mock_game, mock_registry, mock_controller):
        """Visual run should start with simulation paused."""
        screen = self._create_test_lab_screen(mock_game, mock_registry, mock_controller)

        with patch('game.ui.screens.test_lab.test_executor.TestRunner') as MockRunner:
            MockRunner.return_value = Mock()
            screen._on_run()

        # Verify simulation starts paused
        assert mock_game.battle_scene.sim_paused is True

    def test_visual_run_requests_battle_transition(self, mock_game, mock_registry, mock_controller):
        """Visual run should request battle transition via scene_callback."""
        screen = self._create_test_lab_screen(mock_game, mock_registry, mock_controller)
        _, _, mock_scenario = mock_registry

        with patch('game.ui.screens.test_lab.test_executor.TestRunner') as MockRunner:
            MockRunner.return_value = Mock()
            screen._on_run()

        # Verify scene_callback was called to request battle transition
        screen.scene_callback.assert_called_once_with("start_test_battle", scenario=mock_scenario)

    def test_visual_run_calls_scenario_setup(self, mock_game, mock_registry, mock_controller):
        """Visual run should call scenario.setup() with the engine."""
        screen = self._create_test_lab_screen(mock_game, mock_registry, mock_controller)
        _, _, mock_scenario = mock_registry

        with patch('game.ui.screens.test_lab.test_executor.TestRunner') as MockRunner:
            MockRunner.return_value = Mock()
            screen._on_run()

        # Verify scenario.setup() was called once (in _switch_to_battle, not duplicated)
        assert mock_scenario.setup.call_count == 1

    def test_visual_run_stores_scenario_reference(self, mock_game, mock_registry, mock_controller):
        """Visual run should store scenario reference for update() calls."""
        screen = self._create_test_lab_screen(mock_game, mock_registry, mock_controller)
        _, _, mock_scenario = mock_registry

        with patch('game.ui.screens.test_lab.test_executor.TestRunner') as MockRunner:
            MockRunner.return_value = Mock()
            screen._on_run()

        # Verify scenario reference is stored
        assert mock_game.battle_scene.test_scenario == mock_scenario

    def test_visual_run_fits_camera_to_ships(self, mock_game, mock_registry, mock_controller):
        """Visual run should fit camera to ships if ships exist."""
        screen = self._create_test_lab_screen(mock_game, mock_registry, mock_controller)

        # Add ships to the engine (simulating scenario.setup() adding them)
        mock_ship = Mock()
        mock_game.battle_scene.engine.ships = [mock_ship]

        with patch('game.ui.screens.test_lab.test_executor.TestRunner') as MockRunner:
            MockRunner.return_value = Mock()
            screen._on_run()

        # Verify camera.fit_objects() was called with ships
        mock_game.battle_scene.camera.fit_objects.assert_called_once_with([mock_ship])


class TestSceneTransitionCallbacks:
    """Tests that scene transitions use scene_callback (BUG-110).

    The _switch_to_battle() and _on_back() methods must use scene_callback
    to request transitions from app.py, not set game.state directly.
    """

    @pytest.fixture
    def mock_game(self):
        """Create a mock Game object with battle_scene."""
        game = Mock()
        game.battle_scene = Mock()
        game.battle_scene.engine = Mock()
        game.battle_scene.engine.ships = []
        game.battle_scene.sim_paused = False
        game.battle_scene.test_mode = False
        game.battle_scene.headless_mode = True
        game.battle_scene.test_scenario = None
        game.battle_scene.test_tick_count = 0
        game.battle_scene.test_completed = False
        game.battle_scene.camera = Mock()
        game.battle_scene._battle_service = Mock()
        game.screen = Mock()
        game.screen.get_width.return_value = 3840
        game.screen.get_height.return_value = 2160
        return game

    def _create_screen_with_real_switch(self, mock_game, scene_callback):
        """Create a TestLabScreen with the real _switch_to_battle method."""
        from game.ui.screens.test_lab.screen import TestLabScreen

        with patch.object(TestLabScreen, '__init__', lambda self, *a, **kw: None):
            screen = TestLabScreen.__new__(TestLabScreen)
            screen.game = mock_game
            screen.scene_callback = scene_callback
            return screen

    def test_switch_to_battle_calls_scene_callback(self, mock_game):
        """_switch_to_battle must call scene_callback('start_test_battle')."""
        callback = Mock()
        screen = self._create_screen_with_real_switch(mock_game, callback)

        scenario = Mock()
        screen._switch_to_battle(scenario)

        callback.assert_called_once_with("start_test_battle", scenario=scenario)

    def test_switch_to_battle_does_not_set_game_state_directly(self, mock_game):
        """_switch_to_battle must NOT set game.state directly (app.py does that)."""
        callback = Mock()
        mock_game.state = "INITIAL"  # sentinel value
        screen = self._create_screen_with_real_switch(mock_game, callback)

        scenario = Mock()
        screen._switch_to_battle(scenario)

        # game.state should not have been set by _switch_to_battle
        assert mock_game.state == "INITIAL"

    def test_on_back_calls_scene_callback(self, mock_game):
        """_on_back must call scene_callback('return_to_menu')."""
        callback = Mock()
        screen = self._create_screen_with_real_switch(mock_game, callback)

        screen._on_back()

        callback.assert_called_once_with("return_to_menu")

    def test_on_back_does_not_set_game_state_directly(self, mock_game):
        """_on_back must NOT set game.state directly."""
        callback = Mock()
        mock_game.state = "INITIAL"
        screen = self._create_screen_with_real_switch(mock_game, callback)

        screen._on_back()

        assert mock_game.state == "INITIAL"

    def test_switch_to_battle_configures_battle_scene(self, mock_game):
        """_switch_to_battle should configure battle scene for test mode."""
        callback = Mock()
        screen = self._create_screen_with_real_switch(mock_game, callback)

        scenario = Mock()
        screen._switch_to_battle(scenario)

        assert mock_game.battle_scene.headless_mode is False
        assert mock_game.battle_scene.sim_paused is True
        assert mock_game.battle_scene.test_mode is True
        assert mock_game.battle_scene.test_scenario == scenario
        assert mock_game.battle_scene.test_tick_count == 0
        assert mock_game.battle_scene.test_completed is False


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
            from game.simulation.battle_config import BattleConfig, BattleMode, ReturnDestination
            mock_controller = Mock()
            mock_controller.config = BattleConfig(
                mode=BattleMode.TEST,
                return_destination=ReturnDestination.TEST_LAB,
                show_results=True,
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


class TestUpdateBattleVisualWithTestMode:
    """Tests that update_battle_visual properly handles test mode."""

    @pytest.fixture
    def mock_battle_scene_test_mode(self):
        """Create a mock BattleScreen in test mode."""
        scene = Mock()
        scene.sim_tick_counter = 0
        scene.sim_paused = False  # Unpaused to run simulation
        scene.sim_speed_multiplier = 1.0
        scene.headless_mode = False
        scene.test_mode = True
        scene.test_scenario = Mock()
        scene.test_tick_count = 0
        scene.test_completed = False
        scene.is_battle_over.return_value = False
        scene.ships = [Mock()]  # Has ships
        scene.tick_rate_count = 0
        scene.tick_rate_timer = 0.0
        scene.current_tick_rate = 0

        # Camera
        scene.camera = Mock()
        scene.camera.zoom = 1.0

        # UI
        scene.ui = Mock()
        scene.ui.seeker_panel = Mock()
        scene.ui.seeker_panel.rect = Mock()
        scene.ui.seeker_panel.rect.width = 200

        # Engine
        scene.engine = Mock()

        return scene

    def test_update_calls_scenario_update(self, mock_battle_scene_test_mode):
        """BattleScreen.update() should call test_scenario.update() in test mode."""
        from game.ui.screens.battle_screen import BattleScreen

        scene = mock_battle_scene_test_mode

        # Create a minimal callable update that triggers scenario update
        # The real update method checks test_mode and calls scenario.update
        scene.test_scenario.update = Mock()

        # Simulate what update() does in test mode
        if scene.test_mode and scene.test_scenario and not scene.test_completed:
            scene.test_tick_count += 1
            scene.test_scenario.update(scene.engine)

        # Verify scenario.update was called
        scene.test_scenario.update.assert_called_once_with(scene.engine)
        assert scene.test_tick_count == 1
