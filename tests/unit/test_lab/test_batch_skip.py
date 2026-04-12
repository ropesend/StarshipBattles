"""Tests for batch runner skip_test handling (BUG-111).

Verifies that scenarios with skip_test=True are properly skipped
during batch execution without entering the simulation loop.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from game.ui.screens.test_lab.test_executor import TestLabExecutor


def _make_executor(registry=None, output_log=None):
    """Create a TestLabExecutor with mocked dependencies."""
    if output_log is None:
        output_log = []
    return TestLabExecutor(
        registry=registry or Mock(),
        test_history=Mock(),
        controller=Mock(),
        render_progress=lambda t, s, d: None,
        draw_and_flip=lambda: None,
        get_engine=lambda: Mock(),
        ensure_engine=lambda: None,
        switch_to_battle=lambda scenario: None,
        output_log=output_log,
    )


def _make_scenario_info(scenario_cls, metadata=None):
    """Create a scenario_info dict matching registry.get_by_id() format."""
    if metadata is None:
        metadata = Mock()
        metadata.test_id = "TEST-001"
        metadata.name = "Test Scenario"
        metadata.seed = 42
        metadata.max_ticks = 500
    return {
        'class': scenario_cls,
        'metadata': metadata,
    }


class TestBatchSkipTest:
    """Tests that batch runner skips scenarios with skip_test=True (BUG-111)."""

    def test_skipped_scenario_does_not_enter_simulation_loop(self):
        """A scenario with skip_test=True must not call engine.update()."""
        # Create a mock scenario class that returns a skip_test=True instance
        mock_scenario = Mock()
        mock_scenario.skip_test = True
        mock_scenario.skip_reason = "Not implemented yet"
        mock_scenario.results = {}
        mock_scenario.max_ticks = 600
        mock_scenario.metadata = Mock()
        mock_scenario.metadata.seed = 42

        mock_cls = Mock(return_value=mock_scenario)

        mock_registry = Mock()
        mock_registry.get_by_id.return_value = _make_scenario_info(mock_cls)

        mock_engine = Mock()
        output_log = []

        executor = TestLabExecutor(
            registry=mock_registry,
            test_history=Mock(),
            controller=Mock(),
            render_progress=lambda t, s, d: None,
            draw_and_flip=lambda: None,
            get_engine=lambda: mock_engine,
            ensure_engine=lambda: None,
            switch_to_battle=lambda scenario: None,
            output_log=output_log,
        )

        # Set up batch state
        executor.batch_tests = ["TEST-SKIP-001"]
        executor.batch_total = 1
        executor.batch_current_index = 0
        executor.batch_running = True

        with patch('game.ui.screens.test_lab.test_executor.TestRunner') as MockRunner:
            MockRunner.return_value = Mock()
            with patch('game.ui.screens.test_lab.test_executor.pygame'):
                executor.run_next_batch()

        # Engine.update() must NOT have been called
        mock_engine.update.assert_not_called()
        # scenario.setup() must NOT have been called
        mock_scenario.setup.assert_not_called()

    def test_skipped_scenario_logs_skipped_status(self):
        """Skipped scenarios should log SKIPPED, not FAILED."""
        mock_scenario = Mock()
        mock_scenario.skip_test = True
        mock_scenario.skip_reason = "Requires PD ships"
        mock_scenario.results = {}
        mock_scenario.max_ticks = 600
        mock_scenario.metadata = Mock()
        mock_scenario.metadata.seed = 42

        mock_cls = Mock(return_value=mock_scenario)

        mock_registry = Mock()
        mock_registry.get_by_id.return_value = _make_scenario_info(mock_cls)

        output_log = []
        executor = _make_executor(registry=mock_registry, output_log=output_log)

        executor.batch_tests = ["SEEKER-PD-001"]
        executor.batch_total = 1
        executor.batch_current_index = 0
        executor.batch_running = True

        with patch('game.ui.screens.test_lab.test_executor.TestRunner') as MockRunner:
            MockRunner.return_value = Mock()
            with patch('game.ui.screens.test_lab.test_executor.pygame'):
                executor.run_next_batch()

        # Output log should contain SKIPPED, not FAILED
        skip_logs = [msg for msg in output_log if "SKIPPED" in msg]
        assert len(skip_logs) > 0, f"Expected SKIPPED in output log, got: {output_log}"

    def test_skipped_scenario_sets_results(self):
        """Skipped scenarios should set results['skipped'] and results['skip_reason']."""
        mock_scenario = Mock()
        mock_scenario.skip_test = True
        mock_scenario.skip_reason = "Requires PD ships"
        mock_scenario.results = {}
        mock_scenario.max_ticks = 600
        mock_scenario.metadata = Mock()
        mock_scenario.metadata.seed = 42

        mock_cls = Mock(return_value=mock_scenario)

        mock_registry = Mock()
        mock_registry.get_by_id.return_value = _make_scenario_info(mock_cls)

        executor = _make_executor(registry=mock_registry)
        executor.batch_tests = ["SEEKER-PD-001"]
        executor.batch_total = 1
        executor.batch_current_index = 0
        executor.batch_running = True

        with patch('game.ui.screens.test_lab.test_executor.TestRunner') as MockRunner:
            MockRunner.return_value = Mock()
            with patch('game.ui.screens.test_lab.test_executor.pygame'):
                executor.run_next_batch()

        assert mock_scenario.results.get('skipped') is True
        assert mock_scenario.results.get('skip_reason') == "Requires PD ships"

    def test_skipped_scenario_advances_batch_index(self):
        """Skipped scenarios should advance to the next test in the batch."""
        mock_scenario = Mock()
        mock_scenario.skip_test = True
        mock_scenario.skip_reason = "Not ready"
        mock_scenario.results = {}
        mock_scenario.max_ticks = 600
        mock_scenario.metadata = Mock()
        mock_scenario.metadata.seed = 42

        mock_cls = Mock(return_value=mock_scenario)

        mock_registry = Mock()
        mock_registry.get_by_id.return_value = _make_scenario_info(mock_cls)

        executor = _make_executor(registry=mock_registry)
        executor.batch_tests = ["SKIP-001", "SKIP-002"]
        executor.batch_total = 2
        executor.batch_current_index = 0
        executor.batch_running = True

        with patch('game.ui.screens.test_lab.test_executor.TestRunner') as MockRunner:
            MockRunner.return_value = Mock()
            with patch('game.ui.screens.test_lab.test_executor.pygame'):
                executor.run_next_batch()

        assert executor.batch_current_index == 1

    def test_non_skipped_scenario_still_runs_normally(self):
        """Scenarios without skip_test should run the full simulation loop."""
        mock_scenario = Mock()
        mock_scenario.skip_test = False
        mock_scenario.results = {}
        mock_scenario.max_ticks = 10
        mock_scenario.passed = True
        mock_scenario.metadata = Mock()
        mock_scenario.metadata.seed = 42
        mock_scenario.metadata.name = "Normal Test"

        # Make verify return True
        mock_scenario.verify.return_value = True

        # PROJ-269 Phase 6: configure empty-teams spec so the run_battle
        # path short-circuits cleanly.
        empty_spec = Mock()
        empty_spec.seed = 42
        empty_spec.teams = ()
        empty_spec.boundary = None
        empty_spec.modifier_stack = Mock()
        empty_spec.end_condition = Mock()
        empty_spec.absolute_max_ticks = 100
        mock_scenario.to_spec.return_value = empty_spec
        mock_scenario._run_validation.return_value = Mock(passed=True)

        mock_cls = Mock(return_value=mock_scenario)

        metadata = Mock()
        metadata.test_id = "NORMAL-001"
        metadata.name = "Normal Test"
        metadata.seed = 42

        mock_registry = Mock()
        mock_registry.get_by_id.return_value = {
            'class': mock_cls,
            'metadata': metadata,
        }

        mock_engine = Mock()
        mock_engine.is_battle_over.return_value = False

        output_log = []
        # PROJ-269 Phase 6: supply a controller mock with a concrete
        # seed so the run_battle path can do `replace(spec, seed=...)`
        # without stumbling over Mock-valued seeds.
        ctrl = Mock()
        ctrl.ui_state.get_effective_seed.return_value = 42
        ctrl.ui_state.get_seed_mode.return_value = "metadata"
        executor = TestLabExecutor(
            registry=mock_registry,
            test_history=Mock(),
            controller=ctrl,
            render_progress=lambda t, s, d: None,
            draw_and_flip=lambda: None,
            get_engine=lambda: mock_engine,
            ensure_engine=lambda: None,
            switch_to_battle=lambda scenario: None,
            output_log=output_log,
        )

        executor.batch_tests = ["NORMAL-001"]
        executor.batch_total = 1
        executor.batch_current_index = 0
        executor.batch_running = True

        with patch('game.ui.screens.test_lab.test_executor.TestRunner') as MockRunner:
            MockRunner.return_value = Mock()
            with patch('game.ui.screens.test_lab.test_executor.BattleStateCapture') as MockCapture:
                MockCapture.return_value.__enter__ = Mock(return_value=Mock())
                MockCapture.return_value.__exit__ = Mock(return_value=False)
                MockCapture.return_value.get_results_dict = Mock(return_value={})
                with patch('game.ui.screens.test_lab.test_executor.pygame'):
                    executor.run_next_batch()

        # PROJ-269 Phase 6: for non-skipped scenarios, the run_battle
        # path calls `to_spec()` → `before_run_battle()` → run_battle.
        mock_scenario.to_spec.assert_called_once()
        mock_scenario.before_run_battle.assert_called_once()

    def test_headless_skips_skip_test_scenario(self):
        """run_headless should also skip scenarios with skip_test=True."""
        mock_scenario = Mock()
        mock_scenario.skip_test = True
        mock_scenario.skip_reason = "Not implemented"
        mock_scenario.results = {}
        mock_scenario.max_ticks = 600
        mock_scenario.metadata = Mock()
        mock_scenario.metadata.seed = 42
        mock_scenario.name = "Skipped Test"

        mock_cls = Mock(return_value=mock_scenario)

        metadata = Mock()
        metadata.test_id = "SKIP-001"
        metadata.name = "Skipped Test"
        metadata.seed = 42

        mock_registry = Mock()
        mock_registry.get_by_id.return_value = {
            'class': mock_cls,
            'metadata': metadata,
        }

        mock_engine = Mock()
        output_log = []

        executor = TestLabExecutor(
            registry=mock_registry,
            test_history=Mock(),
            controller=Mock(),
            render_progress=lambda t, s, d: None,
            draw_and_flip=lambda: None,
            get_engine=lambda: mock_engine,
            ensure_engine=lambda: None,
            switch_to_battle=lambda scenario: None,
            output_log=output_log,
        )

        with patch('game.ui.screens.test_lab.test_executor.TestRunner') as MockRunner:
            MockRunner.return_value = Mock()
            result = executor.run_headless("SKIP-001")

        # Should return True (completed, even if skipped)
        assert result is True
        # Engine should not have been used for simulation
        mock_engine.update.assert_not_called()
        # Results should be marked as skipped
        assert mock_scenario.results.get('skipped') is True

    def test_scenario_without_skip_test_attribute_runs_normally(self):
        """Scenarios that don't define skip_test at all should run normally."""
        # PROJ-269 Phase 6: spec includes the new spec-compiler surface.
        mock_scenario = Mock(spec=[
            'results', 'max_ticks', 'passed', 'metadata', 'name',
            'setup', 'update', 'verify', '_run_validation', '_override_seed',
            '_effective_seed', '_load_ship',
            'to_spec', 'before_run_battle', 'wire_ships', 'custom_setup',
        ])
        mock_scenario.results = {}
        mock_scenario.max_ticks = 10
        mock_scenario.passed = True
        mock_report = Mock()
        mock_report.passed = True
        mock_scenario._run_validation.return_value = mock_report
        mock_scenario.metadata = Mock()
        mock_scenario.metadata.seed = 42
        mock_scenario.metadata.name = "No Skip Attr"
        mock_scenario.name = "No Skip Attr"

        # PROJ-269 Phase 6: empty-teams spec → short-circuit via run_battle.
        empty_spec = Mock()
        empty_spec.seed = 42
        empty_spec.teams = ()
        empty_spec.boundary = None
        empty_spec.modifier_stack = Mock()
        empty_spec.end_condition = Mock()
        empty_spec.absolute_max_ticks = 100
        mock_scenario.to_spec.return_value = empty_spec

        mock_cls = Mock(return_value=mock_scenario)

        metadata = Mock()
        metadata.test_id = "NOATTR-001"
        metadata.name = "No Skip Attr"
        metadata.seed = 42

        mock_registry = Mock()
        mock_registry.get_by_id.return_value = {
            'class': mock_cls,
            'metadata': metadata,
        }

        mock_engine = Mock()
        mock_engine.is_battle_over.return_value = False

        executor = TestLabExecutor(
            registry=mock_registry,
            test_history=Mock(),
            controller=Mock(),
            render_progress=lambda t, s, d: None,
            draw_and_flip=lambda: None,
            get_engine=lambda: mock_engine,
            ensure_engine=lambda: None,
            switch_to_battle=lambda scenario: None,
            output_log=[],
        )

        executor.batch_tests = ["NOATTR-001"]
        executor.batch_total = 1
        executor.batch_current_index = 0
        executor.batch_running = True

        with patch('game.ui.screens.test_lab.test_executor.TestRunner') as MockRunner:
            MockRunner.return_value = Mock()
            with patch('game.ui.screens.test_lab.test_executor.BattleStateCapture') as MockCapture:
                MockCapture.return_value.__enter__ = Mock(return_value=Mock())
                MockCapture.return_value.__exit__ = Mock(return_value=False)
                MockCapture.return_value.get_results_dict = Mock(return_value={})
                with patch('game.ui.screens.test_lab.test_executor.pygame'):
                    executor.run_next_batch()

        # PROJ-269 Phase 6: should still run normally via the spec path.
        mock_scenario.to_spec.assert_called_once()
