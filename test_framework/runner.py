import sys
import os
import pygame
import importlib
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.core.registry import RegistryManager
from game.simulation.systems.battle_engine import BattleEngine
from game.simulation.components.component import load_components, load_modifiers
from game.simulation.entities.ship import initialize_ship_data
from simulation_tests.logging_config import get_logger, setup_combat_lab_logging

# Setup logging
setup_combat_lab_logging()
logger = get_logger(__name__)

class TestRunner:
    def __init__(self):
        self.engine = BattleEngine()
        self.current_scenario = None
        
    def load_data_for_scenario(self, scenario):
        """
        Reload global game data based on scenario requirements.

        IMPORTANT: When running from Combat Lab, this keeps the registry unfrozen
        to allow ship loading and validator creation. The registry will remain
        unfrozen until the test completes or the game restarts.
        """
        logger.info(f"Loading data for scenario: {scenario.name}")

        paths = scenario.get_data_paths()

        # Reset Globals (unfreeze if needed for Combat Lab)
        registry = RegistryManager.instance()
        was_frozen = registry._frozen
        logger.debug(f"RegistryManager frozen state: {was_frozen}")

        if was_frozen:
            logger.debug("Unfreezing RegistryManager for test data loading")
            registry._frozen = False

        logger.debug("Clearing registry")
        registry.clear()

        # Load New Data
        try:
            logger.debug(f"Loading modifiers from {paths['modifiers']}")
            load_modifiers(paths['modifiers'])

            logger.debug(f"Loading components from {paths['components']}")
            load_components(paths['components'])

            # Helper needed in ship.py to accept direct path
            from game.simulation.entities.ship import load_vehicle_classes
            logger.debug(f"Loading vehicle classes from {paths['vehicle_classes']}")
            load_vehicle_classes(paths['vehicle_classes'])

            # IMPORTANT: Keep unfrozen to allow ship loading in scenario.setup()
            # The registry will remain unfrozen for the test duration
            logger.debug("Registry remains unfrozen to allow ship loading")

        except Exception as e:
            logger.critical(f"Failed to load test data: {e}", exc_info=True)
            raise e
            
    def run_scenario(self, scenario_cls, headless=True, render_callback=None):
        """
        Execute a scenario.
        
        Args:
            scenario_cls: Class of the scenario to run
            headless: If True, run fast without rendering (unless render_callback provided)
            render_callback: Optional function(engine) -> None to draw the state
        """
        scenario = scenario_cls()
        self.current_scenario = scenario
        
        # 1. Load Data
        self.load_data_for_scenario(scenario)
        
        # 2. Setup Engine
        from game.simulation.systems.battle_engine import BattleLogger
        logger = BattleLogger(enabled=True)
        self.engine = BattleEngine(logger=logger) # Fresh engine with logging
        
        # 3. Scenario Setup
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
            return scenario

        end_time = time.time()
        duration = end_time - start_time

        # 5. Verify
        scenario.passed = scenario.verify(self.engine)
        scenario.results['duration_real'] = duration
        scenario.results['ticks'] = self.engine.tick_counter

        status = "PASSED" if scenario.passed else "FAILED"
        logger.info(f"Result: {status} in {duration:.2f}s")
        return scenario

if __name__ == "__main__":
    import argparse
    import importlib.util

    parser = argparse.ArgumentParser(description="Run Starship Battles Combat Scenarios")
    parser.add_argument("scenario", help="Scenario module name (e.g., 'test_framework.scenarios.simple_duel') or path")
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
        
        # Find CombatScenario subclass
        scenario_cls = None
        from test_framework.scenario import CombatScenario
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, CombatScenario) and attr is not CombatScenario:
                scenario_cls = attr
                break
        
        if not scenario_cls:
            logger.error(f"No CombatScenario subclass found in {args.scenario}")
            sys.exit(1)

        runner = TestRunner()
        runner.run_scenario(scenario_cls, headless=args.headless)

    except ImportError as e:
        logger.error(f"Import Error: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Execution Error: {e}", exc_info=True)
