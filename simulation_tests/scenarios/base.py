"""
TestScenario Base Class and TestMetadata

This module provides the foundation for creating test scenarios that work
identically in both pytest (headless) and Combat Lab (visual) environments.

Key Design Principle:
    Both pytest and Combat Lab use the EXACT same BattleEngine code.
    The only difference is headless=True (pytest) vs headless=False (Combat Lab).

Architecture:
    - TestScenario extends CombatScenario from test_framework.scenario
    - Adds TestMetadata for rich test documentation
    - Provides helper methods for loading test data
    - Ensures tests are reproducible with fixed seeds

Usage Example:
    ```python
    from simulation_tests.scenarios.base import TestScenario, TestMetadata

    class MyWeaponTest(TestScenario):
        metadata = TestMetadata(
            test_id="BEAM-001",
            category="Weapons",
            subcategory="Beam Accuracy",
            name="Point-blank beam test",
            summary="Validates beam hits at close range",
            conditions=["Distance: 50px", "Stationary target"],
            edge_cases=["Minimum range"],
            expected_outcome="Beam should hit consistently",
            pass_criteria="Hit rate > 90%",
            max_ticks=500,
            seed=42
        )

        def setup(self, battle_engine):
            attacker = self._load_ship('Test_Attacker_Beam.json')
            target = self._load_ship('Test_Target.json')

            attacker.position = pygame.math.Vector2(0, 0)
            target.position = pygame.math.Vector2(50, 0)

            battle_engine.start([attacker], [target], seed=self.metadata.seed)

        def verify(self, battle_engine):
            # Check if test passed
            return battle_engine.teams[1][0].hp < initial_hp
    ```
"""

import os
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from test_framework.scenario import CombatScenario
from game.simulation.entities.ship import Ship


