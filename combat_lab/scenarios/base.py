"""
TestScenario Base Class and TestMetadata

This module provides the foundation for creating test scenarios that work
identically in both pytest (headless) and Combat Lab (visual) environments.

Key Design Principle:
    Both pytest and Combat Lab use the EXACT same BattleEngine code.
    The only difference is headless=True (pytest) vs headless=False (Combat Lab).

Architecture:
    - TestScenario is the single base class for all scenarios
    - Carries TestMetadata for rich test documentation
    - Provides helper methods for loading test data
    - Ensures tests are reproducible with fixed seeds

Usage Example (PROJ-270 post-unified-entry contract):
    ```python
    from combat_lab.scenarios.base import TestScenario, TestMetadata
    from combat_lab.scenarios.templates import StaticTargetScenario

    class MyWeaponTest(StaticTargetScenario):
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

        # Template-driven: the template compiles a BattleSpec via to_spec(),
        # run_battle drives it, then wire_ships() binds self.attacker /
        # self.target onto the materialized ships post-start.
        attacker_ship = "Test_Attacker_Beam.json"
        target_ship = "Test_Target.json"
        distance = 50

        def validate(self, outcome, telemetry=None):
            # self.target is wired by the template; outcome.duration_ticks
            # replaces the old engine.tick_counter read.
            return [check_true(
                "Target damaged",
                self.target.hp < self.initial_hp,
                phase="outcome",
            )]
    ```
"""

import os
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from game.simulation.entities.ship import Ship
from combat_lab.scenarios.validation import Check, ValidationReport
from combat_lab.logging_config import get_logger

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
    ui_priority: int = 0
    tags: List[str] = field(default_factory=list)
    # PROJ-269 Phase 5: optional telemetry override. Default string
    # "DETAILED" means the Combat Lab compiler resolves to
    # `TelemetryLevel.DETAILED`. Scenarios can set "MINIMAL" or "NORMAL"
    # for faster batch runs at reduced instrumentation.
    telemetry_level: str = "DETAILED"

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
            'ui_priority': self.ui_priority,
            'tags': self.tags,
        }


