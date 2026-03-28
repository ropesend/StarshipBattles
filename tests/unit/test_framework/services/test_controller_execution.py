"""
Unit tests for TestLabUIController - execution, metadata updates, and queries.

PROJ-48: Split from test_test_lab_controller.py
"""

import pytest
from pathlib import Path
from unittest.mock import Mock
from test_framework.services.test_lab_controller import TestLabUIController
from tests.unit.test_framework.services.conftest import create_test_metadata


class TestHandleRunHeadless:
    """Test headless test execution handling."""

    def test_handle_run_headless_success(
        self,
        mock_game,
        mock_test_registry,
        mock_test_history,
        sample_scenario_info
    ):
        """Test successful headless test run."""
        mock_test_registry.get_by_id = Mock(return_value=sample_scenario_info)
        controller = TestLabUIController(mock_game, mock_test_registry, mock_test_history)
        controller.ui_state.select_test("TEST-001")
        controller.test_execution.run_headless = Mock(return_value={
            'passed': True,
            'results': {'damage_dealt': 150},
            'ticks_run': 500,
            'duration_real': 0.5,
            'error': None
        })

        result = controller.handle_run_headless()

        assert result['passed'] is True
        assert any("PASSED" in msg for msg in controller.output_log)

    def test_handle_run_headless_failed_test(
        self,
        mock_game,
        mock_test_registry,
        mock_test_history,
        sample_scenario_info
    ):
        """Test headless run with failed test."""
        mock_test_registry.get_by_id = Mock(return_value=sample_scenario_info)
        controller = TestLabUIController(mock_game, mock_test_registry, mock_test_history)
        controller.ui_state.select_test("TEST-001")
        controller.test_execution.run_headless = Mock(return_value={
            'passed': False,
            'results': {'damage_dealt': 0},
            'ticks_run': 500,
            'duration_real': 0.5,
            'error': None
        })

        result = controller.handle_run_headless()

        assert result['passed'] is False
        assert any("FAILED" in msg for msg in controller.output_log)

    def test_handle_run_headless_no_test_selected(
        self,
        mock_game,
        mock_test_registry,
        mock_test_history
    ):
        """Test headless run with no test selected."""
        controller = TestLabUIController(mock_game, mock_test_registry, mock_test_history)

        controller.handle_run_headless()

        assert any("No test selected" in msg for msg in controller.output_log)

    def test_handle_run_headless_test_not_found(
        self,
        mock_game,
        mock_test_registry,
        mock_test_history
    ):
        """Test headless run with invalid test ID."""
        mock_test_registry.get_by_id = Mock(return_value=None)
        controller = TestLabUIController(mock_game, mock_test_registry, mock_test_history)
        controller.ui_state.select_test("INVALID")

        controller.handle_run_headless()

        assert any("not found" in msg for msg in controller.output_log)

    def test_handle_run_headless_with_error(
        self,
        mock_game,
        mock_test_registry,
        mock_test_history,
        sample_scenario_info
    ):
        """Test headless run with error."""
        mock_test_registry.get_by_id = Mock(return_value=sample_scenario_info)
        controller = TestLabUIController(mock_game, mock_test_registry, mock_test_history)
        controller.ui_state.select_test("TEST-001")
        controller.test_execution.run_headless = Mock(return_value={
            'passed': False,
            'results': {},
            'ticks_run': 0,
            'duration_real': 0,
            'error': "Test error"
        })

        result = controller.handle_run_headless()

        assert any("ERROR" in msg for msg in controller.output_log)

    def test_handle_run_headless_progress_callback(
        self,
        mock_game,
        mock_test_registry,
        mock_test_history,
        sample_scenario_info
    ):
        """Test headless run with progress callback."""
        mock_test_registry.get_by_id = Mock(return_value=sample_scenario_info)
        controller = TestLabUIController(mock_game, mock_test_registry, mock_test_history)
        controller.ui_state.select_test("TEST-001")

        progress_callback = Mock()
        controller.test_execution.run_headless = Mock(return_value={
            'passed': True,
            'results': {},
            'ticks_run': 500,
            'duration_real': 0.5,
            'error': None
        })

        controller.handle_run_headless(on_progress=progress_callback)

        # Verify progress callback was passed through
        controller.test_execution.run_headless.assert_called_once()
        call_kwargs = controller.test_execution.run_headless.call_args[1]
        assert 'on_progress' in call_kwargs

    def test_handle_run_headless_updates_ui_state(
        self,
        mock_game,
        mock_test_registry,
        mock_test_history,
        sample_scenario_info
    ):
        """Test that headless running state is managed."""
        mock_test_registry.get_by_id = Mock(return_value=sample_scenario_info)
        controller = TestLabUIController(mock_game, mock_test_registry, mock_test_history)
        controller.ui_state.select_test("TEST-001")

        running_states = []

        def capture_state(*args, **kwargs):
            running_states.append(controller.ui_state.is_headless_running())
            return {
                'passed': True,
                'results': {},
                'ticks_run': 500,
                'duration_real': 0.5,
                'error': None
            }

        controller.test_execution.run_headless = capture_state

        controller.handle_run_headless()

        # Should be True during execution, False after
        assert running_states[0] is True
        assert controller.ui_state.is_headless_running() is False

    def test_handle_run_headless_adds_to_history(
        self,
        mock_game,
        mock_test_registry,
        mock_test_history,
        sample_scenario_info
    ):
        """Test that results are added to history."""
        mock_test_registry.get_by_id = Mock(return_value=sample_scenario_info)
        controller = TestLabUIController(mock_game, mock_test_registry, mock_test_history)
        controller.ui_state.select_test("TEST-001")
        controller.test_results.add_run = Mock()

        test_results = {'damage_dealt': 150}
        controller.test_execution.run_headless = Mock(return_value={
            'passed': True,
            'results': test_results,
            'ticks_run': 500,
            'duration_real': 0.5,
            'error': None
        })

        controller.handle_run_headless()

        controller.test_results.add_run.assert_called_once_with(
            "TEST-001",
            test_results,
            update_registry=True
        )


