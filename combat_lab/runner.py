import sys
import os
import importlib
import time
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.core.paths import Paths
from game.core.registry import get_default_registry_manager, get_default_registry_provider
from game.ai.ai_factory import AIControllerFactory
from game.simulation.battle_runner import run_battle
from game.simulation.components.component import load_components, load_modifiers
from combat_lab.logging_config import get_logger, setup_combat_lab_logging

# Importing the Combat Lab spec compiler here ensures the monkey-patch that
# attaches `TestScenario.to_spec` is always in effect when the runner is
# loaded — callers don't have to know about that side-effect.
import combat_lab.spec_compiler  # noqa: F401 (side-effect import)

# Setup logging
setup_combat_lab_logging()
logger = get_logger(__name__)


def _role_from_instance_id(instance_id: str):
    """Return the role suffix after the last ':' in a spec instance_id.

    PROJ-269 Task 6.7a: the Combat Lab compiler tags each ShipSpec with
    a role (`:attacker`, `:target`, `:ship1`, `:ship2`, `:ship`,
    `:variant_attacker`, `:variant_target`, `:baseline_attacker`,
    `:baseline_target`). The runner uses this to build the
    `ships_by_role` dict passed to `scenario.wire_ships(...)`.
    """
    if not instance_id or ":" not in instance_id:
        return None
    return instance_id.rsplit(":", 1)[1]


def _snapshot_ship_state(ship) -> dict:
    """Capture a freshly-loaded Ship's state pre-engine-start.

    Used by `_run_scenario_via_battle_runner` — some scenarios assert
    against the initial HP / resource values a ship has BEFORE
    `engine.start()` runs its first component-update cycle (which can
    drain always-on resources like fuel/energy). Templates read from
    this snapshot in `wire_ships(...)` instead of re-reading post-start.
    """
    state: dict = {"hp": getattr(ship, "hp", 0)}
    resources = getattr(ship, "resources", None)
    if resources is None:
        state["resources"] = {}
        return state
    resource_values: dict = {}
    try:
        names = resources.get_resource_names()
    except (AttributeError, TypeError):
        names = []
    for name in names:
        try:
            resource_values[name] = resources.get_value(name)
        except (AttributeError, KeyError, TypeError):
            continue
    state["resources"] = resource_values
    return state

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
        """Execute a scenario through the unified `run_battle(spec)` entry.

        PROJ-269 Phase 6: the legacy raw-`BattleEngine(...)` path and the
        `USE_BATTLE_RUNNER` feature flag were removed once all five Combat
        Lab scenario templates gained compiler support. Scenarios that
        subclass a template (StaticTarget / Duel / Propulsion / Resource /
        Comparison) are compiled to a `BattleSpec` via `scenario.to_spec()`
        and handed to `run_battle`. Scenarios that do not inherit from a
        template must provide their own `to_spec()` override.

        Args:
            scenario_cls: Class of the scenario to run.
            headless: If True, run without rendering (unless
                render_callback is provided).
            render_callback: Optional callable(engine) invoked each tick —
                used by the Combat Lab visual runner for frame rendering.
            log_results: If True, record results to the persistent log.
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

        # 2. Compile to a BattleSpec. Scenarios must inherit from a
        # template or supply their own `to_spec()` override; anything else
        # is a hard error (no silent legacy fallback post-Phase 6).
        spec = scenario.to_spec(registries=None)
        ai_factory = AIControllerFactory()

        # 3. Pre-run hook — ComparisonScenario runs its private baseline
        # battle here (must happen BEFORE variant ships are materialized
        # to preserve ship-creation ordering for deterministic outcomes).
        scenario.before_run_battle(spec)

        # 4. Role-keyed ship registry + pre-start snapshot. `ship_builder`
        # populates both as ships materialize; `pre_tick_loop` passes the
        # full dicts to `scenario.wire_ships(...)` after `engine.start()`.
        ships_by_role: dict = {}
        initial_state_by_role: dict = {}

        def ship_builder(ship_spec):
            ship = scenario._load_ship(ship_spec.design_id)
            role = _role_from_instance_id(ship_spec.instance_id)
            if role is not None:
                ships_by_role[role] = ship
                initial_state_by_role[role] = _snapshot_ship_state(ship)
            return ship

        engine_ref = {"engine": None}

        def pre_tick_loop(engine):
            engine_ref["engine"] = engine
            # Custom_setup hooks and ComparisonScenario's baseline-battle
            # path both read `_effective_seed`.
            scenario._effective_seed = spec.seed
            scenario.wire_ships(
                ships_by_role,
                engine=engine,
                initial_state=initial_state_by_role,
            )
            scenario.custom_setup(engine)

        def per_tick(engine):
            engine_ref["engine"] = engine
            scenario.update(engine)
            if render_callback is not None:
                render_callback(engine)

        # 5. Run the unified path.
        logger.info(
            f"Starting Scenario: {scenario.name} (Max Ticks: {scenario.max_ticks})"
        )
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
            logger.error(f"Scenario Crash: {e}", exc_info=True)
            scenario.passed = False
            scenario.results['error'] = str(e)
            if log_results:
                self.log_test_execution(scenario, headless)
            return scenario

        duration = time.time() - start_time
        engine = engine_ref["engine"]
        self.engine = engine  # Exposed for external callers reading runner.engine

        if engine is None:
            scenario.passed = False
            scenario.results['error'] = 'run_battle produced no engine reference'
            if log_results:
                self.log_test_execution(scenario, headless)
            return scenario

        # 6. Validate.
        report = scenario._run_validation(engine)
        scenario.passed = report.passed
        scenario.results['duration_real'] = duration
        scenario.results['ticks'] = engine.tick_counter
        scenario.results['battle_outcome_end_reason'] = outcome.end_reason.value

        status = "PASSED" if scenario.passed else "FAILED"
        logger.info(f"Result: {status} in {duration:.2f}s")

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
