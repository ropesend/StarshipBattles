"""
Unit tests for TestLabUIController - metadata updates and queries.

PROJ-48: Split from test_test_lab_controller.py
PROJ-342: Removed `TestHandleRunHeadless` class — `handle_run_headless`
deleted along with `TestExecutionService`/`TestResultsService` orphans.
"""

import pytest
from unittest.mock import Mock
from combat_lab.services.test_lab_controller import TestLabUIController
from tests.unit.combat_lab.services.conftest import create_test_metadata


class TestGetFilteredScenarios:
    """Test scenario filtering."""

    def test_get_filtered_scenarios_all(
        self,
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
        controller = TestLabUIController(mock_test_registry, mock_test_history)

        scenarios = controller.get_filtered_scenarios(category=None)

        assert scenarios == all_scenarios

    def test_get_filtered_scenarios_by_category(
        self,
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
        controller = TestLabUIController(mock_test_registry, mock_test_history)

        scenarios = controller.get_filtered_scenarios(category="Beam Weapons")

        assert len(scenarios) == 1
        assert 'TEST-001' in scenarios
        assert 'TEST-002' not in scenarios


class TestGetShipInfo:
    """Test ship info retrieval."""

    def test_get_ship_info_success(
        self,
        mock_test_registry,
        mock_test_history,
        sample_scenario_info
    ):
        """Test getting ship info for test."""
        mock_test_registry.get_by_id = Mock(return_value=sample_scenario_info)
        controller = TestLabUIController(mock_test_registry, mock_test_history)
        controller.scenario_data.extract_ships_from_scenario = Mock(return_value=[
            {'role': 'Attacker', 'filename': 'test.json'}
        ])

        ships = controller.get_ship_info("TEST-001")

        assert len(ships) == 1
        assert ships[0]['role'] == 'Attacker'

    def test_get_ship_info_test_not_found(
        self,
        mock_test_registry,
        mock_test_history
    ):
        """Test getting ship info for invalid test."""
        mock_test_registry.get_by_id = Mock(return_value=None)
        controller = TestLabUIController(mock_test_registry, mock_test_history)

        ships = controller.get_ship_info("INVALID")

        assert ships == []


class TestGetComponentData:
    """Test component data retrieval."""

    def test_get_component_data_success(
        self,
        mock_test_registry,
        mock_test_history,
        sample_component_data
    ):
        """Test getting component data."""
        controller = TestLabUIController(mock_test_registry, mock_test_history)
        controller.scenario_data.load_component_data = Mock(return_value=sample_component_data)

        component = controller.get_component_data("test_beam_low_acc_1dmg")

        assert component == sample_component_data

    def test_get_component_data_not_found(
        self,
        mock_test_registry,
        mock_test_history
    ):
        """Test getting non-existent component."""
        controller = TestLabUIController(mock_test_registry, mock_test_history)
        controller.scenario_data.load_component_data = Mock(return_value=None)

        component = controller.get_component_data("invalid_component")

        assert component is None
