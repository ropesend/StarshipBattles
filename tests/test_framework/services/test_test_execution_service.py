"""
Unit tests for TestExecutionService.

Tests visual and headless test execution, progress callbacks, and error handling.
"""

import pytest
import time
from unittest.mock import Mock, patch, call
from test_framework.services.test_execution_service import TestExecutionService


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
        mock_battle_scene,
        sample_scenario_info,
        mock_test_scenario
    ):
        """Test successful visual test execution."""
        service = TestExecutionService()

        # Mock scenario class to return test scenario instance
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)

        # Mock runner methods
        service.runner.load_data_for_scenario = Mock()

        success = service.run_visual(sample_scenario_info, mock_battle_scene, mock_game)

        assert success is True
        mock_test_scenario.setup.assert_called_once_with(mock_battle_scene.engine)
        assert mock_battle_scene.test_mode is True
        assert mock_battle_scene.sim_paused is True
        assert mock_battle_scene.headless_mode is False
        assert mock_battle_scene.test_scenario is mock_test_scenario

    def test_run_visual_loads_data(
        self,
        mock_game,
        mock_battle_scene,
        sample_scenario_info,
        mock_test_scenario
    ):
        """Test that run_visual loads test data."""
        service = TestExecutionService()
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)
        service.runner.load_data_for_scenario = Mock()

        service.run_visual(sample_scenario_info, mock_battle_scene, mock_game)

        service.runner.load_data_for_scenario.assert_called_once_with(mock_test_scenario)

    def test_run_visual_clears_engine(
        self,
        mock_game,
        mock_battle_scene,
        sample_scenario_info,
        mock_test_scenario
    ):
        """Test that run_visual clears battle engine before setup."""
        service = TestExecutionService()
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)
        service.runner.load_data_for_scenario = Mock()

        service.run_visual(sample_scenario_info, mock_battle_scene, mock_game)

        mock_battle_scene.engine.start.assert_called_once_with([], [])

    def test_run_visual_fits_camera(
        self,
        mock_game,
        mock_battle_scene,
        sample_scenario_info,
        mock_test_scenario
    ):
        """Test that camera is fitted to ships."""
        service = TestExecutionService()
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)
        service.runner.load_data_for_scenario = Mock()

        # Add mock ships
        mock_ship1 = Mock()
        mock_ship2 = Mock()
        mock_battle_scene.engine.ships = [mock_ship1, mock_ship2]

        service.run_visual(sample_scenario_info, mock_battle_scene, mock_game)

        mock_battle_scene.camera.fit_objects.assert_called_once_with([mock_ship1, mock_ship2])

    def test_run_visual_switches_to_battle_state(
        self,
        mock_game,
        mock_battle_scene,
        sample_scenario_info,
        mock_test_scenario
    ):
        """Test that game state is switched to BATTLE."""
        service = TestExecutionService()
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)
        service.runner.load_data_for_scenario = Mock()

        with patch('test_framework.services.test_execution_service.GameState') as mock_game_state:
            service.run_visual(sample_scenario_info, mock_battle_scene, mock_game)

            assert mock_game.state == mock_game_state.BATTLE

    def test_run_visual_error_handling(
        self,
        mock_game,
        mock_battle_scene,
        sample_scenario_info
    ):
        """Test error handling in visual execution."""
        service = TestExecutionService()

        # Make scenario instantiation fail
        sample_scenario_info['class'] = Mock(side_effect=Exception("Test error"))

        success = service.run_visual(sample_scenario_info, mock_battle_scene, mock_game)

        assert success is False


