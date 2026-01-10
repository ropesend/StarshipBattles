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
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import pygame
from game.simulation.entities.ship import Ship, load_vehicle_classes, LayerType
from game.simulation.components.component import load_components, create_component
from game.simulation.systems.battle_engine import BattleEngine
from game.ai.controller import AIController
from game.core.registry import RegistryManager

from component_test_logger import ComponentTestLogger, TestEventType, enable_test_logging, reset_logging
from log_parser_test_utils import TestLogParser


class TestGrid:
    """Mock grid for AI target finding in tests."""
    def __init__(self, ships: List[Ship]):
        self.ships = ships
        self.width = 10000
        self.height = 10000
        
    def query_radius(self, position, radius):
        """Return all ships within radius (simplified: returns all ships)."""
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
    velocity_log_ticks: List[int] = None
    
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
    """Runs simulation-based component tests."""
    
    def __init__(self, data_dir: str = "tests/unit/data"):
        self.data_dir = data_dir
        self._initialized = False
    
    def _ensure_initialized(self) -> None:
        """Ensure pygame and data files are loaded."""
        if self._initialized: return
        
        pygame.init()
        # Headless-ish
        pygame.display.set_mode((1, 1))
        
        load_vehicle_classes(os.path.join(ROOT_DIR, self.data_dir, "test_vehicleclasses.json"))
        load_components(os.path.join(ROOT_DIR, self.data_dir, "test_components.json"))
        self._initialized = True
    
    def run_test(self, config_path: str) -> 'TestResult':
        self._ensure_initialized()
        config = TestConfig.from_file(config_path)
        
        logger = None
        orig_sys_path = sys.path.copy()
        try:
            # Create logger
            log_filename = f"{config.test_id}.log"
            logger = ComponentTestLogger(log_filename, enabled=True)
            logger.start()
            
            # Load ships
            ships = []
            for ship_config in config.ships:
                ship = self._load_ship(ship_config)
                ships.append(ship)
                logger.log_ship_spawn(ship.name, ship.x, ship.y, ship.ship_class, ship.mass, ship.total_thrust)
            
            logger.log_sim_start(config.test_id, [s.name for s in ships])
            
            grid = TestGrid(ships)
            ai_controllers = {s.name: AIController(s, grid, 2 if s.team_id == 1 else 1) for s in ships}
            ai_strategies = {ships[i].name: config.ships[i].get('ai_strategy', 'do_nothing') for i in range(len(ships))}
            
            # Simulation Loop
            for tick in range(config.duration_ticks + 1):
                logger.set_tick(tick)
                for ship in [s for s in ships if s.is_alive]:
                    strategy = ai_strategies.get(ship.name, 'do_nothing')
                    controller = ai_controllers[ship.name]
                    
                    if not ship.current_target:
                        ship.current_target = controller.find_target()
                    
                    if strategy in controller.behaviors:
                        behavior = controller.behaviors[strategy]
                        if controller.current_behavior != behavior:
                            if behavior: behavior.enter()
                            controller.current_behavior = behavior
                        ship.comp_trigger_pulled = bool(ship.current_target)
                        if behavior: behavior.update(ship.current_target, {})
                    else:
                        ship.ai_strategy = strategy
                        controller.update()
                    
                    ship.update(dt=0.01) # Use fixed dt
                    
                if tick in config.velocity_log_ticks or tick == config.duration_ticks:
                    for ship in ships:
                        logger.log_ship_velocity(ship.name, ship.velocity.x, ship.velocity.y, ship.current_speed, ship.angle)
                        logger.log_ship_position(ship.name, ship.x, ship.y)
                        
            logger.log_sim_end(len([s for s in ships if s.is_alive]))
            logger.close()
            
            parser = TestLogParser(os.path.join(logger.log_dir, log_filename))
            parser.parse()
            
            result = TestResult(config.test_id, config.description)
            for assertion in config.assertions:
                passed, msg = self._verify_assertion(assertion, parser)
                result.add_assertion_result(assertion.assertion_type, passed, msg)
            return result
        finally:
            if logger: logger.close()
            reset_logging()
            RegistryManager.instance().clear()
            pygame.quit()
            sys.path = orig_sys_path
    
    def _load_ship(self, ship_config: Dict[str, Any]) -> Ship:
        if 'file' in ship_config:
            filepath = os.path.join(ROOT_DIR, ship_config['file'])
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            ship = Ship.from_dict(data)
        else:
            ship = Ship(
                name=ship_config.get('name', 'TestShip'),
                x=ship_config.get('position', [0, 0])[0],
                y=ship_config.get('position', [0, 0])[1],
                color=(0, 255, 0),
                ship_class=ship_config.get('ship_class', 'TestS_2L')
            )
            
        if 'position' in ship_config:
            ship.x, ship.y = ship_config['position']
            ship.position = pygame.math.Vector2(ship.x, ship.y)
        ship.recalculate_stats()
        return ship

    def _verify_assertion(self, assertion, parser):
        atype = assertion.assertion_type
        params = assertion.params
        
        if atype == 'velocity_at_tick':
            ship, tick, expected = params['ship'], params['tick'], params['expected_speed']
            actual = parser.get_velocity_at_tick(ship, tick)
            if actual is None: return False, f"No velocity for {ship} at {tick}"
            passed = abs(actual - expected) <= params.get('tolerance', 0.1)
            return passed, f"Speed {actual:.2f} (exp: {expected:.2f})"
        
        elif atype == 'max_speed':
            ship, expected = params['ship'], params['expected']
            actual = parser.get_max_speed_reached(ship)
            passed = abs(actual - expected) <= params.get('tolerance', 0.1)
            return passed, f"Max speed {actual:.2f} (exp: {expected:.2f})"
            
        elif atype == 'hit_rate':
            rate = parser.get_accuracy_rate(params['attacker'], params['target'])
            passed = params.get('min', 0.0) <= rate <= params.get('max', 1.0)
            return passed, f"Hit rate {rate:.2%}"
            
        elif atype == 'hit_count':
            actual = parser.get_hit_count(params['attacker'], params['target'])
            passed = actual == params['expected']
            return passed, f"Hit count {actual} (exp: {params['expected']})"

        elif atype == 'position_delta':
            s_pos = parser.get_position_at_tick(params['ship'], params.get('start_tick', 0))
            e_pos = parser.get_position_at_tick(params['ship'], params.get('end_tick', 1000))
            if not s_pos or not e_pos: return False, "Missing position"
            dist = math.sqrt((e_pos[0]-s_pos[0])**2 + (e_pos[1]-s_pos[1])**2)
            passed = params.get('min_delta', 0.0) <= dist <= params.get('max_delta', 0.1)
            return passed, f"Delta {dist:.2f}"
            
        return False, f"Unknown assertion: {atype}"


