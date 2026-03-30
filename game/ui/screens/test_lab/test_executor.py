"""
TestLabExecutor - Test execution engine for Combat Lab.

This module handles running test scenarios both visually and headlessly,
including batch execution of multiple tests. It is decoupled from the
screen's pygame rendering through callback interfaces.
"""
import time
import pygame

from test_framework.runner import TestRunner
from test_framework.battle_state_capture import BattleStateCapture
from simulation_tests.logging_config import get_logger

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

    def run_visual(self, test_id):
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

            # Switch to battle scene for visual execution
            # (_switch_to_battle handles engine.start + scenario.setup)
            self.switch_to_battle(scenario)

            self.output_log.append(f"Started test {test_id}")

        except (OSError, ValueError, KeyError, TypeError) as e:
            logger.error(f"Error running visual test: {e}", exc_info=True)
            self.output_log.append(f"ERROR: {e}")

    def run_visual_baseline(self, test_id):
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

    def run_headless(self, test_id):
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

        # Ensure battle engine exists (may have been reset after visual test)
        self.ensure_engine()
        engine = self.get_engine()

        if engine is None:
            self.output_log.append("ERROR: Could not create battle engine!")
            return False

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

            # Load test data
            logger.debug(f" Loading test data for scenario")
            runner.load_data_for_scenario(scenario)
            logger.debug(f" Test data loaded successfully")

            # Get seed based on current seed mode setting BEFORE starting engine
            seed = self.controller.ui_state.get_effective_seed(metadata.seed)
            logger.debug(f" Using seed: {seed} (mode: {self.controller.ui_state.get_seed_mode()})")

            # Pass seed to scenario for use in engine.start()
            scenario._override_seed = seed
            logger.debug(f" Set scenario._override_seed={seed}")

            # Setup scenario (this will call engine.start with the seed)
            logger.debug(f" Calling scenario.setup()")
            scenario.setup(engine)
            logger.debug(f" Scenario setup complete")

            # Show "Running Test..." overlay
            self.render_progress("Running Test...", metadata.name, f"Max ticks: {scenario.max_ticks}")
            self.draw_and_flip()

            # Run simulation headless
            result = self._execute_headless(test_id, scenario, engine, seed, runner)

            return result

        except (OSError, ValueError, KeyError, TypeError) as e:
            self.output_log.append(f"ERROR: {e}")
            return False

    def _execute_headless(self, test_id, scenario, engine, seed, runner):
        """
        Execute a headless test simulation.

        Shared logic between run_headless and run_next_batch.

        Args:
            test_id: Test ID being run
            scenario: Instantiated scenario object
            engine: BattleEngine instance
            seed: Random seed used
            runner: TestRunner instance for logging

        Returns:
            True if test completed successfully
        """
        start_time = time.time()
        tick_count = 0
        max_ticks = scenario.max_ticks

        logger.debug(f" Starting headless simulation loop (max_ticks={max_ticks})")

        with BattleStateCapture(engine, test_id, seed) as state_capture:
            # Run simulation as fast as possible
            while tick_count < max_ticks:
                # Call scenario update for dynamic logic
                scenario.update(engine)

                # Update engine one tick
                engine.update()
                tick_count += 1

                # Check if battle ended naturally
                if engine.is_battle_over():
                    logger.debug(f" Battle ended naturally at tick {tick_count}")
                    break

        # Simulation complete - verify results
        elapsed_time = time.time() - start_time
        logger.debug(f" Simulation complete: {tick_count} ticks in {elapsed_time:.2f}s ({tick_count/elapsed_time:.0f} ticks/sec)")

        # Validate results (new system) or verify (legacy fallback)
        try:
            report = scenario._run_validation(engine)
            scenario.passed = report.passed
        except NotImplementedError:
            scenario.passed = scenario.verify(engine)
        logger.debug(f" Test {'PASSED' if scenario.passed else 'FAILED'}")

        # Store results including battle state file paths
        scenario.results['ticks_run'] = tick_count
        scenario.results['duration_real'] = elapsed_time
        scenario.results['ticks'] = tick_count  # Alias for consistency with runner
        scenario.results.update(state_capture.get_results_dict())  # Add state file paths and seed
        self.registry.update_last_run_results(test_id, scenario.results)

        # Add to persistent test history
        self.test_history.add_run(test_id, scenario.results)

        # Log test execution (for UI vs headless comparison)
        runner.log_test_execution(scenario, headless=True)

        # Update output log
        status = "PASSED" if scenario.passed else "FAILED"
        self.output_log.append(f"Test {test_id} {status} ({tick_count} ticks, {elapsed_time:.2f}s)")

        return True

    def run_all(self, filtered_scenarios):
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

    def run_next_batch(self):
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

            # Load test data
            runner.load_data_for_scenario(scenario)

            # Get seed based on current seed mode setting BEFORE starting engine
            seed = self.controller.ui_state.get_effective_seed(metadata.seed)

            # Ensure battle engine exists (may have been reset)
            self.ensure_engine()
            engine = self.get_engine()

            if engine is None:
                self.output_log.append(f"[{self.batch_current_index + 1}/{self.batch_total}] {test_id}: ERROR - No engine")
                self.batch_current_index += 1
                pygame.time.set_timer(pygame.USEREVENT + 1, 50, loops=1)
                return

            # Pass seed to scenario for use in engine.start()
            scenario._override_seed = seed

            # Setup scenario (this will call engine.start with the seed)
            scenario.setup(engine)

            # Show progress overlay
            progress_title = f"Running test {self.batch_current_index + 1}/{self.batch_total}"
            self.render_progress(progress_title, metadata.name, f"ID: {test_id}")
            self.draw_and_flip()

            # Run headless simulation with battle state capture
            start_time = time.time()
            tick_count = 0
            max_ticks = scenario.max_ticks

            with BattleStateCapture(engine, test_id, seed) as state_capture:
                while tick_count < max_ticks:
                    scenario.update(engine)
                    engine.update()
                    tick_count += 1

                    if engine.is_battle_over():
                        break

            # Validate results (new system) or verify (legacy fallback)
            elapsed_time = time.time() - start_time
            try:
                report = scenario._run_validation(engine)
                scenario.passed = report.passed
            except NotImplementedError:
                scenario.passed = scenario.verify(engine)

            # Store results including battle state file paths
            scenario.results['ticks_run'] = tick_count
            scenario.results['duration_real'] = elapsed_time
            scenario.results['ticks'] = tick_count
            scenario.results.update(state_capture.get_results_dict())
            self.registry.update_last_run_results(test_id, scenario.results)

            # Add to persistent test history
            self.test_history.add_run(test_id, scenario.results)

            # Log test execution
            runner.log_test_execution(scenario, headless=True)

            # Update output log
            status = "PASSED" if scenario.passed else "FAILED"
            self.output_log.append(f"[{self.batch_current_index + 1}/{self.batch_total}] {test_id}: {status}")

        except (OSError, ValueError, KeyError, TypeError) as e:
            self.output_log.append(f"[{self.batch_current_index + 1}/{self.batch_total}] {test_id}: ERROR - {e}")

        # Move to next test
        self.batch_current_index += 1
        # Use a small delay to allow UI updates, then continue
        pygame.time.set_timer(pygame.USEREVENT + 1, 50, loops=1)

    def continue_batch(self):
        """Continue batch execution (called from event handler)."""
        if self.batch_running:
            self.run_next_batch()
