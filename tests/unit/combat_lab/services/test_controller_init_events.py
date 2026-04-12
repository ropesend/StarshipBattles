"""
Unit tests for TestLabUIController - initialization and event handling.

PROJ-48: Split from test_test_lab_controller.py
"""

from unittest.mock import Mock
from combat_lab.services.test_lab_controller import TestLabUIController


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
        assert controller.output_log == []

    def test_init_loads_scenarios(self, mock_game, mock_test_registry, mock_test_history):
        """Test that initialization loads all scenarios."""
        controller = TestLabUIController(mock_game, mock_test_registry, mock_test_history)

        mock_test_registry.get_all_scenarios.assert_called_once()


class TestHistoryLoadedOnInit:
    """Test that historical test results are loaded into registry on startup."""

    def test_init_loads_history_into_registry(
        self, mock_game, mock_test_registry, mock_test_history
    ):
        """Tests with prior runs show their last result in the registry."""
        # Setup: history has a passing run for TEST-001
        mock_run = Mock()
        mock_run.to_dict.return_value = {
            'passed': True,
            'validation_summary': {'pass': 3, 'fail': 0, 'warn': 0},
            'validation_results': [
                {'name': 'Check1', 'status': 'PASS', 'phase': 'outcome'}
            ],
        }
        mock_test_history.get_latest_run = Mock(side_effect=lambda tid: mock_run if tid == 'TEST-001' else None)

        # Registry has TEST-001 in its scenarios
        mock_test_registry.get_all_scenarios.return_value = {
            'TEST-001': {'last_run_results': None},
        }

        TestLabUIController(mock_game, mock_test_registry, mock_test_history)

        # Registry should have been updated with the historical result
        mock_test_registry.update_last_run_results.assert_any_call('TEST-001', mock_run.to_dict())

    def test_init_skips_tests_with_no_history(
        self, mock_game, mock_test_registry, mock_test_history
    ):
        """Tests without prior runs keep last_run_results as None."""
        mock_test_history.get_latest_run = Mock(return_value=None)

        mock_test_registry.get_all_scenarios.return_value = {
            'NEW-001': {'last_run_results': None},
        }

        TestLabUIController(mock_game, mock_test_registry, mock_test_history)

        # update_last_run_results should NOT be called for tests with no history
        for call in mock_test_registry.update_last_run_results.call_args_list:
            assert call[0][0] != 'NEW-001'

    def test_init_loads_failing_test_history(
        self, mock_game, mock_test_registry, mock_test_history
    ):
        """Failed test results are also loaded into registry."""
        mock_run = Mock()
        mock_run.to_dict.return_value = {
            'passed': False,
            'validation_summary': {'pass': 2, 'fail': 1, 'warn': 0},
            'validation_results': [
                {'name': 'Check1', 'status': 'PASS', 'phase': 'data'},
                {'name': 'Check2', 'status': 'FAIL', 'phase': 'outcome'},
            ],
        }
        mock_test_history.get_latest_run = Mock(return_value=mock_run)

        mock_test_registry.get_all_scenarios.return_value = {
            'FAIL-001': {'last_run_results': None},
        }

        TestLabUIController(mock_game, mock_test_registry, mock_test_history)

        mock_test_registry.update_last_run_results.assert_any_call('FAIL-001', mock_run.to_dict())


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
