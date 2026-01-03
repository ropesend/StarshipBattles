"""
Component Test Runner - Execute simulation-based component tests.

Loads test configurations, runs simulations, and verifies results
by parsing log files.
"""
import json
import os
import sys
import unittest
import math
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pygame
from game.simulation.entities.ship import Ship, load_vehicle_classes, LayerType
from game.simulation.components.component import load_components, create_component
from game.simulation.systems.battle_engine import BattleEngine
from game.ai.controller import AIController

from test_logger import ComponentTestLogger, TestEventType, enable_test_logging
from test_log_parser import TestLogParser


class TestGrid:
    """Mock grid for AI target finding in tests."""
    def __init__(self, ships: List[Ship]):
        self.ships = ships
        self.width = 10000
        self.height = 10000
        
    def query_radius(self, position, radius):
        """Return all ships within radius (simplified: returns all ships)."""
        # In a real hash we'd filter, but for small N tests, all is fine.
        # Could implement distance check if strictly needed.
        return self.ships
        
    def add(self, entity): pass
    def remove(self, entity): pass
    def update(self, entity): pass


@dataclass
class TestAssertion:
    """Represents a single test assertion."""
    assertion_type: str
    params: Dict[str, Any]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestAssertion':
        return cls(
            assertion_type=data.get('type', ''),
            params={k: v for k, v in data.items() if k != 'type'}
        )


