"""
Unit tests for TestLabUIController - initialization and event handling.

PROJ-48: Split from test_test_lab_controller.py
"""

import pytest
from unittest.mock import Mock, patch
from test_framework.services.test_lab_controller import TestLabUIController


class TestTestLabUIControllerInit:
    """Test TestLabUIController initialization."""

    def test_init(self, mock_game, mock_test_registry, mock_test_history):
        """Test controller initialization."""
        controller = TestLabUIController(mock_game, mock_test_registry, mock_test_history)

        assert controller.game is mock_game
        assert controller.registry is mock_test_registry
        assert controller.scenario_data is not None
        assert controller.test_execution is not None
        assert controller.ui_state is not None
        assert controller.test_results is not None
        assert controller.metadata_mgmt is not None
        assert controller.output_log == []

    def test_init_loads_scenarios(self, mock_game, mock_test_registry, mock_test_history):
        """Test that initialization loads all scenarios."""
        controller = TestLabUIController(mock_game, mock_test_registry, mock_test_history)

        mock_test_registry.get_all_scenarios.assert_called_once()

    @patch('test_framework.services.test_lab_controller.MetadataManagementService')
    def test_init_runs_static_validation(
        self,
        mock_metadata_service,
        mock_game,
        mock_test_registry,
        mock_test_history
    ):
        """Test that static validation runs on init."""
        mock_metadata_instance = Mock()
        mock_metadata_service.return_value = mock_metadata_instance
        mock_metadata_instance.validate_all_scenarios = Mock(return_value={})

        controller = TestLabUIController(mock_game, mock_test_registry, mock_test_history)

        mock_metadata_instance.validate_all_scenarios.assert_called_once()


class TestHandleCategoryClick:
    """Test category click handling."""

    def test_handle_category_click(self, mock_game, mock_test_registry, mock_test_history):
        """Test category selection."""
        controller = TestLabUIController(mock_game, mock_test_registry, mock_test_history)

        controller.handle_category_click("Beam Weapons")

        assert controller.ui_state.get_selected_category() == "Beam Weapons"

    def test_handle_category_click_clears_test(self, mock_game, mock_test_registry, mock_test_history):
        """Test that category click clears test selection."""
        controller = TestLabUIController(mock_game, mock_test_registry, mock_test_history)
        controller.ui_state.select_test("TEST-001")

        controller.handle_category_click("Beam Weapons")

        assert controller.ui_state.get_selected_test_id() is None


class TestHandleTestClick:
    """Test test click handling."""

    def test_handle_test_click(self, mock_game, mock_test_registry, mock_test_history):
        """Test test selection."""
        controller = TestLabUIController(mock_game, mock_test_registry, mock_test_history)

        controller.handle_test_click("TEST-001")

        assert controller.ui_state.get_selected_test_id() == "TEST-001"


class TestHandleRunVisual:
    """Test visual test execution handling."""

    def test_handle_run_visual_success(
        self,
        mock_game,
        mock_test_registry,
        mock_test_history,
        sample_scenario_info
    ):
        """Test successful visual test run."""
        mock_test_registry.get_by_id = Mock(return_value=sample_scenario_info)
        controller = TestLabUIController(mock_game, mock_test_registry, mock_test_history)
        controller.ui_state.select_test("TEST-001")
        controller.test_execution.run_visual = Mock(return_value=True)

        controller.handle_run_visual()

        controller.test_execution.run_visual.assert_called_once()
        assert any("Started test" in msg for msg in controller.output_log)

    def test_handle_run_visual_no_test_selected(
        self,
        mock_game,
        mock_test_registry,
        mock_test_history
    ):
        """Test visual run with no test selected."""
        controller = TestLabUIController(mock_game, mock_test_registry, mock_test_history)

        controller.handle_run_visual()

        assert any("No test selected" in msg for msg in controller.output_log)

    def test_handle_run_visual_test_not_found(
        self,
        mock_game,
        mock_test_registry,
        mock_test_history
    ):
        """Test visual run with invalid test ID."""
        mock_test_registry.get_by_id = Mock(return_value=None)
        controller = TestLabUIController(mock_game, mock_test_registry, mock_test_history)
        controller.ui_state.select_test("INVALID")

        controller.handle_run_visual()

        assert any("not found" in msg for msg in controller.output_log)

    def test_handle_run_visual_execution_failure(
        self,
        mock_game,
        mock_test_registry,
        mock_test_history,
        sample_scenario_info
    ):
        """Test visual run execution failure."""
        mock_test_registry.get_by_id = Mock(return_value=sample_scenario_info)
        controller = TestLabUIController(mock_game, mock_test_registry, mock_test_history)
        controller.ui_state.select_test("TEST-001")
        controller.test_execution.run_visual = Mock(return_value=False)

        controller.handle_run_visual()

        assert any("Failed to start" in msg for msg in controller.output_log)
