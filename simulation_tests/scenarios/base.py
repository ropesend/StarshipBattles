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
from simulation_tests.scenarios.validation import Check, ValidationReport
from simulation_tests.logging_config import get_logger
from game.core.constants import SimulationConstants

# Get logger for this module
logger = get_logger(__name__)

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
        battle_end_mode: Battle end condition mode - "time_based", "hp_based", "capability",
                        "manual", "escape" (default: "time_based" for tests to run full duration)
        battle_end_check_derelict: Count derelict ships as defeated (for hp_based mode, default: False)
        absolute_max_ticks: Hard ceiling to prevent infinite loops (safety net)
        escape_radius: Distance from origin for "escape" mode
        escape_team: Which team must escape (None = any, 0 or 1 = specific)
        escape_all_ships: Require all ships to escape (default: False)
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
    absolute_max_ticks: int = field(default_factory=lambda: SimulationConstants.ABSOLUTE_MAX_TICKS)
    escape_radius: Optional[float] = None
    escape_team: Optional[int] = None
    escape_all_ships: bool = False
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
            'absolute_max_ticks': self.absolute_max_ticks,
            'escape_radius': self.escape_radius,
            'escape_team': self.escape_team,
            'escape_all_ships': self.escape_all_ships,
            'ui_priority': self.ui_priority,
            'tags': self.tags,
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

    # Position tracking — set to True on scenarios that need path analysis
    track_positions: bool = False

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

        # Store test_id in results for UI display (e.g., propulsion test detection)
        self.results['test_id'] = self.metadata.test_id

        # Position tracking log (populated by _track_tick when track_positions=True)
        self._position_log: Dict[str, list] = {}
        self._tracking_weapon_range: Optional[float] = None

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
        logger.debug(f"Loading ship from dict: {data.get('name', 'Unknown')}")
        logger.debug(f"Ship has {len(data.get('layers', {}).get('CORE', []))} CORE components")

        from game.core.registry import RegistryManager, get_default_registry_provider, GameRegistries
        reg = RegistryManager.instance()
        logger.debug(f"Registry frozen state before Ship.from_dict: {reg._frozen}")

        # Get registries for ship deserialization (PROJ-181: use provider pattern)
        provider = get_default_registry_provider()
        registries = GameRegistries(
            components=provider.get_components(),
            modifiers=provider.get_modifiers(),
            vehicle_classes=provider.get_vehicle_classes(),
            resources=provider.get_resources(),
        )
        ship = Ship.from_dict(data, registries=registries)
        logger.debug("Ship loaded successfully")

        # Ensure stats are calculated
        ship.recalculate_stats()
        logger.debug("Ship stats recalculated")

        # Validate expected_stats if present in ship JSON
        expected_stats = data.get('expected_stats', {})
        if expected_stats:
            validation_errors = self._validate_expected_stats(ship, expected_stats, filename)
            if validation_errors:
                # Log warnings but don't fail - this is for debugging test data
                for error in validation_errors:
                    logger.warning(f"[LOAD VALIDATION] {error}")
                # Store validation results for UI display
                if not hasattr(self, '_load_validation_errors'):
                    self._load_validation_errors = []
                self._load_validation_errors.extend(validation_errors)

        # Note: Resources are initialized automatically by the ship system
        # No manual resource initialization needed

        return ship

    def _validate_expected_stats(self, ship: Ship, expected_stats: dict, filename: str) -> List[str]:
        """
        Validate ship's expected_stats against actual calculated physics values.

        This is a load-time validation that ensures the test data (expected_stats)
        in the ship JSON matches the actual physics calculations. If they don't
        match, the test data is wrong and should be updated.

        Args:
            ship: The loaded Ship instance with calculated stats
            expected_stats: The expected_stats dict from ship JSON
            filename: Ship filename for error messages

        Returns:
            List of validation error messages (empty if all pass)
        """
        errors = []
        tolerance = 1e-6  # Tiny tolerance for floating point comparison

        # Map expected_stats keys to ship attributes
        stat_mapping = {
            'max_speed': 'max_speed',
            'total_thrust': 'total_thrust',
            'turn_speed': 'turn_speed',
            'mass': 'mass',
            'hull_hp': 'hull_hp',
            'max_hp': 'max_hp',
        }

        for stat_name, expected_val in expected_stats.items():
            if stat_name not in stat_mapping:
                # Unknown stat - skip for now (could be custom validation)
                continue

            ship_attr = stat_mapping[stat_name]
            actual_val = getattr(ship, ship_attr, None)

            if actual_val is None:
                errors.append(
                    f"{filename}: Cannot validate '{stat_name}' - ship has no '{ship_attr}' attribute"
                )
                continue

            # Compare values with tiny tolerance
            if abs(actual_val - expected_val) > tolerance:
                errors.append(
                    f"{filename}: expected_stats.{stat_name} mismatch - "
                    f"JSON says {expected_val}, ship has {actual_val} "
                    f"(diff: {actual_val - expected_val:.6f})"
                )

        return errors

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
            TickLimitCondition,
            end_condition_from_dict,
        )

        # If metadata has an explicit end_condition dict, use it
        if hasattr(self.metadata, 'end_condition') and self.metadata.end_condition is not None:
            return end_condition_from_dict(self.metadata.end_condition)

        # Default for tests: time-based (run for full duration)
        return TickLimitCondition(max_ticks=self.metadata.max_ticks)

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

    def validate(self, engine) -> 'List[Check]':
        """
        Return all validation checks for this scenario.

        Subclasses implement this instead of verify(). Each check is tagged
        with a phase ("data", "precondition", "outcome") so the framework
        knows what failed and why.

        Args:
            engine: BattleEngine instance after simulation.

        Returns:
            List of Check objects.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement validate(engine)"
        )

    def collect_results(self, engine):
        """
        Populate measurement attributes before validate() runs.

        Override in templates to calculate derived values (damage_dealt,
        final_velocity, etc.) that validate() checks reference.

        Args:
            engine: BattleEngine instance after simulation.
        """
        pass

    def _run_validation(self, engine) -> 'ValidationReport':
        """
        Run the three-phase validation pipeline.

        1. Calls collect_results(engine) to populate measurement attributes.
        2. Calls validate(engine) to get all Check objects.
        3. Builds a ValidationReport that determines pass/fail.

        Returns:
            ValidationReport with the authoritative pass/fail result.
        """
        self.collect_results(engine)
        checks = self.validate(engine)
        report = ValidationReport(checks=checks)
        self.results['validation'] = report.to_dict()

        # Populate keys the Combat Lab UI reads for rendering
        self.results['validation_results'] = [
            {
                'name': c.name,
                'status': 'PASS' if c.passed else 'FAIL',
                'expected': c.expected,
                'actual': c.actual,
                'p_value': None,
                'tolerance': None,
                'phase': c.phase,
                'detail': c.detail,
            }
            for c in checks
        ]
        summary = report.summary()
        self.results['validation_summary'] = {
            'pass': sum(s['passed'] for s in summary.values()),
            'fail': sum(s['failed'] for s in summary.values()),
            'warn': 0,
            'info': 0,
        }
        self.results['has_validation_failures'] = not report.passed

        return report

    def verify(self, battle_engine) -> bool:
        """
        Legacy pass/fail method. Kept as fallback during migration.

        New scenarios should implement validate() instead.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement validate(engine) or verify(battle_engine)"
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

    # Ship attribute names to discover for tracking, in priority order.
    # First match with a .position attribute is the reference ship for distance.
    _TRACKABLE_SHIPS = [
        ('attacker', True),   # (attr_name, is_reference)
        ('target', False),
        ('ship', True),       # PropulsionScenario / ResourceScenario
        ('ship1', True),      # DuelScenario
        ('ship2', False),
    ]

    def _track_tick(self, tick: int) -> None:
        """Record position data for all discovered ships this tick.

        When ``track_positions`` is False this method returns immediately
        (single bool check — zero overhead).

        Set ``_tracking_weapon_range`` before the first call to get
        per-tick ``in_range`` flags on non-reference ships.

        Args:
            tick: Current simulation tick number.
        """
        if not self.track_positions:
            return

        # Find reference ship (for distance calculations)
        ref_ship = None
        for attr, is_ref in self._TRACKABLE_SHIPS:
            ship = getattr(self, attr, None)
            if ship is not None and hasattr(ship, 'position') and is_ref:
                ref_ship = ship
                break

        # Record each discovered ship
        for attr, is_ref in self._TRACKABLE_SHIPS:
            ship = getattr(self, attr, None)
            if ship is None or not hasattr(ship, 'position'):
                continue

            entry = {
                'tick': tick,
                'x': ship.position.x,
                'y': ship.position.y,
                'speed': getattr(ship, 'current_speed', ship.velocity.length() if hasattr(ship, 'velocity') else 0.0),
                'heading': getattr(ship, 'angle', 0.0),
            }

            # Distance and range for non-reference ships
            if ref_ship is not None and ship is not ref_ship:
                dist = ref_ship.position.distance_to(ship.position)
                entry['dist_to_attacker'] = dist
                if self._tracking_weapon_range is not None:
                    entry['in_range'] = dist <= self._tracking_weapon_range

            self._position_log.setdefault(attr, []).append(entry)

    def _finalize_tracking(self) -> None:
        """Store tracking data and per-ship summaries in ``self.results``.

        Call this from ``collect_results()`` or ``_collect_extra_results()``.
        When tracking is disabled this is a no-op.
        """
        if not self.track_positions or not self._position_log:
            return

        self.results['position_tracks'] = dict(self._position_log)

        summary = {}
        for role, entries in self._position_log.items():
            distances = [e['dist_to_attacker'] for e in entries if 'dist_to_attacker' in e]
            in_range_count = sum(1 for e in entries if e.get('in_range', False))
            out_of_range_count = sum(1 for e in entries if 'in_range' in e and not e['in_range'])

            role_summary = {'ticks_tracked': len(entries)}
            if distances:
                role_summary['min_distance'] = min(distances)
                role_summary['max_distance'] = max(distances)
                role_summary['ticks_in_range'] = in_range_count
                role_summary['ticks_out_of_range'] = out_of_range_count

            summary[role] = role_summary

        self.results['tracking_summary'] = summary

    def _collect_weapon_stats(self, ship: Ship, role: str, engine=None) -> None:
        """
        Collect per-weapon firing statistics from a ship's components.

        Reads the existing ``shots_fired`` and ``shots_hit`` counters that the
        simulation engine maintains on every Component and stores them in
        ``self.results`` under role-prefixed keys.

        When ``engine`` is provided, also counts in-flight projectiles owned
        by this ship so hit rate can be calculated against resolved shots
        only (excluding projectiles that hadn't arrived when the test ended).

        Stored results::

            {role}_total_shots_fired : int
                Ship-level aggregate of all shots fired.
            {role}_weapons : list[dict]
                One entry per weapon component with keys:
                name, type, shots_fired, shots_hit.
            {role}_in_flight : int  (only when engine provided)
                Projectiles still alive at test end, owned by this ship.
            {role}_resolved_shots : int  (only when engine provided)
                total_shots_fired minus in_flight.
            {role}_resolved_hits : int  (only when engine provided)
                Same as total shots_hit (hits are always resolved).

        Args:
            ship: Ship instance whose weapons to inspect.
            role: Prefix for result keys (e.g. ``"attacker"``, ``"target"``).
            engine: Optional BattleEngine for in-flight projectile counting.
        """
        from game.simulation.components.abilities.weapons import WeaponAbility

        self.results[f'{role}_total_shots_fired'] = ship.total_shots_fired

        weapons = []
        total_hits = 0
        for layer_data in ship.layers.values():
            for comp in layer_data.components:
                if not hasattr(comp, 'ability_instances'):
                    continue
                for ab in comp.ability_instances:
                    if isinstance(ab, WeaponAbility):
                        weapons.append({
                            'name': comp.name,
                            'type': ab.__class__.__name__,
                            'shots_fired': comp.shots_fired,
                            'shots_hit': comp.shots_hit,
                        })
                        total_hits += comp.shots_hit
                        break  # one entry per component

        self.results[f'{role}_weapons'] = weapons

        # Count in-flight projectiles (still alive at test end)
        if engine is not None:
            in_flight = sum(
                1 for p in engine.projectiles
                if p.is_alive and p.owner is ship
            )
            self.results[f'{role}_in_flight'] = in_flight
            self.results[f'{role}_resolved_shots'] = ship.total_shots_fired - in_flight
            self.results[f'{role}_resolved_hits'] = total_hits

    def get_ability(self, ship, ability_class_name: str):
        """
        Extract the first ability instance of a given class from a ship.

        Args:
            ship: Ship instance.
            ability_class_name: Class name string (e.g., 'BeamWeaponAbility').

        Returns:
            Ability instance, or None if not found.
        """
        if hasattr(ship, 'layers') and ship.layers:
            for layer_data in ship.layers.values():
                for component in layer_data.components:
                    if hasattr(component, 'ability_instances'):
                        for ability in component.ability_instances:
                            if ability.__class__.__name__ == ability_class_name:
                                return ability
        return None
