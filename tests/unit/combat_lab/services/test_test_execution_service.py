"""
Unit tests for TestExecutionService.

Tests visual and headless test execution, progress callbacks, and error handling.
"""

from unittest.mock import Mock, patch
from combat_lab.services.test_execution_service import TestExecutionService


class TestTestExecutionServiceInit:
    """Test TestExecutionService initialization."""

    def test_init(self):
        """Test service initialization."""
        service = TestExecutionService()

        assert service.runner is not None


class TestRunVisual:
    """Test visual test execution."""

    def test_run_visual_success(
        self,
        mock_game,
        mock_battle_screen,
        sample_scenario_info,
        mock_test_scenario
    ):
        """Test successful visual test execution.

        PROJ-269 Phase 6: dropped the `controller.config.mode == TEST`
        assertion since BattleMode is gone — `start_paused` and
        `test_scenario` carry the same intent.
        """
        service = TestExecutionService()

        # Mock scenario class to return test scenario instance
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)

        # Mock runner methods
        service.runner.load_data_for_scenario = Mock()

        success = service.run_visual(sample_scenario_info, mock_battle_screen, mock_game)

        assert success is True
        # PROJ-269 Phase 6: the spec-compiled visual path calls
        # `scenario.to_spec()` + `wire_ships()` + `custom_setup()`, NOT
        # `scenario.setup()`. Assert the new contract.
        mock_test_scenario.to_spec.assert_called_once()
        mock_test_scenario.wire_ships.assert_called_once()
        mock_test_scenario.custom_setup.assert_called_once()
        # start_battle should be called with a BattleController
        mock_battle_screen.start_battle.assert_called_once()
        controller = mock_battle_screen.start_battle.call_args[0][0]
        assert controller.config.start_paused is True
        assert controller.config.test_scenario is mock_test_scenario

    def test_run_visual_loads_data(
        self,
        mock_game,
        mock_battle_screen,
        sample_scenario_info,
        mock_test_scenario
    ):
        """Test that run_visual loads test data."""
        service = TestExecutionService()
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)
        service.runner.load_data_for_scenario = Mock()

        service.run_visual(sample_scenario_info, mock_battle_screen, mock_game)

        service.runner.load_data_for_scenario.assert_called_once_with(mock_test_scenario)

    def test_run_visual_uses_controller_engine(
        self,
        mock_game,
        mock_battle_screen,
        sample_scenario_info,
        mock_test_scenario
    ):
        """Test that run_visual creates a controller with its own engine."""
        service = TestExecutionService()
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)
        service.runner.load_data_for_scenario = Mock()

        service.run_visual(sample_scenario_info, mock_battle_screen, mock_game)

        # The controller creates its own engine; start_battle receives it
        mock_battle_screen.start_battle.assert_called_once()
        controller = mock_battle_screen.start_battle.call_args[0][0]
        assert controller.service.get_engine() is not None

    def test_run_visual_delegates_camera_to_start_battle(
        self,
        mock_game,
        mock_battle_screen,
        sample_scenario_info,
        mock_test_scenario
    ):
        """Test that camera fitting is handled by start_battle, not directly."""
        service = TestExecutionService()
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)
        service.runner.load_data_for_scenario = Mock()

        service.run_visual(sample_scenario_info, mock_battle_screen, mock_game)

        # Camera fitting is now internal to start_battle; just verify start_battle was called
        mock_battle_screen.start_battle.assert_called_once()

    def test_run_visual_switches_to_battle_state(
        self,
        mock_game,
        mock_battle_screen,
        sample_scenario_info,
        mock_test_scenario
    ):
        """Test that game state is switched to BATTLE."""
        service = TestExecutionService()
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)
        service.runner.load_data_for_scenario = Mock()

        # Import the actual GameState to check against
        from game.core.constants import GameState

        service.run_visual(sample_scenario_info, mock_battle_screen, mock_game)

        assert mock_game.state == GameState.BATTLE

    def test_run_visual_error_handling(
        self,
        mock_game,
        mock_battle_screen,
        sample_scenario_info
    ):
        """Test error handling in visual execution."""
        service = TestExecutionService()

        # Make scenario instantiation fail
        sample_scenario_info['class'] = Mock(side_effect=Exception("Test error"))

        success = service.run_visual(sample_scenario_info, mock_battle_screen, mock_game)

        assert success is False


def _fake_run_battle_factory(tick_count=10):
    """Build a fake `run_battle` callable for patching.

    The fake fires `pre_tick_loop_callback` once with a Mock engine, then
    invokes `per_tick_callback` `tick_count` times. Returns a Mock outcome.
    """
    def _fake(spec, *, ai_factory, ship_builder, headless=True,
              per_tick_callback=None, pre_tick_loop_callback=None):
        engine = Mock()
        engine.tick_counter = 0
        engine.projectiles = []
        if pre_tick_loop_callback is not None:
            pre_tick_loop_callback(engine)
        if per_tick_callback is not None:
            for i in range(tick_count):
                engine.tick_counter = i + 1
                per_tick_callback(engine)
        outcome = Mock()
        outcome.end_reason = Mock(value="tick_limit")
        outcome.duration_ticks = tick_count
        return outcome
    return _fake


