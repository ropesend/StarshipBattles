"""
TestLabExecutor - Test execution engine for Combat Lab.

This module handles running test scenarios both visually and headlessly,
including batch execution of multiple tests. It is decoupled from the
screen's pygame rendering through callback interfaces.
"""
from __future__ import annotations

from typing import Any
import time
import pygame

from combat_lab.runner import TestRunner
from combat_lab.battle_state_capture import BattleStateCapture
from combat_lab.logging_config import get_logger

logger = get_logger(__name__)


class TestLabExecutor:
    """
    Handles test scenario execution for the Combat Lab.

    Supports three execution modes:
    - Visual: Runs test in battle scene with full rendering
    - Headless: Runs test inline with progress overlay
    - Batch: Runs multiple tests headlessly in sequence

    All pygame/screen access flows through callbacks to maintain
    separation from the screen class.
    """

    def __init__(
        self,
        registry,
        test_history,
        controller,
        render_progress,
        draw_and_flip,
        get_engine,
        ensure_engine,
        switch_to_battle,
        output_log,
    ):
        """
        Initialize the test executor.

        Args:
            registry: TestRegistry instance for scenario lookup
            test_history: TestHistory instance for recording results
            controller: TestLabUIController for seed mode access
            render_progress: Callback (title, subtitle, detail) -> None for progress overlay
            draw_and_flip: Callback () -> None to redraw screen and flip display
            get_engine: Callback () -> BattleEngine
            ensure_engine: Callback () -> None to ensure engine exists
            switch_to_battle: Callback (scenario) -> None for visual test mode
            output_log: List reference for appending log messages
        """
        self.registry = registry
        self.test_history = test_history
        self.controller = controller
        self.render_progress = render_progress
        self.draw_and_flip = draw_and_flip
        self.get_engine = get_engine
        self.ensure_engine = ensure_engine
        self.switch_to_battle = switch_to_battle
        self.output_log = output_log

        # Batch execution state
        self.batch_running = False
        self.batch_tests = []
        self.batch_current_index = 0
        self.batch_total = 0

    def run_visual(self, test_id) -> None:
        """
        Run the selected test scenario visually in Combat Lab.

        Args:
            test_id: Test ID to run (e.g., "BEAM360-001")
        """
        if test_id is None:
            self.output_log.append("ERROR: No test selected!")
            return

        scenario_info = self.registry.get_by_id(test_id)
        if scenario_info is None:
            self.output_log.append(f"ERROR: Test {test_id} not found!")
            return

        metadata = scenario_info['metadata']
        self.output_log.append(f"Running {metadata.name}...")

        runner = TestRunner()

        try:
            # Instantiate scenario
            logger.debug(f" Instantiating scenario class")
            scenario_cls = scenario_info['class']
            scenario = scenario_cls()
            logger.debug(f" Scenario instantiated: {scenario.name}")

            # Load test data
            logger.debug(f" Loading test data for scenario")
            runner.load_data_for_scenario(scenario)
            logger.debug(f" Test data loaded successfully")

            # Ensure battle engine exists (may have been reset after previous test)
            self.ensure_engine()

            if self.get_engine() is None:
                self.output_log.append("ERROR: Could not create battle engine!")
                return

            # Switch to battle scene for visual execution. `_switch_to_battle`
            # compiles the spec, drives BattleController.start_from_spec, and
            # wires the scenario's initial_state + custom_setup.
            self.switch_to_battle(scenario)

            self.output_log.append(f"Started test {test_id}")

        except (OSError, ValueError, KeyError, TypeError) as e:
            logger.error(f"Error running visual test: {e}", exc_info=True)
            self.output_log.append(f"ERROR: {e}")
        finally:
            runner.cleanup()

    def run_visual_baseline(self, test_id) -> None:
        """
        Run the baseline battle of a ComparisonScenario visually.

        Sets _visual_baseline=True on the scenario so setup() configures
        the baseline configuration on the runner's engine for rendering.
        """
        if test_id is None:
            self.output_log.append("ERROR: No test selected!")
            return

        scenario_info = self.registry.get_by_id(test_id)
        if scenario_info is None:
            self.output_log.append(f"ERROR: Test {test_id} not found!")
            return

        if not scenario_info.get('is_comparison'):
            self.output_log.append(f"ERROR: {test_id} is not a comparison scenario")
            return

        metadata = scenario_info['metadata']
        self.output_log.append(f"Running {metadata.name} (baseline)...")

        runner = TestRunner()

        try:
            scenario_cls = scenario_info['class']
            scenario = scenario_cls()
            scenario._visual_baseline = True

            runner.load_data_for_scenario(scenario)
            self.ensure_engine()

            if self.get_engine() is None:
                self.output_log.append("ERROR: Could not create battle engine!")
                return

            self.switch_to_battle(scenario)
            self.output_log.append(f"Started baseline for {test_id}")

        except (OSError, ValueError, KeyError, TypeError) as e:
            logger.error(f"Error running visual baseline: {e}", exc_info=True)
            self.output_log.append(f"ERROR: {e}")
        finally:
            runner.cleanup()

    def run_headless(self, test_id) -> bool:
        """
        Run the selected test scenario in headless mode (fast, no visuals).

        Args:
            test_id: Test ID to run (e.g., "BEAM360-001")

        Returns:
            True if test completed (pass or fail), False if error
        """
        if test_id is None:
            self.output_log.append("ERROR: No test selected!")
            return False

        scenario_info = self.registry.get_by_id(test_id)
        if scenario_info is None:
            self.output_log.append(f"ERROR: Test {test_id} not found!")
            return False

        metadata = scenario_info['metadata']
        self.output_log.append(f"Running {metadata.name} (headless)...")

        runner = TestRunner()

        try:
            # Instantiate scenario
            logger.debug(f" Instantiating scenario class for headless run")
            scenario_cls = scenario_info['class']
            scenario = scenario_cls()
            logger.debug(f" Scenario instantiated: {scenario.name}")

            # Skip scenarios that are marked as not ready to run (BUG-111)
            if getattr(scenario, 'skip_test', False):
                skip_reason = getattr(scenario, 'skip_reason', 'No reason given')
                scenario.results['skipped'] = True
                scenario.results['skip_reason'] = skip_reason
                self.registry.update_last_run_results(test_id, scenario.results)
                self.output_log.append(f"Test {test_id} SKIPPED - {skip_reason}")
                return True

            runner.load_data_for_scenario(scenario)

            seed = self.controller.ui_state.get_effective_seed(metadata.seed)
            logger.debug(f" Using seed: {seed} (mode: {self.controller.ui_state.get_seed_mode()})")
            scenario._override_seed = seed

            # Show "Running Test..." overlay.
            self.render_progress("Running Test...", metadata.name, f"Max ticks: {scenario.max_ticks}")
            self.draw_and_flip()

            return self._run_scenario_via_run_battle(
                test_id=test_id,
                scenario=scenario,
                seed=seed,
                runner=runner,
                progress_label=None,
            )

        except (OSError, ValueError, KeyError, TypeError) as e:
            self.output_log.append(f"ERROR: {e}")
            return False
        finally:
            runner.cleanup()

    def _run_scenario_via_run_battle(
        self, *, test_id, scenario, seed, runner, progress_label,
    ) -> bool:
        """Run a scenario headless through `run_battle(spec)`.

        PROJ-269 Phase 6 Task 6.9: replaces the legacy
        `scenario.setup(engine)` + direct tick loop pattern with the
        unified entry.
        PROJ-270 Phase 2.5: engine_ref closure trick is gone — validator
        consumes `(outcome, telemetry)` from the shared helper.

        `BattleStateCapture` is driven manually (no `with` block) — the
        engine isn't available until the helper's `pre_tick_loop_hook` fires.
        """
        from combat_lab.services.scenario_run_helper import run_scenario_via_run_battle

        # State capture bridged across run_battle via manual __enter__/__exit__.
        state_capture = BattleStateCapture(engine=None, test_id=test_id, seed=seed)

        def pre_tick_loop_hook(engine) -> None:
            # Now the engine has ships + state → safe to capture initial.
            state_capture.engine = engine
            state_capture.__enter__()

        start_time = time.time()
        try:
            outcome, telemetry = run_scenario_via_run_battle(
                scenario,
                seed_override=seed,
                pre_tick_loop_hook=pre_tick_loop_hook,
            )
        finally:
            # Always capture final state (even on exceptions) so
            # partial-run states are written to disk for forensics.
            if state_capture.engine is not None:
                state_capture.__exit__(None, None, None)

        elapsed_time = time.time() - start_time
        tick_count = outcome.duration_ticks
        logger.debug(
            f" Simulation complete: {tick_count} ticks in {elapsed_time:.2f}s "
            f"({tick_count / elapsed_time:.0f} ticks/sec)"
            if elapsed_time > 0
            else f" Simulation complete: {tick_count} ticks"
        )

        # Validate results via outcome + telemetry.
        report = scenario._run_validation(outcome, telemetry)
        scenario.passed = report.passed

        scenario.results["ticks_run"] = tick_count
        scenario.results["duration_real"] = elapsed_time
        scenario.results["ticks"] = tick_count
        scenario.results.update(state_capture.get_results_dict())
        self.registry.update_last_run_results(test_id, scenario.results)
        self.test_history.add_run(test_id, scenario.results)
        runner.log_test_execution(scenario, headless=True)

        status = "PASSED" if scenario.passed else "FAILED"
        if progress_label is not None:
            self.output_log.append(f"{progress_label} {test_id}: {status}")
        else:
            self.output_log.append(
                f"Test {test_id} {status} ({tick_count} ticks, {elapsed_time:.2f}s)"
            )
        return True

    def run_all(self, filtered_scenarios) -> None:
        """
        Run all visible tests headlessly in sequence.

        Args:
            filtered_scenarios: Dict of test_id -> scenario_info to run
        """
        self.batch_tests = sorted(filtered_scenarios.keys())
        self.batch_total = len(self.batch_tests)

        if self.batch_total == 0:
            self.output_log.append("No tests to run!")
            return

        self.batch_current_index = 0
        self.batch_running = True
        self.output_log.append(f"Starting batch run of {self.batch_total} tests...")
        self.run_next_batch()

    def run_next_batch(self) -> None:
        """Run the next test in the batch sequence."""
        if self.batch_current_index >= self.batch_total:
            # All tests complete
            self.batch_running = False
            self.output_log.append(f"Batch complete: {self.batch_total} tests run")
            return

        test_id = self.batch_tests[self.batch_current_index]
        scenario_info = self.registry.get_by_id(test_id)

        if scenario_info is None:
            self.output_log.append(f"ERROR: Test {test_id} not found, skipping")
            self.batch_current_index += 1
            self.run_next_batch()
            return

        metadata = scenario_info['metadata']
        runner = TestRunner()

        try:
            # Instantiate scenario
            scenario_cls = scenario_info['class']
            scenario = scenario_cls()

            # Skip scenarios that are marked as not ready to run (BUG-111)
            if getattr(scenario, 'skip_test', False):
                skip_reason = getattr(scenario, 'skip_reason', 'No reason given')
                scenario.results['skipped'] = True
                scenario.results['skip_reason'] = skip_reason
                self.registry.update_last_run_results(test_id, scenario.results)
                self.output_log.append(
                    f"[{self.batch_current_index + 1}/{self.batch_total}] {test_id}: SKIPPED - {skip_reason}"
                )
                self.batch_current_index += 1
                pygame.time.set_timer(pygame.USEREVENT + 1, 50, loops=1)
                return

            runner.load_data_for_scenario(scenario)

            seed = self.controller.ui_state.get_effective_seed(metadata.seed)
            scenario._override_seed = seed

            progress_title = f"Running test {self.batch_current_index + 1}/{self.batch_total}"
            self.render_progress(progress_title, metadata.name, f"ID: {test_id}")
            self.draw_and_flip()

            self._run_scenario_via_run_battle(
                test_id=test_id,
                scenario=scenario,
                seed=seed,
                runner=runner,
                progress_label=f"[{self.batch_current_index + 1}/{self.batch_total}]",
            )

        except (OSError, ValueError, KeyError, TypeError) as e:
            self.output_log.append(f"[{self.batch_current_index + 1}/{self.batch_total}] {test_id}: ERROR - {e}")
        finally:
            runner.cleanup()

        # Move to next test
        self.batch_current_index += 1
        # Use a small delay to allow UI updates, then continue
        pygame.time.set_timer(pygame.USEREVENT + 1, 50, loops=1)

    def continue_batch(self) -> None:
        """Continue batch execution (called from event handler)."""
        if self.batch_running:
            self.run_next_batch()