@dataclass
class TestMetadata:
    """
    Metadata describing a test scenario.

    This metadata serves multiple purposes:
    1. Documentation: Clear description of what the test validates
    2. Organization: Categorization for filtering and grouping
    3. UI Display: Rich information for Combat Lab interface
    4. Traceability: Links tests to requirements and edge cases

    Attributes:
        test_id: Unique identifier (e.g., "BEAM-001", "PROP-042")
        category: Major category (e.g., "Weapons", "Propulsion", "Abilities")
        subcategory: Specific area (e.g., "Beam Accuracy", "Engine Physics")
        name: Short descriptive name (e.g., "Point-blank beam test")
        summary: Brief 1-2 sentence description of the test
        conditions: List of test conditions (e.g., ["Distance: 50px", "Stationary target"])
        edge_cases: Edge cases being tested (e.g., ["Minimum range", "Zero velocity"])
        expected_outcome: What should happen (e.g., "Beam hits consistently")
        pass_criteria: How we verify success (e.g., "Hit rate > 90%")
        max_ticks: Maximum simulation ticks before timeout (default: 1000)
        seed: Random seed for reproducibility (default: 42)
        battle_end_mode: Battle end condition mode - "time_based", "hp_based", "capability", "manual"
                        (default: "time_based" for tests to run full duration)
        battle_end_check_derelict: Count derelict ships as defeated (for hp_based mode, default: False)
        ui_priority: Display priority in Combat Lab (0=normal, higher=more important)
        tags: Optional tags for filtering (e.g., ["accuracy", "close_range"])
    """
    test_id: str
    category: str
    subcategory: str
    name: str
    summary: str
    conditions: List[str]
    edge_cases: List[str]
    expected_outcome: str
    pass_criteria: str
    max_ticks: int = 1000
    seed: int = 42
    battle_end_mode: str = "time_based"  # Default: run for full duration
    battle_end_check_derelict: bool = False
    ui_priority: int = 0
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary for serialization."""
        return {
            'test_id': self.test_id,
            'category': self.category,
            'subcategory': self.subcategory,
            'name': self.name,
            'summary': self.summary,
            'conditions': self.conditions,
            'edge_cases': self.edge_cases,
            'expected_outcome': self.expected_outcome,
            'pass_criteria': self.pass_criteria,
            'max_ticks': self.max_ticks,
            'seed': self.seed,
            'battle_end_mode': self.battle_end_mode,
            'battle_end_check_derelict': self.battle_end_check_derelict,
            'ui_priority': self.ui_priority,
            'tags': self.tags
        }


class TestScenario(CombatScenario):
    """
    Base class for test scenarios that work in both pytest and Combat Lab.

    This class extends CombatScenario with:
    - Rich metadata for documentation and UI display
    - Helper methods for loading test ships
    - Automatic configuration from metadata
    - Simplified test data paths

    Key Design:
        - Both pytest and Combat Lab use the same BattleEngine
        - Only difference is headless mode (no rendering vs rendering)
        - Tests must be deterministic (use fixed seeds)
        - Test data lives in simulation_tests/data/

    Class Attributes:
        metadata: TestMetadata instance describing this test

    Methods to Implement:
        setup(battle_engine): Configure ships and initial state
        verify(battle_engine): Return True if test passed
        update(battle_engine): Optional per-tick logic

    Helper Methods:
        _load_ship(filename): Load ship from simulation_tests/data/ships/
        _get_test_data_path(relative_path): Get absolute path to test data

    Example:
        ```python
        class BeamPointBlankTest(TestScenario):
            metadata = TestMetadata(
                test_id="BEAM-001",
                category="Weapons",
                subcategory="Beam Accuracy",
                name="Point-blank accuracy",
                summary="Validates beam weapons hit at minimum range",
                conditions=["Distance: 50px"],
                edge_cases=["Minimum range"],
                expected_outcome="Consistent hits",
                pass_criteria="Damage dealt > 0",
                max_ticks=500
            )

            def setup(self, battle_engine):
                attacker = self._load_ship('Test_Attacker_Beam.json')
                target = self._load_ship('Test_Target.json')

                import pygame
                attacker.position = pygame.math.Vector2(0, 0)
                target.position = pygame.math.Vector2(50, 0)

                battle_engine.start([attacker], [target], seed=self.metadata.seed)
                self.initial_hp = target.hp

            def verify(self, battle_engine):
                target = battle_engine.teams[1][0]
                damage_dealt = self.initial_hp - target.hp
                return damage_dealt > 0
        ```
    """

    # Subclasses must define this
    metadata: TestMetadata = None

    def __init__(self):
        """Initialize test scenario from metadata."""
        super().__init__()

        if self.metadata is None:
            raise ValueError(
                f"{self.__class__.__name__} must define a 'metadata' class attribute"
            )

        # Configure scenario from metadata
        self.name = f"[{self.metadata.test_id}] {self.metadata.name}"
        self.description = self.metadata.summary
        self.max_ticks = self.metadata.max_ticks

        # Set test data paths - use simulation_tests/data
        data_dir = self._get_test_data_dir()
        self.components_path = os.path.join(data_dir, 'components.json')
        self.modifiers_path = os.path.join(data_dir, 'modifiers.json')
        self.vehicle_classes_path = os.path.join(data_dir, 'vehicleclasses.json')

    def _get_test_data_dir(self) -> str:
        """
        Get absolute path to simulation_tests/data directory.

        Returns:
            Absolute path to test data directory
        """
        # Get simulation_tests directory
        # This file is in simulation_tests/scenarios/base.py
        scenarios_dir = os.path.dirname(os.path.abspath(__file__))
        simulation_tests_dir = os.path.dirname(scenarios_dir)
        return os.path.join(simulation_tests_dir, 'data')

    def _get_test_data_path(self, relative_path: str) -> str:
        """
        Get absolute path to a test data file.

        Args:
            relative_path: Path relative to simulation_tests/data/

        Returns:
            Absolute path to the file

        Example:
            path = self._get_test_data_path('ships/Test_Attacker.json')
        """
        return os.path.join(self._get_test_data_dir(), relative_path)

    def _load_ship(self, filename: str) -> Ship:
        """
        Load a ship from a JSON file in simulation_tests/data/ships/.

        This helper simplifies loading pre-built test ships. The ship is
        fully loaded with components and stats recalculated.

        Args:
            filename: Name of ship file (e.g., 'Test_Attacker_Beam.json')

        Returns:
            Fully configured Ship instance

        Raises:
            FileNotFoundError: If ship file doesn't exist
            json.JSONDecodeError: If ship file is invalid JSON

        Example:
            attacker = self._load_ship('Test_Attacker_Beam360_High.json')
            target = self._load_ship('Test_Target_Stationary.json')
        """
        ship_path = self._get_test_data_path(os.path.join('ships', filename))

        if not os.path.exists(ship_path):
            raise FileNotFoundError(
                f"Ship file not found: {ship_path}\n"
                f"Available ships should be in simulation_tests/data/ships/"
            )

        try:
            with open(ship_path, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in ship file {filename}: {e.msg}",
                e.doc,
                e.pos
            )

        # Load ship from dictionary
        print(f"DEBUG: Loading ship from dict: {data.get('name', 'Unknown')}")
        print(f"DEBUG: Ship has {len(data.get('layers', {}).get('CORE', []))} CORE components")

        from game.core.registry import RegistryManager
        reg = RegistryManager.instance()
        print(f"DEBUG: Registry frozen state before Ship.from_dict: {reg._frozen}")

        ship = Ship.from_dict(data)
        print(f"DEBUG: Ship loaded successfully")

        # Ensure stats are calculated
        ship.recalculate_stats()
        print(f"DEBUG: Ship stats recalculated")

        # Note: Resources are initialized automatically by the ship system
        # No manual resource initialization needed

        return ship

    def _create_ship_with_components(self, component_ids: List[str], name: str = "Test Ship") -> Ship:
        """
        Create a minimal ship with specified components.

        This helper creates a basic ship configuration with only the specified
        components, useful for testing specific component interactions without
        needing pre-built ship JSON files.

        Args:
            component_ids: List of component IDs to add to the ship
            name: Name for the ship (default: "Test Ship")

        Returns:
            Fully configured Ship instance with specified components

        Example:
            # Create ship with beam weapon and small energy storage
            attacker = self._create_ship_with_components(
                ["test_beam_med_acc", "test_storage_energy_small"],
                "Limited Energy Attacker"
            )
        """
        ship_data = {
            "name": name,
            "color": [255, 0, 0],
            "team_id": 1,
            "ship_class": "TestS_2L",
            "theme_id": "Federation",
            "ai_strategy": "test_do_nothing",
            "layers": {
                "CORE": [{"id": cid} for cid in component_ids],
                "ARMOR": []
            }
        }

        # Load ship from dictionary
        ship = Ship.from_dict(ship_data)

        # Ensure stats are calculated
        ship.recalculate_stats()

        return ship

    def _create_end_condition(self):
        """
        Create BattleEndCondition from test metadata.

        This helper converts the metadata's battle_end_mode string into
        a BattleEndCondition object for the BattleEngine.

        Returns:
            BattleEndCondition configured from metadata

        Raises:
            ValueError: If battle_end_mode is invalid

        Example:
            # In setup():
            end_condition = self._create_end_condition()
            battle_engine.start([attacker], [target],
                              seed=self.metadata.seed,
                              end_condition=end_condition)
        """
        from game.simulation.systems.battle_end_conditions import (
            BattleEndCondition, BattleEndMode
        )

        # Convert string mode to enum
        try:
            mode = BattleEndMode(self.metadata.battle_end_mode)
        except ValueError:
            raise ValueError(
                f"Invalid battle_end_mode '{self.metadata.battle_end_mode}'. "
                f"Valid modes: {[m.value for m in BattleEndMode]}"
            )

        # Create condition with appropriate parameters
        return BattleEndCondition(
            mode=mode,
            max_ticks=self.metadata.max_ticks if mode == BattleEndMode.TIME_BASED else None,
            check_derelict=self.metadata.battle_end_check_derelict
        )

    def setup(self, battle_engine):
        """
        Configure the battle engine with ships and initial state.

        Subclasses MUST implement this method.

        Args:
            battle_engine: BattleEngine instance to configure

        Example:
            def setup(self, battle_engine):
                attacker = self._load_ship('Test_Attacker.json')
                target = self._load_ship('Test_Target.json')

                import pygame
                attacker.position = pygame.math.Vector2(0, 0)
                target.position = pygame.math.Vector2(100, 0)

                battle_engine.start([attacker], [target], seed=self.metadata.seed)
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement setup(battle_engine)"
        )

    def verify(self, battle_engine) -> bool:
        """
        Check if the test passed.

        Subclasses MUST implement this method.

        Args:
            battle_engine: BattleEngine instance to verify

        Returns:
            True if test passed, False otherwise

        Example:
            def verify(self, battle_engine):
                target = battle_engine.teams[1][0]
                damage_dealt = self.initial_hp - target.hp
                return damage_dealt > 0
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement verify(battle_engine)"
        )

    def update(self, battle_engine):
        """
        Optional per-tick update logic.

        Override this if you need custom behavior during simulation
        (e.g., spawning reinforcements, changing AI behavior, etc.)

        Args:
            battle_engine: BattleEngine instance being updated

        Example:
            def update(self, battle_engine):
                # Spawn reinforcement at tick 100
                if battle_engine.tick_counter == 100:
                    reinforcement = self._load_ship('Reinforcement.json')
                    reinforcement.position = pygame.math.Vector2(500, 0)
                    battle_engine.add_ship(reinforcement, team=1)
        """
        pass

    def get_metadata_dict(self) -> Dict[str, Any]:
        """
        Get metadata as dictionary for serialization.

        Returns:
            Dictionary containing all test metadata
        """
        return self.metadata.to_dict()