@dataclass
class TestConfig:
    """Represents a test configuration loaded from JSON."""
    test_id: str
    description: str
    ships: List[Dict[str, Any]]
    duration_ticks: int
    assertions: List[TestAssertion]
    velocity_log_ticks: List[int] = None  # Ticks at which to log velocity
    
    @classmethod
    def from_file(cls, filepath: str) -> 'TestConfig':
        """Load test configuration from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls(
            test_id=data.get('test_id', 'UNKNOWN'),
            description=data.get('description', ''),
            ships=data.get('ships', []),
            duration_ticks=data.get('duration_ticks', 1000),
            assertions=[TestAssertion.from_dict(a) for a in data.get('assertions', [])],
            velocity_log_ticks=data.get('velocity_log_ticks', [0, 100, 500, 1000])
        )


class ComponentTestRunner:
    """
    Runs simulation-based component tests.
    
    Usage:
        runner = ComponentTestRunner()
        result = runner.run_test("unit_tests/simulation/test_configs/ENG-001.json")
        print(f"Pass: {result.passed}")
    """
    
    def __init__(self, data_dir: str = "unit_tests/data"):
        """
        Initialize the test runner.
        
        Args:
            data_dir: Directory containing test data files
        """
        self.data_dir = data_dir
        self._initialized = False
    
    def _ensure_initialized(self) -> None:
        """Ensure pygame and data files are loaded."""
        if self._initialized:
            return
        
        pygame.init()
        load_vehicle_classes(os.path.join(self.data_dir, "test_vehicleclasses.json"))
        load_components(os.path.join(self.data_dir, "test_components.json"))
        self._initialized = True
    
    def run_test(self, config_path: str) -> 'TestResult':
        """
        Execute a single simulation test.
        
        Args:
            config_path: Path to test configuration JSON
            
        Returns:
            TestResult with pass/fail status and details
        """
        self._ensure_initialized()
        
        # Load configuration
        config = TestConfig.from_file(config_path)
        
        # Create logger
        log_filename = f"{config.test_id}.log"
        logger = ComponentTestLogger(log_filename, enabled=True)
        logger.start()
        
        # Load ships
        ships = []
        for ship_config in config.ships:
            ship = self._load_ship(ship_config)
            ships.append(ship)
            
            # Log spawn event
            logger.log_ship_spawn(
                name=ship.name,
                x=ship.x,
                y=ship.y,
                ship_class=ship.ship_class,
                mass=ship.mass,
                thrust=ship.total_thrust
            )
        
        # Log simulation start
        logger.log_sim_start(config.test_id, [s.name for s in ships])
        
        # Initialize Grid and AI Controllers
        grid = TestGrid(ships)
        ai_controllers = {}
        for ship in ships:
            # Determine enemy team (Team 1 vs Team 2 usually)
            enemy_team = 2 if ship.team_id == 1 else 1 
            # If default team 0, maybe enemy is 1? Default for tests: Attacker=1, Target=2.
            # If ship set to 0, adapt if needed.
            ai_controllers[ship.name] = AIController(ship, grid, enemy_team)

        # Build AI strategy map for each ship
        ai_strategies = {}
        for i, ship_config in enumerate(config.ships):
            ai_strategies[ships[i].name] = ship_config.get('ai_strategy', 'do_nothing')
        
        # Run simulation
        for tick in range(config.duration_ticks + 1):
            logger.set_tick(tick)
            
            # Apply AI behaviors and update each ship
            for ship in ships:
                if not ship.is_alive: continue
                
                strategy = ai_strategies.get(ship.name, 'do_nothing')
                controller = ai_controllers[ship.name]
                
                # Ensure target acquisition
                if not ship.current_target:
                    ship.current_target = controller.find_target()
                    if ship.name == "Test Attacker Proj360" and not ship.current_target:
                         # Force debug for this specific failure
                         pass # print(f"[DEBUG] {ship.name} failed to find target. Grid: {len(grid.ships)} ships. EnemyTeam: {controller.enemy_team_id}")
                
                if ship.name == "Test Attacker Proj360" and tick < 5:
                    print(f"[DEBUG] Tick {tick}: {ship.name} Target: {ship.current_target} Trigger: {ship.comp_trigger_pulled} Pos: {ship.position}")

                # Check for Direct Behavior Override via known keys
                if strategy in controller.behaviors:
                    behavior = controller.behaviors[strategy]
                    if controller.current_behavior != behavior:
                        if behavior: behavior.enter()
                        controller.current_behavior = behavior
                    
                    # Manually handle firing trigger for overridden behaviors
                    # (Normally handled by controller.update)
                    if ship.current_target:
                        ship.comp_trigger_pulled = True
                    else:
                        ship.comp_trigger_pulled = False
                        
                    if behavior:
                        # Context usually comes from policy/strategy, empty dict for simple overrides
                        behavior.update(ship.current_target, {})
                else:
                    # Use full controller logic (Strategy Manager Lookup)
                    ship.ai_strategy = strategy
                    controller.update()
                
                # Update ship physics (uses throttles set by AI)
                ship.update(context={'projectiles': [], 'grid': grid})
            
            # Log velocity and position at specified ticks
            if tick in config.velocity_log_ticks or tick == config.duration_ticks:
                for ship in ships:
                    vel = ship.velocity if hasattr(ship, 'velocity') else pygame.math.Vector2(0, 0)
                    speed = getattr(ship, 'current_speed', vel.length() if vel else 0)
                    heading = ship.angle if hasattr(ship, 'angle') else 0
                    logger.log_ship_velocity(
                        name=ship.name,
                        vx=vel.x if vel else 0,
                        vy=vel.y if vel else 0,
                        speed=speed,
                        heading=heading
                    )
                    logger.log_ship_position(
                        name=ship.name,
                        x=ship.x,
                        y=ship.y
                    )
        
        # Log simulation end
        logger.log_sim_end(ships_remaining=len([s for s in ships if s.is_alive]))
        logger.close()
        
        # Parse log and verify assertions
        log_path = os.path.join(logger.log_dir, log_filename)
        parser = TestLogParser(log_path)
        parser.parse()
        
        # Verify assertions
        result = TestResult(test_id=config.test_id, description=config.description)
        
        for assertion in config.assertions:
            passed, message = self._verify_assertion(assertion, parser)
            result.add_assertion_result(assertion.assertion_type, passed, message)
        
        return result
    
    def _load_ship(self, ship_config: Dict[str, Any]) -> Ship:
        """Load a ship from configuration."""
        import json
        
        # Load from file if specified
        if 'file' in ship_config:
            filepath = ship_config['file']
            if not os.path.isabs(filepath):
                filepath = os.path.join(os.path.dirname(__file__), '..', '..', filepath)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            ship = Ship.from_dict(data)
            ship.recalculate_stats()
        else:
            # Create ship programmatically
            ship = Ship(
                name=ship_config.get('name', 'TestShip'),
                x=ship_config.get('position', [0, 0])[0],
                y=ship_config.get('position', [0, 0])[1],
                color=(0, 255, 0),
                ship_class=ship_config.get('ship_class', 'TestS_2L')
            )
        
        # Set position if specified
        if 'position' in ship_config:
            ship.x = ship_config['position'][0]
            ship.y = ship_config['position'][1]
            ship.position = pygame.math.Vector2(ship.x, ship.y)
        
        # Apply AI strategy if specified
        if 'ai_strategy' in ship_config:
            # TODO: Apply AI strategy
            pass
        
        return ship
    
    def _verify_assertion(self, assertion: TestAssertion, 
                          parser: TestLogParser) -> tuple:
        """
        Verify a single assertion against parsed log.
        
        Returns:
            (passed: bool, message: str)
        """
        atype = assertion.assertion_type
        params = assertion.params
        
        if atype == 'velocity_at_tick':
            ship = params.get('ship', '')
            tick = params.get('tick', 0)
            expected = params.get('expected_speed', 0)
            tolerance = params.get('tolerance', 0.1)
            
            actual = parser.get_velocity_at_tick(ship, tick)
            if actual is None:
                return False, f"No velocity found for {ship} at tick {tick}"
            
            diff = abs(actual - expected)
            if diff <= tolerance:
                return True, f"Speed {actual:.2f} within tolerance of {expected:.2f}"
            else:
                return False, f"Speed {actual:.2f} not within {tolerance} of {expected:.2f}"
        
        elif atype == 'max_speed':
            ship = params.get('ship', '')
            expected = params.get('expected', 0)
            tolerance = params.get('tolerance', 0.1)
            
            actual = parser.get_max_speed_reached(ship)
            diff = abs(actual - expected)
            if diff <= tolerance:
                return True, f"Max speed {actual:.2f} within tolerance of {expected:.2f}"
            else:
                return False, f"Max speed {actual:.2f} not within {tolerance} of {expected:.2f}"
        
        elif atype == 'hit_rate':
            attacker = params.get('attacker')
            target = params.get('target')
            expected_min = params.get('min', 0.0)
            expected_max = params.get('max', 1.0)
            
            rate = parser.get_accuracy_rate(attacker, target)
            if expected_min <= rate <= expected_max:
                return True, f"Hit rate {rate:.2%} within [{expected_min:.2%}, {expected_max:.2%}]"
            else:
                return False, f"Hit rate {rate:.2%} outside [{expected_min:.2%}, {expected_max:.2%}]"
        
        elif atype == 'hit_count':
            attacker = params.get('attacker')
            target = params.get('target')
            expected = params.get('expected', 0)
            
            actual = parser.get_hit_count(attacker, target)
            if actual == expected:
                return True, f"Hit count {actual} matches expected {expected}"
            else:
                return False, f"Hit count {actual} != expected {expected}"
        
        elif atype == 'no_hits':
            attacker = params.get('attacker')
            target = params.get('target')
            
            hits = parser.get_hit_count(attacker, target)
            if hits == 0:
                return True, "No hits as expected"
            else:
                return False, f"Expected 0 hits but got {hits}"

        elif atype == 'position_delta':
            ship = params.get('ship', '')
            start_tick = params.get('start_tick', 0)
            end_tick = params.get('end_tick', 1000)
            max_delta = params.get('max_delta', 0.1)
            min_delta = params.get('min_delta', 0.0)
            
            start_pos = parser.get_position_at_tick(ship, start_tick)
            end_pos = parser.get_position_at_tick(ship, end_tick)
            
            if not start_pos or not end_pos:
                return False, f"Missing position data for {ship}"
                
            dist = math.sqrt((end_pos[0] - start_pos[0])**2 + (end_pos[1] - start_pos[1])**2)
            
            if min_delta <= dist <= max_delta:
                return True, f"Displacement {dist:.2f} within [{min_delta}, {max_delta}]"
            else:
                return False, f"Displacement {dist:.2f} outside [{min_delta}, {max_delta}]"
                
        elif atype == 'heading_change':
            ship = params.get('ship', '')
            tick = params.get('tick', 1000)
            expected_heading = params.get('expected_heading', None)
            min_rotation = params.get('min_rotation', 0.0)
            
            initial_heading = parser.get_velocity_at_tick(ship, 0, param='heading')
            final_heading = parser.get_velocity_at_tick(ship, tick, param='heading')
            
            if initial_heading is None or final_heading is None:
                 return False, f"Missing heading data for {ship}"
                 
            if expected_heading is not None:
                diff = abs(final_heading - expected_heading) % 360
                if diff < 1.0:
                     return True, f"Heading {final_heading} matches {expected_heading}"
                else:
                     return False, f"Heading {final_heading} != {expected_heading}"
            
            total_rotation = abs(final_heading - initial_heading)
            if total_rotation >= min_rotation:
                return True, f"Rotation {total_rotation} >= {min_rotation}"
            else:
                return False, f"Rotation {total_rotation} < {min_rotation}"
        
        else:
            return False, f"Unknown assertion type: {atype}"


@dataclass
class AssertionResult:
    """Result of a single assertion."""
    assertion_type: str
    passed: bool
    message: str


class TestResult:
    """Result of a complete test execution."""
    
    def __init__(self, test_id: str, description: str):
        self.test_id = test_id
        self.description = description
        self.assertion_results: List[AssertionResult] = []
    
    def add_assertion_result(self, atype: str, passed: bool, message: str) -> None:
        self.assertion_results.append(AssertionResult(atype, passed, message))
    
    @property
    def passed(self) -> bool:
        if not self.assertion_results:
            return False
        return all(r.passed for r in self.assertion_results)
    
    def __str__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        lines = [f"[{status}] {self.test_id}: {self.description}"]
        for r in self.assertion_results:
            status_str = "[PASS]" if r.passed else "[FAIL]"
            lines.append(f"  {status_str} {r.assertion_type}: {r.message}")
        return "\n".join(lines)


def run_all_tests(config_dir: str = "unit_tests/simulation/test_configs") -> List[TestResult]:
    """
    Run all test configurations in a directory.
    
    Args:
        config_dir: Directory containing test config JSON files
        
    Returns:
        List of TestResult objects
    """
    runner = ComponentTestRunner()
    results = []
    
    if not os.path.exists(config_dir):
        print(f"Config directory not found: {config_dir}")
        return results
    
    for filename in sorted(os.listdir(config_dir)):
        if filename.endswith('.json'):
            config_path = os.path.join(config_dir, filename)
            try:
                result = runner.run_test(config_path)
                results.append(result)
                print(result)
            except Exception as e:
                print(f"[ERROR] {filename}: {e}")
    
    return results


if __name__ == '__main__':
    # Run all tests when executed directly
    import argparse
    
    parser = argparse.ArgumentParser(description='Run component simulation tests')
    parser.add_argument('--config', '-c', help='Path to single test config file')
    parser.add_argument('--dir', '-d', default='unit_tests/simulation/test_configs',
                        help='Directory containing test configs')
    
    args = parser.parse_args()
    
    if args.config:
        # Run single test
        runner = ComponentTestRunner()
        result = runner.run_test(args.config)
        print(result)
        sys.exit(0 if result.passed else 1)
    else:
        # Run all tests in directory
        results = run_all_tests(args.dir)
        
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        
        print(f"\n{'='*50}")
        print(f"Results: {passed}/{total} tests passed")
        
        sys.exit(0 if passed == total else 1)