@dataclass
class AssertionResult:
    assertion_type: str
    passed: bool
    message: str


class TestResult:
    def __init__(self, test_id, description):
        self.test_id = test_id
        self.description = description
        self.assertion_results = []
    
    def add_assertion_result(self, atype, passed, message):
        self.assertion_results.append(AssertionResult(atype, passed, message))
    
    @property
    def passed(self):
        return all(r.passed for r in self.assertion_results) if self.assertion_results else False
    
    def __str__(self):
        status = "PASS" if self.passed else "FAIL"
        lines = [f"[{status}] {self.test_id}: {self.description}"]
        for r in self.assertion_results:
            lines.append(f"  [{'PASS' if r.passed else 'FAIL'}] {r.assertion_type}: {r.message}")
        return "\n".join(lines)


def run_all_tests(config_dir="tests/unit/simulation/test_configs"):
    runner = ComponentTestRunner()
    results = []
    full_config_dir = os.path.join(ROOT_DIR, config_dir)
    if not os.path.exists(full_config_dir): return results
    
    for filename in sorted(os.listdir(full_config_dir)):
        if filename.endswith('.json'):
            try:
                result = runner.run_test(os.path.join(full_config_dir, filename))
                results.append(result)
                print(result)
            except Exception as e:
                print(f"[ERROR] {filename}: {e}")
    return results


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c')
    parser.add_argument('--dir', '-d', default='tests/unit/simulation/test_configs')
    args = parser.parse_args()
    
    if args.config:
        res = ComponentTestRunner().run_test(args.config)
        print(res)
        sys.exit(0 if res.passed else 1)
    else:
        results = run_all_tests(args.dir)
        passed = sum(1 for r in results if r.passed)
        print(f"\nResults: {passed}/{len(results)} passed")
        sys.exit(0 if len(results) > 0 and passed == len(results) else 1)