class TestRunHeadless:
    """Test headless test execution — PROJ-270 Phase 1.1 contract.

    The new contract: `run_headless(scenario_info, on_progress=None)` compiles
    a spec via `scenario.to_spec(registries=None)` and drives the battle through
    `run_battle(spec, ...)`. It no longer accepts a `battle_engine` parameter
    and no longer calls `scenario.setup(engine)` or `battle_engine.start([], [])`.
    """

    def test_run_headless_compiles_spec(
        self,
        sample_scenario_info,
        mock_test_scenario,
    ):
        """`run_headless` calls `scenario.to_spec(registries=None)`."""
        service = TestExecutionService()
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)
        service.runner.load_data_for_scenario = Mock()
        service.runner.log_test_execution = Mock()

        with patch(
            'combat_lab.services.scenario_run_helper.run_battle',
            side_effect=_fake_run_battle_factory(tick_count=5),
        ):
            service.run_headless(sample_scenario_info)

        mock_test_scenario.to_spec.assert_called_once_with(registries=None)

    def test_run_headless_calls_before_run_battle(
        self,
        sample_scenario_info,
        mock_test_scenario,
    ):
        """`run_headless` fires the `before_run_battle` pre-hook."""
        service = TestExecutionService()
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)
        service.runner.load_data_for_scenario = Mock()
        service.runner.log_test_execution = Mock()

        with patch(
            'combat_lab.services.scenario_run_helper.run_battle',
            side_effect=_fake_run_battle_factory(tick_count=5),
        ):
            service.run_headless(sample_scenario_info)

        mock_test_scenario.before_run_battle.assert_called_once()

    def test_run_headless_drives_run_battle(
        self,
        sample_scenario_info,
        mock_test_scenario,
    ):
        """`run_headless` invokes `run_battle(spec, ...)` with the compiled spec."""
        service = TestExecutionService()
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)
        service.runner.load_data_for_scenario = Mock()
        service.runner.log_test_execution = Mock()

        with patch(
            'combat_lab.services.scenario_run_helper.run_battle',
            side_effect=_fake_run_battle_factory(tick_count=5),
        ) as mock_run_battle:
            service.run_headless(sample_scenario_info)

        mock_run_battle.assert_called_once()
        call_kwargs = mock_run_battle.call_args.kwargs
        # run_battle receives ai_factory + ship_builder; the spec is positional
        assert 'ai_factory' in call_kwargs
        assert 'ship_builder' in call_kwargs
        # Spec passed positionally is the one compiled by to_spec
        spec_arg = mock_run_battle.call_args.args[0]
        assert spec_arg is mock_test_scenario.to_spec.return_value

    def test_run_headless_does_not_call_scenario_setup(
        self,
        sample_scenario_info,
        mock_test_scenario,
    ):
        """`scenario.setup(engine)` is NOT called — the legacy entry is dead."""
        service = TestExecutionService()
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)
        service.runner.load_data_for_scenario = Mock()
        service.runner.log_test_execution = Mock()

        with patch(
            'combat_lab.services.scenario_run_helper.run_battle',
            side_effect=_fake_run_battle_factory(tick_count=5),
        ):
            service.run_headless(sample_scenario_info)

        mock_test_scenario.setup.assert_not_called()

    def test_run_headless_wires_ships_and_custom_setup_in_pre_tick_loop(
        self,
        sample_scenario_info,
        mock_test_scenario,
    ):
        """`pre_tick_loop_callback` invokes `wire_ships` + `custom_setup`."""
        service = TestExecutionService()
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)
        service.runner.load_data_for_scenario = Mock()
        service.runner.log_test_execution = Mock()

        with patch(
            'combat_lab.services.scenario_run_helper.run_battle',
            side_effect=_fake_run_battle_factory(tick_count=5),
        ):
            service.run_headless(sample_scenario_info)

        mock_test_scenario.wire_ships.assert_called_once()
        mock_test_scenario.custom_setup.assert_called_once()

    def test_run_headless_calls_scenario_update_per_tick(
        self,
        sample_scenario_info,
        mock_test_scenario,
    ):
        """`per_tick_callback` invokes `scenario.update(engine)` each tick."""
        service = TestExecutionService()
        mock_test_scenario.max_ticks = 10
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)
        service.runner.load_data_for_scenario = Mock()
        service.runner.log_test_execution = Mock()

        with patch(
            'combat_lab.services.scenario_run_helper.run_battle',
            side_effect=_fake_run_battle_factory(tick_count=10),
        ):
            service.run_headless(sample_scenario_info)

        assert mock_test_scenario.update.call_count == 10

    def test_run_headless_runs_validation(
        self,
        sample_scenario_info,
        mock_test_scenario,
    ):
        """`_run_validation` is called exactly once with the final engine.

        PROJ-270 Phase 1 keeps validator consuming engine; Phase 2 migrates it
        to `BattleOutcome`. This test locks Phase 1 behaviour — update when
        Phase 2 lands.
        """
        service = TestExecutionService()
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)
        service.runner.load_data_for_scenario = Mock()
        service.runner.log_test_execution = Mock()

        with patch(
            'combat_lab.services.scenario_run_helper.run_battle',
            side_effect=_fake_run_battle_factory(tick_count=5),
        ):
            service.run_headless(sample_scenario_info)

        mock_test_scenario._run_validation.assert_called_once()

    def test_run_headless_loads_data(
        self,
        sample_scenario_info,
        mock_test_scenario,
    ):
        """Scenario data is loaded before the spec is compiled."""
        service = TestExecutionService()
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)
        service.runner.load_data_for_scenario = Mock()
        service.runner.log_test_execution = Mock()

        with patch(
            'combat_lab.services.scenario_run_helper.run_battle',
            side_effect=_fake_run_battle_factory(tick_count=5),
        ):
            service.run_headless(sample_scenario_info)

        service.runner.load_data_for_scenario.assert_called_once_with(mock_test_scenario)

    def test_run_headless_logs_execution(
        self,
        sample_scenario_info,
        mock_test_scenario,
    ):
        """Execution is logged exactly once for UI/headless comparison."""
        service = TestExecutionService()
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)
        service.runner.load_data_for_scenario = Mock()
        service.runner.log_test_execution = Mock()

        with patch(
            'combat_lab.services.scenario_run_helper.run_battle',
            side_effect=_fake_run_battle_factory(tick_count=5),
        ):
            service.run_headless(sample_scenario_info)

        service.runner.log_test_execution.assert_called_once_with(
            mock_test_scenario, headless=True,
        )

    def test_run_headless_returns_results_dict(
        self,
        sample_scenario_info,
        mock_test_scenario,
    ):
        """Result dict carries passed/results/ticks_run/duration_real/error."""
        service = TestExecutionService()
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)
        service.runner.load_data_for_scenario = Mock()
        service.runner.log_test_execution = Mock()
        mock_test_scenario.results = {'damage_dealt': 150}

        with patch(
            'combat_lab.services.scenario_run_helper.run_battle',
            side_effect=_fake_run_battle_factory(tick_count=7),
        ):
            result = service.run_headless(sample_scenario_info)

        assert result['passed'] is True
        assert result['error'] is None
        assert result['ticks_run'] == 7
        assert 'duration_real' in result
        assert result['results']['damage_dealt'] == 150

    def test_run_headless_failed_validation(
        self,
        sample_scenario_info,
        mock_test_scenario,
    ):
        """Failing validation yields passed=False in the result dict."""
        service = TestExecutionService()
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)
        service.runner.load_data_for_scenario = Mock()
        service.runner.log_test_execution = Mock()
        failed_report = Mock()
        failed_report.passed = False
        mock_test_scenario._run_validation = Mock(return_value=failed_report)

        with patch(
            'combat_lab.services.scenario_run_helper.run_battle',
            side_effect=_fake_run_battle_factory(tick_count=5),
        ):
            result = service.run_headless(sample_scenario_info)

        assert result['passed'] is False
        assert result['error'] is None

    def test_run_headless_error_handling(
        self,
        sample_scenario_info,
    ):
        """Instantiation exception is captured in the result dict."""
        service = TestExecutionService()
        sample_scenario_info['class'] = Mock(side_effect=Exception("Test error"))

        result = service.run_headless(sample_scenario_info)

        assert result['passed'] is False
        assert result['error'] == "Test error"
        assert result['ticks_run'] == 0
        assert result['duration_real'] == 0

    def test_run_headless_progress_callback(
        self,
        sample_scenario_info,
        mock_test_scenario,
    ):
        """`on_progress(tick, max_ticks)` fires every 100 ticks."""
        service = TestExecutionService()
        mock_test_scenario.max_ticks = 250
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)
        service.runner.load_data_for_scenario = Mock()
        service.runner.log_test_execution = Mock()
        progress_callback = Mock()

        with patch(
            'combat_lab.services.scenario_run_helper.run_battle',
            side_effect=_fake_run_battle_factory(tick_count=250),
        ):
            service.run_headless(sample_scenario_info, on_progress=progress_callback)

        # Every 100 ticks → 2 calls (at tick 100 and tick 200)
        assert progress_callback.call_count == 2