class TestHandleUpdateExpectedValues:
    """Test update expected values handling."""

    def test_handle_update_expected_values_success(
        self,
        mock_game,
        mock_test_registry,
        mock_test_history,
        sample_scenario_info
    ):
        """Test collecting validation failures."""
        sample_scenario_info['last_run_results'] = {
            'validation': {
                'checks': [
                    {'phase': 'data', 'name': 'Test', 'expected': 1, 'actual': 2, 'passed': False, 'detail': ''}
                ]
            }
        }
        mock_test_registry.get_by_id = Mock(return_value=sample_scenario_info)
        controller = TestLabUIController(mock_game, mock_test_registry, mock_test_history)
        controller.ui_state.select_test("TEST-001")

        changes = controller.handle_update_expected_values()

        assert len(changes) == 1
        assert changes[0]['old_value'] == 1
        assert changes[0]['new_value'] == 2

    def test_handle_update_expected_values_no_test_selected(
        self,
        mock_game,
        mock_test_registry,
        mock_test_history
    ):
        """Test update with no test selected."""
        controller = TestLabUIController(mock_game, mock_test_registry, mock_test_history)

        changes = controller.handle_update_expected_values()

        assert changes is None

    def test_handle_update_expected_values_test_not_found(
        self,
        mock_game,
        mock_test_registry,
        mock_test_history
    ):
        """Test update with invalid test ID."""
        mock_test_registry.get_by_id = Mock(return_value=None)
        controller = TestLabUIController(mock_game, mock_test_registry, mock_test_history)
        controller.ui_state.select_test("INVALID")

        changes = controller.handle_update_expected_values()

        assert changes is None

    def test_handle_update_expected_values_no_results(
        self,
        mock_game,
        mock_test_registry,
        mock_test_history,
        sample_scenario_info
    ):
        """Test update with no test results."""
        sample_scenario_info['last_run_results'] = None
        mock_test_registry.get_by_id = Mock(return_value=sample_scenario_info)
        controller = TestLabUIController(mock_game, mock_test_registry, mock_test_history)
        controller.ui_state.select_test("TEST-001")

        changes = controller.handle_update_expected_values()

        assert changes is None


class TestApplyMetadataUpdates:
    """Test applying metadata updates."""

    def test_apply_metadata_updates_success(
        self,
        mock_game,
        mock_test_registry,
        mock_test_history,
        sample_scenario_info,
        tmp_path
    ):
        """Test successful metadata updates."""
        scenario_file = tmp_path / "test.py"
        scenario_file.write_text("# test")
        sample_scenario_info['file'] = str(scenario_file)

        mock_test_registry.get_by_id = Mock(return_value=sample_scenario_info)
        controller = TestLabUIController(mock_game, mock_test_registry, mock_test_history)
        controller.ui_state.select_test("TEST-001")

        changes = [{'field': 'Test', 'old_value': 1, 'new_value': 2}]
        success, error = controller.apply_metadata_updates(changes)

        assert success is True
        assert error is None
        mock_test_registry.refresh.assert_called_once()

    def test_apply_metadata_updates_no_test_selected(
        self,
        mock_game,
        mock_test_registry,
        mock_test_history
    ):
        """Test update with no test selected."""
        controller = TestLabUIController(mock_game, mock_test_registry, mock_test_history)

        success, error = controller.apply_metadata_updates([])

        assert success is False
        assert error == "No test selected"

    def test_apply_metadata_updates_test_not_found(
        self,
        mock_game,
        mock_test_registry,
        mock_test_history
    ):
        """Test update with invalid test ID."""
        mock_test_registry.get_by_id = Mock(return_value=None)
        controller = TestLabUIController(mock_game, mock_test_registry, mock_test_history)
        controller.ui_state.select_test("INVALID")

        success, error = controller.apply_metadata_updates([])

        assert success is False
        assert error == "Test not found"

    def test_apply_metadata_updates_refreshes_registry(
        self,
        mock_game,
        mock_test_registry,
        mock_test_history,
        sample_scenario_info,
        tmp_path
    ):
        """Test that registry is refreshed after updates."""
        scenario_file = tmp_path / "test.py"
        scenario_file.write_text("# test")
        sample_scenario_info['file'] = str(scenario_file)

        mock_test_registry.get_by_id = Mock(return_value=sample_scenario_info)
        mock_test_registry.get_all_scenarios = Mock(return_value={'TEST-001': sample_scenario_info})
        controller = TestLabUIController(mock_game, mock_test_registry, mock_test_history)
        controller.ui_state.select_test("TEST-001")

        changes = [{'field': 'Test', 'old_value': 1, 'new_value': 2}]
        controller.apply_metadata_updates(changes)

        mock_test_registry.refresh.assert_called_once()
        # all_scenarios should be reloaded
        assert controller.all_scenarios == {'TEST-001': sample_scenario_info}


