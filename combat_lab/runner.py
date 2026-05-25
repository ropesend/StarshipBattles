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
from game.simulation.components.component import load_components, load_modifiers
from combat_lab.logging_config import get_logger, setup_combat_lab_logging

# Importing the Combat Lab spec compiler here ensures the monkey-patch that
# attaches `TestScenario.to_spec` is always in effect when the runner is
# loaded — callers don't have to know about that side-effect.
import combat_lab.spec_compiler  # noqa: F401 (side-effect import)

# Setup logging
setup_combat_lab_logging()
logger = get_logger(__name__)


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
        """Initialize the Combat Lab TestRunner.

        PROJ-274: switches the default ship materializer to
        `DesignOnlyMaterializer` backed by `load_combat_lab_design`. Covers
        both the CLI entry point (`python -m combat_lab.run_tests`) and the
        UI entry point (`TestLabExecutor`) — both instantiate a
        `TestRunner` before scenario execution, so this is the single
        install point.
        """
        self.engine = None  # Created fresh per scenario in run_scenario()
        self.current_scenario = None
        self.test_log = []
        from combat_lab.design_loader import load_combat_lab_design
        from game.simulation.services.ship_materializer import (
            DesignOnlyMaterializer,
            set_default_ship_materializer,
        )
        set_default_ship_materializer(
            DesignOnlyMaterializer(design_loader=load_combat_lab_design)
        )

    def cleanup(self):
        """Restore the production default ship materializer.

        Undoes the ``DesignOnlyMaterializer`` override installed in
        ``__init__``.  Passing ``None`` triggers lazy re-init to
        ``InstanceBackedMaterializer`` on the next
        ``get_default_ship_materializer()`` call (see
        ``ship_materializer.py`` docstring).

        In-game callers (``TestLabExecutor``) must call this after test
        execution completes so the override does not leak into
        non-Combat-Lab flows (e.g. Battle Setup).
        CLI entry points (``run_tests.py``) run in their own process
        and do not need cleanup.
        """
        from game.simulation.services.ship_materializer import (
            set_default_ship_materializer,
        )
        set_default_ship_materializer(None)

    def load_data_for_scenario(self, scenario):
        """
        Hydrate the global registry from the scenario's data directory.

        Delegates to ``game.data_loader.load_data_from_path`` so the same
        mode-scoped lifecycle hook (registry clear + hydrate + downstream
        cache invalidation) that fires on main-game data transitions
        fires here too. The scenario's three legacy file-path attributes
        (``components_path``, ``modifiers_path``, ``vehicle_classes_path``)
        all share a common parent directory; that directory is the data
        set the scenario runs against.
        """
        logger.info(f"Loading data for scenario: {scenario.name}")

        from game.data_loader import load_data_from_path

        paths = scenario.get_data_paths()
        data_dir = os.path.dirname(paths['components'])
        try:
            load_data_from_path(data_dir)
        except Exception as e:
            logger.critical(f"Failed to load test data: {e}", exc_info=True)
            raise

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

        # 2. Compile + drive via the shared helper.
        # PROJ-270 Phase 2.5: engine_ref closure trick is gone — validator
        # consumes (outcome, telemetry). The helper handles to_spec,
        # before_run_battle, ship materialization, wire_ships, custom_setup,
        # and per-tick dispatch internally.
        from combat_lab.services.scenario_run_helper import run_scenario_via_run_battle

        def per_tick_hook(engine):
            if render_callback is not None:
                render_callback(engine)

        logger.info(
            f"Starting Scenario: {scenario.name} (Max Ticks: {scenario.max_ticks})"
        )
        start_time = time.time()
        try:
            outcome, telemetry = run_scenario_via_run_battle(
                scenario, per_tick_hook=per_tick_hook,
            )
        except Exception as e:
            logger.error(f"Scenario Crash: {e}", exc_info=True)
            scenario.passed = False
            scenario.results['error'] = str(e)
            if log_results:
                self.log_test_execution(scenario, headless)
            return scenario

        duration = time.time() - start_time
        self.engine = None  # PROJ-270 Phase 2.5: no engine escape from run_battle.

        # 6. Validate via outcome + telemetry.
        report = scenario._run_validation(outcome, telemetry)
        scenario.passed = report.passed
        scenario.results['duration_real'] = duration
        scenario.results['ticks'] = outcome.duration_ticks
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
