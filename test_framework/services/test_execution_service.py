"""
Test Execution Service

Handles execution of test scenarios in both visual and headless modes.
Separates test execution logic from UI rendering concerns.
"""

import time
from typing import Callable, Optional, Dict, Any
from test_framework.runner import TestRunner
from simulation_tests.logging_config import get_logger

logger = get_logger(__name__)


class TestExecutionService:
    """Service for executing test scenarios."""

    def __init__(self):
        """Initialize test execution service."""
        self.runner = TestRunner()

    def run_visual(
        self,
        scenario_info: Dict[str, Any],
        battle_scene,
        game
    ) -> bool:
        """
        Execute a test scenario visually in the battle scene.

        Args:
            scenario_info: Scenario information from registry
            battle_scene: Battle scene instance
            game: Game instance for state management

        Returns:
            True if setup successful, False otherwise
        """
        metadata = scenario_info['metadata']

        try:
            # Instantiate scenario
            logger.debug(f" Instantiating scenario class")
            scenario_cls = scenario_info['class']
            scenario = scenario_cls()
            logger.debug(f" Scenario instantiated: {scenario.name}")

            # Load test data
            logger.debug(f" Loading test data for scenario")
            self.runner.load_data_for_scenario(scenario)
            logger.debug(f" Test data loaded successfully")

            # Clear battle engine
            logger.debug(f" Clearing battle engine")
            battle_scene.engine.start([], [])

            # Setup scenario
            logger.debug(f" Calling scenario.setup()")
            scenario.setup(battle_scene.engine)
            logger.debug(f" Scenario setup complete")

            # Configure battle scene for test mode
            logger.debug(f" Configuring battle scene for test mode")
            logger.debug(f" BEFORE: test_mode={battle_scene.test_mode}")
            battle_scene.headless_mode = False
            battle_scene.sim_paused = True  # Start paused
            battle_scene.test_mode = True   # Enable test mode
            battle_scene.test_scenario = scenario  # Pass scenario for update() calls
            battle_scene.test_tick_count = 0  # Reset tick counter
            battle_scene.test_completed = False  # Reset completed flag
            battle_scene.action_return_to_test_lab = False
            logger.debug(f" AFTER: test_mode={battle_scene.test_mode}")
            logger.debug(f" Battle scene configured (paused=True, test_mode=True, scenario={scenario.metadata.test_id})")

            # Fit camera to ships
            if battle_scene.engine.ships:
                battle_scene.camera.fit_objects(battle_scene.engine.ships)
                logger.debug(f" Camera fitted to ships")

            # Switch to battle state
            from game.core.constants import GameState
            logger.debug(f" Switching to BATTLE state")
            game.state = GameState.BATTLE

            return True

        except Exception as e:
            logger.error(f"Error running visual test: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run_headless(
        self,
        scenario_info: Dict[str, Any],
        battle_engine,
        on_progress: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, Any]:
        """
        Execute a test scenario headlessly (fast, no visuals).

        Args:
            scenario_info: Scenario information from registry
            battle_engine: Battle engine instance
            on_progress: Optional callback(current_tick, max_ticks) for progress updates

        Returns:
            Dict containing test results with keys:
                - passed: bool
                - results: Dict with test metrics
                - ticks_run: int
                - duration_real: float
                - error: Optional error message
        """
        metadata = scenario_info['metadata']

        try:
            # Instantiate scenario
            logger.debug(f" Instantiating scenario class for headless run")
            scenario_cls = scenario_info['class']
            scenario = scenario_cls()
            logger.debug(f" Scenario instantiated: {scenario.name}")

            # Load test data
            logger.debug(f" Loading test data for scenario")
            self.runner.load_data_for_scenario(scenario)
            logger.debug(f" Test data loaded successfully")

            # Clear battle engine
            logger.debug(f" Clearing battle engine")
            battle_engine.start([], [])

            # Setup scenario
            logger.debug(f" Calling scenario.setup()")
            scenario.setup(battle_engine)
            logger.debug(f" Scenario setup complete")

            # Run simulation headless
            start_time = time.time()
            tick_count = 0
            max_ticks = scenario.max_ticks

            logger.debug(f" Starting headless simulation loop (max_ticks={max_ticks})")

            # Run simulation as fast as possible
            while tick_count < max_ticks:
                # Call scenario update for dynamic logic
                scenario.update(battle_engine)

                # Update engine one tick
                battle_engine.update()
                tick_count += 1

                # Optional progress callback
                if on_progress and tick_count % 100 == 0:  # Update every 100 ticks
                    on_progress(tick_count, max_ticks)

                # Check if battle ended naturally
                if battle_engine.is_battle_over():
                    logger.debug(f" Battle ended naturally at tick {tick_count}")
                    break

            # Simulation complete - verify results
            elapsed_time = time.time() - start_time
            logger.debug(f" Simulation complete: {tick_count} ticks in {elapsed_time:.2f}s ({tick_count/elapsed_time:.0f} ticks/sec)")

            # Verify and collect results
            scenario.passed = scenario.verify(battle_engine)
            logger.debug(f" Test {'PASSED' if scenario.passed else 'FAILED'}")

            # Store results
            scenario.results['ticks_run'] = tick_count
            scenario.results['duration_real'] = elapsed_time
            scenario.results['ticks'] = tick_count  # Alias for consistency with runner

            # Log test execution (for UI vs headless comparison)
            self.runner._log_test_execution(scenario, headless=True)

            return {
                'passed': scenario.passed,
                'results': scenario.results,
                'ticks_run': tick_count,
                'duration_real': elapsed_time,
                'error': None
            }

        except Exception as e:
            logger.error(f"Error running headless test: {e}")
            import traceback
            traceback.print_exc()

            return {
                'passed': False,
                'results': {},
                'ticks_run': 0,
                'duration_real': 0,
                'error': str(e)
            }
