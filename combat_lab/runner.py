import sys
import os
import pygame
import importlib
import time
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.core.paths import Paths
from game.core.registry import get_default_registry_manager, get_default_registry_provider
from game.simulation.systems.battle_engine import BattleEngine
from game.ai.ai_factory import AIControllerFactory
from game.simulation.components.component import load_components, load_modifiers
from combat_lab.logging_config import get_logger, setup_combat_lab_logging

# PROJ-269 Phase 1 Task 1.10: feature flag that routes Combat Lab CLI through
# the unified `run_battle(spec) -> BattleOutcome` entry. Off by default —
# subsequent phases migrate more call sites until Phase 6 deletes the legacy
# branch entirely.
USE_BATTLE_RUNNER: bool = os.environ.get("SB_USE_BATTLE_RUNNER", "0") == "1"

# Importing the Combat Lab spec compiler here ensures the monkey-patch that
# attaches `TestScenario.to_spec` is always in effect when the runner is
# loaded — callers don't have to know about that side-effect.
import combat_lab.spec_compiler  # noqa: F401 (side-effect import)

# Setup logging
setup_combat_lab_logging()
logger = get_logger(__name__)

class TestRunner:
    __test__ = False  # Not a pytest test class

    def __init__(self):
        self.engine = None  # Created fresh per scenario in run_scenario()
        self.current_scenario = None
        self.test_log = []
        
    def load_data_for_scenario(self, scenario):
        """
        Reload global game data based on scenario requirements.

        Uses ``registry.unfrozen()`` so the registry is temporarily writable
        during clear/hydrate and is restored to its prior frozen state on
        exit (even if hydration raises). Safe to call from any context
        whether the registry is currently frozen or not.
        """
        logger.info(f"Loading data for scenario: {scenario.name}")

        paths = scenario.get_data_paths()
        registry = get_default_registry_manager()

        with registry.unfrozen():
            logger.debug("Clearing registry")
            registry.clear()

            # Load New Data
            try:
                # PROJ-211: Pass registry_provider explicitly (no fallback)
                provider = get_default_registry_provider()

                logger.debug(f"Loading modifiers from {paths['modifiers']}")
                load_modifiers(paths['modifiers'], registry_provider=provider)

                logger.debug(f"Loading components from {paths['components']}")
                load_components(paths['components'], registry_provider=provider)

                # Helper needed in ship.py to accept direct path
                from game.simulation.entities.ship_loader import load_vehicle_classes
                logger.debug(f"Loading vehicle classes from {paths['vehicle_classes']}")
                load_vehicle_classes(paths['vehicle_classes'], registry_provider=provider)

            except Exception as e:
                logger.critical(f"Failed to load test data: {e}", exc_info=True)
                raise e
            
    def run_scenario(self, scenario_cls, headless=True, render_callback=None, log_results=True):
        """
        Execute a scenario.

        Args:
            scenario_cls: Class of the scenario to run
            headless: If True, run fast without rendering (unless render_callback provided)
            render_callback: Optional function(engine) -> None to draw the state
            log_results: If True, log results to test_log and file (default: True)
        """
        scenario = scenario_cls()
        self.current_scenario = scenario

        # Skip scenarios that are marked as not ready to run (BUG-111)
        if getattr(scenario, 'skip_test', False):
            skip_reason = getattr(scenario, 'skip_reason', 'No reason given')
            scenario.passed = False
            scenario.results['skipped'] = True
            scenario.results['skip_reason'] = skip_reason
            logger.info(f"Skipping scenario: {scenario.name} - {skip_reason}")
            return scenario

        # 1. Load Data (manages its own unfrozen() scope for clear + hydrate)
        self.load_data_for_scenario(scenario)

        if USE_BATTLE_RUNNER:
            return self._run_scenario_via_battle_runner(
                scenario, headless=headless, log_results=log_results
            )

        # 2. Setup Engine
        from game.simulation.systems.battle_engine import BattleLogger
        battle_logger = BattleLogger(enabled=True)
        # PROJ-126: Create AI factory, then inject into engine (engine calls set_grid automatically)
        ai_factory = AIControllerFactory()
        self.engine = BattleEngine(logger=battle_logger, ai_factory=ai_factory)

        # 3. Scenario Setup — ship loading and validator caching are
        # safe on a frozen registry; only source-data mutations need
        # the unfrozen() scope, and those live inside load_data_for_scenario.
        scenario.setup(self.engine)

        # 4. Loop
        logger.info(f"Starting Scenario: {scenario.name} (Max Ticks: {scenario.max_ticks})")
        start_time = time.time()

        try:
            for tick in range(scenario.max_ticks):
                # Update
                self.engine.update()
                scenario.update(self.engine)

                # Check for early exit?
                if self.engine.is_battle_over():
                     logger.info(f"Battle ended at tick {tick}")
                     break

                # Render if needed
                if render_callback:
                    render_callback(self.engine)

        except Exception as e:
            logger.error(f"Scenario Crash: {e}", exc_info=True)
            scenario.passed = False
            scenario.results['error'] = str(e)
            if log_results:
                self.log_test_execution(scenario, headless)
            return scenario

        end_time = time.time()
        duration = end_time - start_time

        # 5. Validate
        report = scenario._run_validation(self.engine)
        scenario.passed = report.passed
        scenario.results['duration_real'] = duration
        scenario.results['ticks'] = self.engine.tick_counter

        status = "PASSED" if scenario.passed else "FAILED"
        logger.info(f"Result: {status} in {duration:.2f}s")

        # 6. Log results if enabled
        if log_results:
            self.log_test_execution(scenario, headless)

        return scenario

    # ------------------------------------------------------------------
    # PROJ-269 Phase 1 Task 1.10: BattleSpec → run_battle smoke path.
    # ------------------------------------------------------------------

    def _run_scenario_via_battle_runner(
        self, scenario, *, headless: bool, log_results: bool
    ):
        """Run a scenario through `run_battle(spec)` when USE_BATTLE_RUNNER=1.

        Keeps scenario-side semantics (self.attacker / self.target /
        initial_hp / _run_validation) intact by:
          1. Calling `scenario.to_spec(registries)` to translate the
             scenario into a BattleSpec.
          2. Supplying a ship_builder that calls `scenario._load_ship`
             and attaches the resulting Ship onto the scenario
             (`scenario.attacker` / `scenario.target`).
          3. Capturing the engine via a per-tick callback so
             `_run_validation(engine)` can run after the battle.

        Falls back to the legacy branch with a logged warning if the
        scenario's template is not yet supported by the compiler.
        """
        from game.simulation.battle_runner import run_battle

        logger.info(
            f"[USE_BATTLE_RUNNER=1] routing scenario {scenario.name} "
            f"through run_battle()"
        )
        ai_factory = AIControllerFactory()

        # Build the spec (may raise NotImplementedError for unsupported
        # templates — Phase 1 supports StaticTargetScenario subclasses).
        try:
            spec = scenario.to_spec(registries=None)
        except NotImplementedError as exc:
            logger.warning(
                f"to_spec() not supported for {type(scenario).__name__}: "
                f"{exc}. Falling back to legacy path."
            )
            return self._run_scenario_legacy(
                scenario, headless=headless, log_results=log_results
            )

        # Also pre-seed the scenario's template-level state that
        # `_run_validation` reads. StaticTargetScenario sets
        # self.initial_hp from target HP *in setup()*; mirror that here
        # since we don't call setup() on the battle_runner path.
        scenario_ships_by_id = {}

        def ship_builder(ship_spec):
            """Translate ShipSpec.design_id → scenario._load_ship(file).

            Also mirrors the template-level attribute wiring that
            `StaticTargetScenario.setup()` performs (movement policies,
            initial_hp). That way `scenario.custom_setup` + validation
            have the same state they'd have on the legacy path.
            """
            ship = scenario._load_ship(ship_spec.design_id)
            scenario_ships_by_id[ship_spec.instance_id] = ship
            if ":attacker" in ship_spec.instance_id:
                scenario.attacker = ship
                if getattr(scenario, "force_fire", True):
                    ship.movement_policy = "test_stationary"
                else:
                    ship.movement_policy = "test_do_nothing"
            elif ":target" in ship_spec.instance_id:
                scenario.target = ship
                scenario.initial_hp = ship.hp
                ship.movement_policy = "test_do_nothing"
            return ship

        # Capture the engine for validation.
        engine_ref = {"engine": None}

        def pre_tick_loop(engine):
            """Runs once after engine.start() and before the first tick.
            Mirrors `StaticTargetScenario.setup`'s tail (custom_setup hook)."""
            engine_ref["engine"] = engine
            scenario.custom_setup(engine)

        def per_tick(engine):
            # `pre_tick_loop` already set engine_ref, but keep it in sync
            # in case of reinforcements / teardown swaps in later phases.
            engine_ref["engine"] = engine
            scenario.update(engine)

        # Run the unified path.
        start_time = time.time()
        try:
            outcome = run_battle(
                spec,
                ai_factory=ai_factory,
                ship_builder=ship_builder,
                per_tick_callback=per_tick,
                pre_tick_loop_callback=pre_tick_loop,
            )
        except Exception as e:
            logger.error(f"Scenario Crash (run_battle): {e}", exc_info=True)
            scenario.passed = False
            scenario.results['error'] = str(e)
            if log_results:
                self.log_test_execution(scenario, headless)
            return scenario

        duration = time.time() - start_time
        engine = engine_ref["engine"]
        self.engine = engine  # For any external callers reading runner.engine

        # Restore StaticTargetScenario template behavior: target.movement_policy
        # setup in setup() is skipped on the new path, but that's OK for
        # Phase 1 smoke runs where the scenario just observes ticks via the
        # existing AI-driven ships.
        if engine is None:
            scenario.passed = False
            scenario.results['error'] = 'run_battle produced no engine reference'
            if log_results:
                self.log_test_execution(scenario, headless)
            return scenario

        report = scenario._run_validation(engine)
        scenario.passed = report.passed
        scenario.results['duration_real'] = duration
        scenario.results['ticks'] = engine.tick_counter
        scenario.results['battle_outcome_end_reason'] = outcome.end_reason.value

        status = "PASSED" if scenario.passed else "FAILED"
        logger.info(f"Result: {status} in {duration:.2f}s (battle_runner path)")

        if log_results:
            self.log_test_execution(scenario, headless)
        return scenario

    def _run_scenario_legacy(self, scenario, *, headless, log_results):
        """Fallback: the legacy path, extracted so the runner branch can
        reuse it when `USE_BATTLE_RUNNER` is on but the scenario template
        isn't yet supported by `build_test_battle_spec`."""
        from game.simulation.systems.battle_engine import BattleLogger
        battle_logger = BattleLogger(enabled=True)
        ai_factory = AIControllerFactory()
        self.engine = BattleEngine(logger=battle_logger, ai_factory=ai_factory)
        scenario.setup(self.engine)
        logger.info(f"Starting Scenario: {scenario.name} (Max Ticks: {scenario.max_ticks})")
        start_time = time.time()
        try:
            for tick in range(scenario.max_ticks):
                self.engine.update()
                scenario.update(self.engine)
                if self.engine.is_battle_over():
                    logger.info(f"Battle ended at tick {tick}")
                    break
        except Exception as e:
            logger.error(f"Scenario Crash: {e}", exc_info=True)
            scenario.passed = False
            scenario.results['error'] = str(e)
            if log_results:
                self.log_test_execution(scenario, headless)
            return scenario
        duration = time.time() - start_time
        report = scenario._run_validation(self.engine)
        scenario.passed = report.passed
        scenario.results['duration_real'] = duration
        scenario.results['ticks'] = self.engine.tick_counter
        status = "PASSED" if scenario.passed else "FAILED"
        logger.info(f"Result: {status} in {duration:.2f}s (legacy path)")
        if log_results:
            self.log_test_execution(scenario, headless)
        return scenario

    def log_test_execution(self, scenario, headless):
        """
        Log test execution results for comparison between UI and headless modes.

        Args:
            scenario: Completed scenario instance with results
            headless: True if run in headless mode, False if run in UI mode
        """
        # Create log entry
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'test_id': scenario.metadata.test_id,
            'test_name': scenario.metadata.name,
            'mode': 'headless' if headless else 'ui',
            'passed': scenario.passed,
            'ticks_run': scenario.results.get('ticks', 0),
            'damage_dealt': scenario.results.get('damage_dealt', 0),
            'duration_real': scenario.results.get('duration_real', 0),
            'results': self._sanitize_results(scenario.results)
        }

        # Add to in-memory log
        self.test_log.append(log_entry)

        # Write to persistent log file
        log_file = Path(Paths.COMBAT_LAB_OUTPUT_DIR) / "combat_lab_test_log.jsonl"
        try:
            os.makedirs(log_file.parent, exist_ok=True)
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
            logger.debug(f"Logged test execution to {log_file}")
        except Exception as e:
            logger.warning(f"Failed to write test log: {e}")

        # Print summary
        mode_str = 'Headless' if headless else 'UI'
        result_str = 'PASS' if scenario.passed else 'FAIL'
        logger.info(f"[TEST LOG] {scenario.metadata.test_id} - Mode: {mode_str} - Result: {result_str}")

    def _sanitize_results(self, results):
        """
        Sanitize results dict to ensure JSON serialization.

        Removes non-serializable objects and converts them to strings.
        """
        sanitized = {}
        for key, value in results.items():
            try:
                # Test if value is JSON serializable
                json.dumps(value)
                sanitized[key] = value
            except (TypeError, ValueError):
                # Convert non-serializable to string
                sanitized[key] = str(value)
        return sanitized