class TestRunHeadless:
    """Test headless test execution."""

    def test_run_headless_success(
        self,
        mock_battle_engine,
        sample_scenario_info,
        mock_test_scenario
    ):
        """Test successful headless test execution."""
        service = TestExecutionService()
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)
        service.runner.load_data_for_scenario = Mock()
        service.runner._log_test_execution = Mock()

        # Make battle end after 100 ticks
        mock_battle_engine.is_battle_over = Mock(side_effect=[False] * 99 + [True])

        result = service.run_headless(sample_scenario_info, mock_battle_engine)

        assert result['passed'] is True
        assert result['error'] is None
        assert result['ticks_run'] == 100
        assert 'duration_real' in result
        mock_test_scenario.verify.assert_called_once_with(mock_battle_engine)

    def test_run_headless_runs_max_ticks(
        self,
        mock_battle_engine,
        sample_scenario_info,
        mock_test_scenario
    ):
        """Test that headless runs for max_ticks."""
        service = TestExecutionService()
        mock_test_scenario.max_ticks = 50
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)
        service.runner.load_data_for_scenario = Mock()
        service.runner._log_test_execution = Mock()

        result = service.run_headless(sample_scenario_info, mock_battle_engine)

        assert result['ticks_run'] == 50
        assert mock_battle_engine.update.call_count == 50

    def test_run_headless_calls_scenario_update(
        self,
        mock_battle_engine,
        sample_scenario_info,
        mock_test_scenario
    ):
        """Test that scenario.update() is called each tick."""
        service = TestExecutionService()
        mock_test_scenario.max_ticks = 10
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)
        service.runner.load_data_for_scenario = Mock()
        service.runner._log_test_execution = Mock()

        result = service.run_headless(sample_scenario_info, mock_battle_engine)

        assert mock_test_scenario.update.call_count == 10

    def test_run_headless_progress_callback(
        self,
        mock_battle_engine,
        sample_scenario_info,
        mock_test_scenario
    ):
        """Test progress callback is called."""
        service = TestExecutionService()
        mock_test_scenario.max_ticks = 250
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)
        service.runner.load_data_for_scenario = Mock()
        service.runner._log_test_execution = Mock()

        progress_callback = Mock()
        result = service.run_headless(
            sample_scenario_info,
            mock_battle_engine,
            on_progress=progress_callback
        )

        # Should be called every 100 ticks
        assert progress_callback.call_count == 2
        progress_callback.assert_any_call(100, 250)
        progress_callback.assert_any_call(200, 250)

    def test_run_headless_early_termination(
        self,
        mock_battle_engine,
        sample_scenario_info,
        mock_test_scenario
    ):
        """Test that battle ending early terminates simulation."""
        service = TestExecutionService()
        mock_test_scenario.max_ticks = 1000
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)
        service.runner.load_data_for_scenario = Mock()
        service.runner._log_test_execution = Mock()

        # Battle ends at tick 50
        mock_battle_engine.is_battle_over = Mock(side_effect=[False] * 49 + [True])

        result = service.run_headless(sample_scenario_info, mock_battle_engine)

        assert result['ticks_run'] == 50  # Should stop early

    def test_run_headless_stores_results(
        self,
        mock_battle_engine,
        sample_scenario_info,
        mock_test_scenario
    ):
        """Test that results are stored in scenario.results."""
        service = TestExecutionService()
        mock_test_scenario.max_ticks = 10
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)
        service.runner.load_data_for_scenario = Mock()
        service.runner._log_test_execution = Mock()

        result = service.run_headless(sample_scenario_info, mock_battle_engine)

        assert mock_test_scenario.results['ticks_run'] == 10
        assert 'duration_real' in mock_test_scenario.results
        assert mock_test_scenario.results['ticks'] == 10  # Alias

    def test_run_headless_logs_execution(
        self,
        mock_battle_engine,
        sample_scenario_info,
        mock_test_scenario
    ):
        """Test that execution is logged."""
        service = TestExecutionService()
        mock_test_scenario.max_ticks = 10
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)
        service.runner.load_data_for_scenario = Mock()
        service.runner._log_test_execution = Mock()

        result = service.run_headless(sample_scenario_info, mock_battle_engine)

        service.runner._log_test_execution.assert_called_once_with(mock_test_scenario, headless=True)

    def test_run_headless_clears_engine(
        self,
        mock_battle_engine,
        sample_scenario_info,
        mock_test_scenario
    ):
        """Test that engine is cleared before test."""
        service = TestExecutionService()
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)
        service.runner.load_data_for_scenario = Mock()
        service.runner._log_test_execution = Mock()

        result = service.run_headless(sample_scenario_info, mock_battle_engine)

        mock_battle_engine.start.assert_called_once_with([], [])

    def test_run_headless_loads_data(
        self,
        mock_battle_engine,
        sample_scenario_info,
        mock_test_scenario
    ):
        """Test that test data is loaded."""
        service = TestExecutionService()
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)
        service.runner.load_data_for_scenario = Mock()
        service.runner._log_test_execution = Mock()

        result = service.run_headless(sample_scenario_info, mock_battle_engine)

        service.runner.load_data_for_scenario.assert_called_once_with(mock_test_scenario)

    def test_run_headless_calls_setup(
        self,
        mock_battle_engine,
        sample_scenario_info,
        mock_test_scenario
    ):
        """Test that scenario.setup() is called."""
        service = TestExecutionService()
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)
        service.runner.load_data_for_scenario = Mock()
        service.runner._log_test_execution = Mock()

        result = service.run_headless(sample_scenario_info, mock_battle_engine)

        mock_test_scenario.setup.assert_called_once_with(mock_battle_engine)

    def test_run_headless_failed_test(
        self,
        mock_battle_engine,
        sample_scenario_info,
        mock_test_scenario
    ):
        """Test handling of failed test."""
        service = TestExecutionService()
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)
        service.runner.load_data_for_scenario = Mock()
        service.runner._log_test_execution = Mock()

        # Make test fail
        mock_test_scenario.verify = Mock(return_value=False)

        result = service.run_headless(sample_scenario_info, mock_battle_engine)

        assert result['passed'] is False
        assert result['error'] is None

    def test_run_headless_error_handling(
        self,
        mock_battle_engine,
        sample_scenario_info
    ):
        """Test error handling in headless execution."""
        service = TestExecutionService()

        # Make scenario instantiation fail
        sample_scenario_info['class'] = Mock(side_effect=Exception("Test error"))

        result = service.run_headless(sample_scenario_info, mock_battle_engine)

        assert result['passed'] is False
        assert result['error'] == "Test error"
        assert result['ticks_run'] == 0
        assert result['duration_real'] == 0

    def test_run_headless_measures_time(
        self,
        mock_battle_engine,
        sample_scenario_info,
        mock_test_scenario
    ):
        """Test that execution time is measured."""
        service = TestExecutionService()
        mock_test_scenario.max_ticks = 100
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)
        service.runner.load_data_for_scenario = Mock()
        service.runner._log_test_execution = Mock()

        start_time = time.time()
        result = service.run_headless(sample_scenario_info, mock_battle_engine)
        elapsed = time.time() - start_time

        assert result['duration_real'] > 0
        assert result['duration_real'] <= elapsed + 0.1  # Some tolerance

    def test_run_headless_returns_results_dict(
        self,
        mock_battle_engine,
        sample_scenario_info,
        mock_test_scenario
    ):
        """Test that result dict has all required keys."""
        service = TestExecutionService()
        sample_scenario_info['class'] = Mock(return_value=mock_test_scenario)
        service.runner.load_data_for_scenario = Mock()
        service.runner._log_test_execution = Mock()

        # Add some test results
        mock_test_scenario.results = {'damage_dealt': 150, 'hit_count': 10}

        result = service.run_headless(sample_scenario_info, mock_battle_engine)

        assert 'passed' in result
        assert 'results' in result
        assert 'ticks_run' in result
        assert 'duration_real' in result
        assert 'error' in result
        assert result['results']['damage_dealt'] == 150
        assert result['results']['hit_count'] == 10