class TestScenario:
    """
    Base class for test scenarios that work in both pytest and Combat Lab.

    Provides:
    - Rich metadata for documentation and UI display
    - Helper methods for loading test ships
    - Automatic configuration from metadata
    - Simplified test data paths

    Key Design:
        - Both pytest and Combat Lab use the same BattleEngine
        - Only difference is headless mode (no rendering vs rendering)
        - Tests must be deterministic (use fixed seeds)
        - Test data lives in combat_lab/data/

    Class Attributes:
        metadata: TestMetadata instance describing this test

    Methods to Implement:
        setup(battle_engine): Configure ships and initial state
        verify(battle_engine): Return True if test passed
        update(battle_engine): Optional per-tick logic

    Helper Methods:
        _load_ship(filename): Load ship from combat_lab/data/ships/
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

            # PROJ-270 contract: inherit from StaticTargetScenario (or
            # another template) and override `attacker_ship` / `target_ship`
            # / `distance`. The template's to_spec() + wire_ships() handle
            # ship materialization; validate() receives outcome + telemetry.

            attacker_ship = 'Test_Attacker_Beam.json'
            target_ship = 'Test_Target.json'
            distance = 50

            def validate(self, outcome, telemetry=None):
                damage_dealt = self.initial_hp - self.target.hp
                return [check_true("Damage dealt", damage_dealt > 0,
                                   phase="outcome")]
        ```
    """

    # Subclasses must define this
    metadata: TestMetadata = None

    # Position tracking — set to True on scenarios that need path analysis
    track_positions: bool = False

    def __init__(self):
        """Initialize test scenario from metadata."""
        if self.metadata is None:
            raise ValueError(
                f"{self.__class__.__name__} must define a 'metadata' class attribute"
            )

        # Result state
        self.passed: bool = False
        self.results: Dict[str, Any] = {}

        # Configure scenario from metadata
        self.name = f"[{self.metadata.test_id}] {self.metadata.name}"
        self.description = self.metadata.summary
        self.max_ticks = self.metadata.max_ticks

        # Store test_id in results for UI display (e.g., propulsion test detection)
        self.results['test_id'] = self.metadata.test_id

        # Position tracking log (populated by _track_tick when track_positions=True)
        self._position_log: Dict[str, list] = {}
        self._tracking_weapon_range: Optional[float] = None

        # Set test data paths - use combat_lab/data
        data_dir = self._get_test_data_dir()
        self.components_path = os.path.join(data_dir, 'components.json')
        self.modifiers_path = os.path.join(data_dir, 'modifiers.json')
        self.vehicle_classes_path = os.path.join(data_dir, 'vehicleclasses.json')

    def get_data_paths(self) -> Dict[str, str]:
        """Return the data paths this scenario loads before running."""
        return {
            'components': self.components_path,
            'modifiers': self.modifiers_path,
            'vehicle_classes': self.vehicle_classes_path,
        }

    def _get_test_data_dir(self) -> str:
        """
        Get absolute path to combat_lab/data directory.

        Returns:
            Absolute path to test data directory
        """
        # Get combat_lab directory
        # This file is in combat_lab/scenarios/base.py
        scenarios_dir = os.path.dirname(os.path.abspath(__file__))
        combat_lab_dir = os.path.dirname(scenarios_dir)
        return os.path.join(combat_lab_dir, 'data')

    def _get_test_data_path(self, relative_path: str) -> str:
        """
        Get absolute path to a test data file.

        Args:
            relative_path: Path relative to combat_lab/data/

        Returns:
            Absolute path to the file

        Example:
            path = self._get_test_data_path('ships/Test_Attacker.json')
        """
        return os.path.join(self._get_test_data_dir(), relative_path)

    def _load_ship(self, filename: str) -> Ship:
        """
        Load a ship from a JSON file in combat_lab/data/ships/.

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
                f"Available ships should be in combat_lab/data/ships/"
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

        from game.core.registry import get_default_registry_manager, get_default_registry_provider, GameRegistries
        reg = get_default_registry_manager()
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
            "movement_policy": "test_do_nothing",
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

        This helper builds a default time-based BattleEndCondition for the
        BattleEngine. Scenarios that need a different condition can attach an
        ``end_condition`` dict directly to their metadata.

        Returns:
            BattleEndCondition configured from metadata

        Example:
            # Used by template spec compilers to build the BattleSpec's
            # end_condition field. Template-driven scenarios don't need
            # to call this directly.
            end_condition = self._create_end_condition()
        """
        from game.simulation.systems.battle_end_conditions import (
            TickLimitCondition,
            end_condition_from_dict,
        )

        # If a scenario subclass attaches an explicit end_condition dict, use it
        if hasattr(self.metadata, 'end_condition') and self.metadata.end_condition is not None:
            return end_condition_from_dict(self.metadata.end_condition)

        # Default for tests: time-based (run for full duration)
        return TickLimitCondition(max_ticks=self.metadata.max_ticks)


    def validate(self, outcome, telemetry=None) -> 'List[Check]':
        """
        Return all validation checks for this scenario.

        Subclasses implement this instead of verify(). Each check is tagged
        with a phase ("data", "precondition", "outcome") so the framework
        knows what failed and why.

        PROJ-270 Phase 2.5: rewritten to consume `BattleOutcome` +
        `CombatLabTelemetry` instead of a live `BattleEngine` reference.
        `outcome.duration_ticks` replaces `engine.tick_counter`; forensic
        data (in-flight projectiles) comes from `telemetry`.

        Args:
            outcome: `BattleOutcome` from `run_battle`.
            telemetry: Optional `CombatLabTelemetry` bundle (None when
                forensic data isn't needed).

        Returns:
            List of Check objects.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement validate(outcome, telemetry)"
        )

    def collect_results(self, outcome, telemetry=None):
        """
        Populate measurement attributes before validate() runs.

        Override in templates to calculate derived values (damage_dealt,
        final_velocity, etc.) that validate() checks reference.

        PROJ-270 Phase 2.5: rewritten to consume outcome + telemetry.

        Args:
            outcome: `BattleOutcome` from `run_battle`.
            telemetry: Optional `CombatLabTelemetry` bundle.
        """
        pass

    def custom_setup(self, battle_engine) -> None:
        """Optional per-scenario setup hook called by template setup().

        Override in subclasses of StaticTargetScenario / DuelScenario /
        PropulsionScenario / ResourceScenario to tweak ship state after the
        template has positioned the ships but before the battle starts.
        """
        pass

    def before_run_battle(self, spec) -> None:
        """Pre-run hook called BEFORE `run_battle(spec)` fires.

        Used by templates that need to perform work ahead of the main
        battle (e.g. `ComparisonScenario` runs its private baseline
        battle here so ship-creation ordering matches the legacy path).
        Base implementation is a no-op.
        """
        _ = spec

    def wire_ships(self, ships_by_role, *, engine=None, initial_state=None):
        """Wire materialized Ships onto the scenario (PROJ-269 Task 6.7a).

        Called by `combat_lab/runner.py::_run_scenario_via_battle_runner`
        after ships are built and the engine has started, to replace the
        template-level side-effect wiring that used to happen inside
        `setup()`.

        Templates (StaticTarget / Duel / Propulsion / Resource /
        Comparison) override this to cache ship refs, compute initial
        state (hp, resources), and assign movement policies. The base
        implementation is a no-op for non-template scenarios.

        **PROJ-280 authoring rule:** template overrides should call
        `self._snapshot_initial_state(ships_by_role, initial_state)` at
        the top to handle the role-caching + initial-HP/resource snapshot
        boilerplate, then perform their template-specific policy
        assignment + hooks. See `StaticTargetScenario.wire_ships` for the
        canonical pattern.

        Args:
            ships_by_role: Mapping of role name (e.g. "attacker",
                "target", "ship1", "ship") to materialized Ship.
            engine: The BattleEngine post-start. Passed so templates
                that have post-wiring engine hooks (like
                ComparisonScenario.configure_variant) can use it.
            initial_state: Optional per-role dict of pre-engine-start
                snapshots (`{role: {'hp': ..., 'resources': {...}}}`).
                Resource-sensitive templates use this to capture values
                before `engine.start()` has drained any.
        """
        _ = ships_by_role, engine, initial_state

    # ------------------------------------------------------------------
    # PROJ-280 — Shared template lifecycle helpers + enforcement
    # ------------------------------------------------------------------

    def _common_preconditions(self) -> 'List[Check]':
        """Universal precondition checks every template must run (PROJ-280).

        Currently a single check: the simulation ran for at least one
        tick. Templates extend by calling this from
        `_template_preconditions()` and appending their own checks.

        Sets `self._preconditions_base_called = True` as a sentinel that
        `_run_validation` reads to enforce the authoring rule "subclass
        overrides of `_template_preconditions` MUST call
        `super()._template_preconditions()` (which calls this) or
        `self._common_preconditions()` directly."
        """
        from combat_lab.scenarios.validation import check_true

        self._preconditions_base_called = True
        checks = []
        ticks = self.results.get('ticks_run', 0)
        checks.append(check_true(
            "Simulation Ran",
            ticks > 0,
            actual=ticks,
        ))
        return checks

    def _template_preconditions(self) -> 'List[Check]':
        """Template-level precondition checks (PROJ-280).

        Default: returns `_common_preconditions()`. Templates that need
        additional template-specific checks (e.g. `PropulsionScenario`'s
        movement/rotation validation) override this AND must include the
        common checks via `super()._template_preconditions()` or
        `self._common_preconditions()` — otherwise the
        `_run_validation` sentinel raises a loud `RuntimeError`.
        """
        return self._common_preconditions()

    def _snapshot_initial_state(
        self, ships_by_role: dict, initial_state: 'Optional[dict]' = None,
    ) -> None:
        """Snapshot pre-engine-start state into scenario attributes (PROJ-280).

        Default: no-op. Each template overrides this to define its
        role-to-attribute mapping (`self.attacker = ships_by_role["attacker"]`,
        `self.initial_hp = _pre_start_hp(initial_state, "target", ...)`,
        etc.) — extracts the boilerplate snapshot phase out of
        `wire_ships()` so the override only contains the template-specific
        policy assignment.

        Templates' `wire_ships(...)` override should call this at the top
        before doing template-specific policy work. Concrete scenarios
        that override `wire_ships` in non-canonical ways
        (`ExternalBattleConditionApplied`, `PropThrustMassRatioScenario`)
        may skip the helper — it is opt-in.
        """
        _ = ships_by_role, initial_state

    def _collect_extra_results(self, outcome, telemetry=None) -> None:
        """Optional hook for templates to attach scenario-specific metrics.

        Override in subclasses when the template's default result collection
        does not capture everything ``validate()`` needs.
        """
        pass

    def _run_validation(self, outcome, telemetry=None) -> 'ValidationReport':
        """
        Run the three-phase validation pipeline.

        1. Calls collect_results(outcome, telemetry) to populate measurement attributes.
        2. Calls validate(outcome, telemetry) to get all Check objects.
        3. Builds a ValidationReport that determines pass/fail.

        PROJ-280 enforcement: if the scenario's class overrides
        `_template_preconditions`, the override MUST call
        `super()._template_preconditions()` or `self._common_preconditions()` —
        otherwise the universal "Simulation Ran" check is silently skipped.
        We detect missing super-call via a sentinel flag set inside
        `_common_preconditions()` and raise `RuntimeError` if the override
        ran but the sentinel never flipped. Subclasses that don't override
        `_template_preconditions` get the base behavior automatically and
        the sentinel check is skipped.
        """
        self.collect_results(outcome, telemetry)

        # PROJ-280 sentinel: reset before validate(), check after.
        overrides_preconditions = '_template_preconditions' in self.__class__.__dict__
        if overrides_preconditions:
            self._preconditions_base_called = False

        checks = self.validate(outcome, telemetry)

        if overrides_preconditions and not getattr(
            self, '_preconditions_base_called', False
        ):
            raise RuntimeError(
                f"{self.__class__.__name__}._template_preconditions() must "
                f"call super()._template_preconditions() or "
                f"self._common_preconditions() (PROJ-280). The universal "
                f"'Simulation Ran' check was silently skipped."
            )
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

    def _collect_weapon_stats(self, ship: Ship, role: str, telemetry=None) -> None:
        """
        Collect per-weapon firing statistics from a ship's components.

        Reads the existing ``shots_fired`` and ``shots_hit`` counters that the
        simulation engine maintains on every Component and stores them in
        ``self.results`` under role-prefixed keys.

        When ``telemetry`` is provided, also counts in-flight projectiles owned
        by this ship so hit rate can be calculated against resolved shots
        only (excluding projectiles that hadn't arrived when the test ended).

        Stored results::

            {role}_total_shots_fired : int
                Ship-level aggregate of all shots fired.
            {role}_weapons : list[dict]
                One entry per weapon component with keys:
                name, type, shots_fired, shots_hit.
            {role}_in_flight : int  (only when telemetry provided)
                Projectiles still alive at test end, owned by this ship.
            {role}_resolved_shots : int  (only when telemetry provided)
                total_shots_fired minus in_flight.
            {role}_resolved_hits : int  (only when telemetry provided)
                Same as total shots_hit (hits are always resolved).

        Args:
            ship: Ship instance whose weapons to inspect.
            role: Prefix for result keys (e.g. ``"attacker"``, ``"target"``).
            telemetry: Optional CombatLabTelemetry for in-flight projectile counts.
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

        # Count in-flight projectiles (still alive at test end) from telemetry.
        # PROJ-270 Phase 2.5: telemetry bundle replaces live `engine.projectiles`.
        if telemetry is not None:
            in_flight = telemetry.in_flight_for(role)
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