if __name__ == "__main__":
    import argparse
    import importlib.util

    parser = argparse.ArgumentParser(description="Run Starship Battles Combat Scenarios")
    parser.add_argument("scenario", help="Scenario module name (e.g., 'combat_lab.scenarios.beam_scenarios') or path")
    parser.add_argument("--headless", action="store_true", default=True, help="Run without graphics")
    parser.add_argument("--visual", action="store_false", dest="headless", help="Run with graphics (if supported by runner)")
    args = parser.parse_args()

    # Resolve scenario class
    try:
        # Try importing as module
        if args.scenario.endswith(".py"):
            # Load from file path (flexible)
            path = os.path.abspath(args.scenario)
            spec = importlib.util.spec_from_file_location("dynamic_scenario", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        else:
            # Load as python module path
            module = importlib.import_module(args.scenario)
        
        # Find TestScenario subclass
        scenario_cls = None
        from combat_lab.scenarios.base import TestScenario
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, TestScenario) and attr is not TestScenario:
                scenario_cls = attr
                break

        if not scenario_cls:
            logger.error(f"No TestScenario subclass found in {args.scenario}")
            sys.exit(1)

        runner = TestRunner()
        runner.run_scenario(scenario_cls, headless=args.headless)

    except ImportError as e:
        logger.error(f"Import Error: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Execution Error: {e}", exc_info=True)