class TestGetFilteredScenarios:
    """Test scenario filtering."""

    def test_get_filtered_scenarios_all(
        self,
        mock_game,
        mock_test_registry,
        mock_test_history
    ):
        """Test getting all scenarios."""
        # Need proper scenario dicts for validation to work
        metadata1 = create_test_metadata(test_id="TEST-001", name="Test 1")
        metadata2 = create_test_metadata(test_id="TEST-002", name="Test 2")
        all_scenarios = {
            'TEST-001': {'metadata': metadata1, 'class': Mock()},
            'TEST-002': {'metadata': metadata2, 'class': Mock()}
        }
        mock_test_registry.get_all_scenarios = Mock(return_value=all_scenarios)
        controller = TestLabUIController(mock_game, mock_test_registry, mock_test_history)

        scenarios = controller.get_filtered_scenarios(category=None)

        assert scenarios == all_scenarios

    def test_get_filtered_scenarios_by_category(
        self,
        mock_game,
        mock_test_registry,
        mock_test_history
    ):
        """Test filtering scenarios by category."""
        metadata1 = create_test_metadata(
            test_id="TEST-001",
            name="Test 1",
            category="Beam Weapons"
        )
        metadata2 = create_test_metadata(
            test_id="TEST-002",
            name="Test 2",
            category="Seeker Weapons"
        )

        all_scenarios = {
            'TEST-001': {'metadata': metadata1},
            'TEST-002': {'metadata': metadata2}
        }
        mock_test_registry.get_all_scenarios = Mock(return_value=all_scenarios)
        controller = TestLabUIController(mock_game, mock_test_registry, mock_test_history)

        scenarios = controller.get_filtered_scenarios(category="Beam Weapons")

        assert len(scenarios) == 1
        assert 'TEST-001' in scenarios
        assert 'TEST-002' not in scenarios


class TestGetShipInfo:
    """Test ship info retrieval."""

    def test_get_ship_info_success(
        self,
        mock_game,
        mock_test_registry,
        mock_test_history,
        sample_scenario_info
    ):
        """Test getting ship info for test."""
        mock_test_registry.get_by_id = Mock(return_value=sample_scenario_info)
        controller = TestLabUIController(mock_game, mock_test_registry, mock_test_history)
        controller.scenario_data.extract_ships_from_scenario = Mock(return_value=[
            {'role': 'Attacker', 'filename': 'test.json'}
        ])

        ships = controller.get_ship_info("TEST-001")

        assert len(ships) == 1
        assert ships[0]['role'] == 'Attacker'

    def test_get_ship_info_test_not_found(
        self,
        mock_game,
        mock_test_registry,
        mock_test_history
    ):
        """Test getting ship info for invalid test."""
        mock_test_registry.get_by_id = Mock(return_value=None)
        controller = TestLabUIController(mock_game, mock_test_registry, mock_test_history)

        ships = controller.get_ship_info("INVALID")

        assert ships == []


class TestGetComponentData:
    """Test component data retrieval."""

    def test_get_component_data_success(
        self,
        mock_game,
        mock_test_registry,
        mock_test_history,
        sample_component_data
    ):
        """Test getting component data."""
        controller = TestLabUIController(mock_game, mock_test_registry, mock_test_history)
        controller.scenario_data.load_component_data = Mock(return_value=sample_component_data)

        component = controller.get_component_data("test_beam_low_acc_1dmg")

        assert component == sample_component_data

    def test_get_component_data_not_found(
        self,
        mock_game,
        mock_test_registry,
        mock_test_history
    ):
        """Test getting non-existent component."""
        controller = TestLabUIController(mock_game, mock_test_registry, mock_test_history)
        controller.scenario_data.load_component_data = Mock(return_value=None)

        component = controller.get_component_data("invalid_component")

        assert component is None
