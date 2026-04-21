"""
Test Execution Service

Handles execution of test scenarios in both visual and headless modes.
Separates test execution logic from UI rendering concerns.
"""

import time
from typing import Callable, Optional, Dict, Any
from combat_lab.runner import TestRunner
from combat_lab.logging_config import get_logger

logger = get_logger(__name__)


class TestExecutionService:
    __test__ = False  # Not a pytest test class

    """Service for executing test scenarios."""

    def __init__(self):
        """Initialize test execution service."""
        pass

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

            # PROJ-269 Phase 6 Tasks 6.9/6.10: spec-compiled visual-mode
            # path. `controller.start()` is called normally — no more
            # `_is_started=True` hack.
            from combat_lab.runner import _snapshot_ship_state
            from combat_lab.spec_compiler import build_test_battle_spec
            from game.ai.ai_factory import AIControllerFactory
            from game.simulation.battle_config import BattleConfig
            from game.core.return_destination import ReturnDestination
            from game.simulation.battle_controller import BattleController
            from game.simulation.battle_runner import materialize_spec_ships

            # PROJ-279: explicit composition — call the compiler directly.
            spec = build_test_battle_spec(scenario, registries=None)
            scenario.before_run_battle(spec)

            config = BattleConfig(
                start_paused=True,
                return_destination=ReturnDestination.TEST_LAB,
                show_results=True,
                seed=spec.seed,
                end_condition=spec.end_condition,
                absolute_max_ticks=spec.absolute_max_ticks,
            )

            # Pre-materialize ships for initial_state snapshots (role-keyed).
            # start_from_spec re-materializes internally — ship_builder is
            # deterministic per design_id. PROJ-274: both calls rely on
            # the context materializer (DesignOnlyMaterializer installed
            # by TestRunner); no explicit ship_builder kwarg required.
            from game.simulation.battle_runner import (
                _default_ship_builder_from_context,
            )
            _pre_teams, pre_ships_by_role = materialize_spec_ships(
                spec,
                ship_builder=_default_ship_builder_from_context(),
            )
            initial_state = {
                role: _snapshot_ship_state(ship)
                for role, ship in pre_ships_by_role.items()
            }

            # PROJ-270 Phase 10: unified spec-in path.
            controller = BattleController()
            _result, ships_by_role = controller.start_from_spec(
                spec,
                ai_factory=AIControllerFactory(),
                config=config,
            )
            engine = controller.service.get_engine()

            scenario._effective_seed = spec.seed
            scenario.wire_ships(
                ships_by_role, engine=engine, initial_state=initial_state,
            )
            scenario.custom_setup(engine)

            battle_scene.start_battle(controller)
            logger.debug(f" Battle started via controller (scenario={scenario.metadata.test_id})")

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
        finally:
            runner.cleanup()

    def run_headless(
        self,
        scenario_info: Dict[str, Any],
        on_progress: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, Any]:
        """
        Execute a test scenario headlessly through `run_battle(spec)`.

        PROJ-270 Phase 1.1: legacy `battle_engine.start([], [])` +
        `scenario.setup(engine)` + raw-tick-loop removed.
        PROJ-270 Phase 2.5: validator now consumes `(outcome, telemetry)`;
        the live-engine closure trick is gone.

        Args:
            scenario_info: Scenario information from registry.
            on_progress: Optional callback(current_tick, max_ticks) for
                progress updates. Fired every 100 ticks.

        Returns:
            Dict containing test results with keys:
                - passed: bool
                - results: Dict with test metrics
                - ticks_run: int
                - duration_real: float
                - error: Optional error message
        """
        from combat_lab.services.scenario_run_helper import run_scenario_via_run_battle

        runner = TestRunner()
        try:
            logger.debug(" Instantiating scenario class for headless run")
            scenario_cls = scenario_info['class']
            scenario = scenario_cls()
            logger.debug(f" Scenario instantiated: {scenario.name}")

            logger.debug(" Loading test data for scenario")
            runner.load_data_for_scenario(scenario)
            logger.debug(" Test data loaded successfully")

            max_ticks = getattr(scenario, 'max_ticks', 0) or 0
            progress_state = {'last_reported': 0}

            def per_tick_hook(engine):
                if on_progress is None:
                    return
                tick = engine.tick_counter
                if tick // 100 > progress_state['last_reported'] // 100 and tick > 0:
                    on_progress(tick, max_ticks)
                    progress_state['last_reported'] = tick

            logger.debug(f" Starting run_battle (max_ticks={max_ticks})")
            start_time = time.time()
            outcome, telemetry = run_scenario_via_run_battle(
                scenario,
                per_tick_hook=per_tick_hook,
            )
            elapsed_time = time.time() - start_time

            tick_count = outcome.duration_ticks
            ticks_per_sec = tick_count / elapsed_time if elapsed_time > 0 else 0
            logger.debug(
                f" Simulation complete: {tick_count} ticks in {elapsed_time:.2f}s "
                f"({ticks_per_sec:.0f} ticks/sec)"
            )

            # PROJ-270 Phase 2.5: validate via outcome + telemetry.
            report = scenario._run_validation(outcome, telemetry)
            scenario.passed = report.passed
            logger.debug(f" Test {'PASSED' if scenario.passed else 'FAILED'}")

            scenario.results['ticks_run'] = tick_count
            scenario.results['duration_real'] = elapsed_time
            scenario.results['ticks'] = tick_count  # Alias for consistency with runner.

            runner.log_test_execution(scenario, headless=True)

            return {
                'passed': scenario.passed,
                'results': scenario.results,
                'ticks_run': tick_count,
                'duration_real': elapsed_time,
                'error': None,
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
                'error': str(e),
            }
        finally:
            runner.cleanup()
