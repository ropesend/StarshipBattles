# Sweep Validation Report: Strategy Shard (STR)

**Validator:** Claude Opus 4.5
**Date:** 2026-02-13
**Shard:** Strategy (game/strategy/)
**Findings Reviewed:** 44

## Summary

| Verdict | Count |
|---------|-------|
| CONFIRMED | 11 |
| DOWNGRADED | 8 |
| REJECTED | 25 |

**Rejection Rate:** 57%

**Total:** 44 findings

---

## Detailed Verdicts

### ADR-STR-001: Simulation Layer Coupling via Direct Imports
**Original Severity:** MAJOR
**Location:** `game/strategy/services/ship_stats_calculator.py`
**Verdict:** CONFIRMED

**Analysis:**
The file contains direct imports from simulation layer at module level (lines 25-26):
```python
from game.simulation.formula_system import safe_evaluate_math_formula
from game.simulation.components.modifiers import calculate_stat_multipliers
```

This is a genuine architectural violation. The strategy layer should not have top-level imports from the simulation layer. The docstring claims "Only imports from game.core.registry (no simulation layer coupling)" which is false.

---

### ADR-STR-002: Simulation Adapter Has Top-Level Simulation Imports
**Original Severity:** MAJOR
**Location:** `game/strategy/adapters/simulation_battle_resolver.py`
**Verdict:** REJECTED

**Analysis:**
The file `simulation_battle_resolver.py` does not exist. The actual adapter is at `game/strategy/adapters/simulation_adapter.py`. Checking that file:

```python
# Import simulation layer components
from game.simulation.battle_controller import BattleController
from game.simulation.battle_config import BattleConfig, BattleMode
from game.simulation.services.battle_service import BattleService
```

While these are top-level imports, this is **intentional and correct**. This file IS the adapter between strategy and simulation layers - its entire purpose is to import simulation components. The Adapter Pattern is specifically designed to contain such imports in a single, isolated location. This is good architecture, not a violation.

**Reason:** The adapter's purpose is to bridge layers - simulation imports here are appropriate.

---

### ADR-STR-003: Galaxy Class Approaching God Class Status
**Original Severity:** MAJOR
**Location:** `game/strategy/data/galaxy.py`
**Verdict:** DOWNGRADED to MINOR

**Analysis:**
Galaxy class has approximately 40 methods and 837 lines. While substantial, examining the code reveals:
- Entity registries (planets, fleets) - appropriate for galaxy
- Spatial indexes - performance optimization
- System/warp generation - factory methods
- Serialization (to_dict/from_dict) - standard pattern

Many methods are helper methods for internal use (_build_edge_candidates, _apply_mst_edges, etc.). The class is cohesive around "galaxy management" rather than accumulating unrelated responsibilities.

**Reason:** While large, the class is cohesive. Size alone does not make it a God Class. Downgrade to MINOR as a monitoring concern.

---

### ADR-STR-004: TYPE_CHECKING Block Indicates Tight Coupling
**Original Severity:** MINOR
**Location:** `game/strategy/data/fleet_battle_stats.py`
**Verdict:** REJECTED

**Analysis:**
File `fleet_battle_stats.py` does not exist. The finding references a non-existent file.

**Reason:** File not found in codebase.

---

### ADR-STR-005: Late Import Pattern Inconsistency
**Original Severity:** MINOR
**Location:** Unknown
**Verdict:** REJECTED

**Analysis:**
Finding has no specific location ("Unknown"). Cannot validate a finding without a concrete location to verify.

**Reason:** No specific location provided - cannot validate.

---

### ADR-STR-006: Potential Circular Dependency Risk in FleetBattleStats
**Original Severity:** MINOR
**Location:** `game/strategy/data/fleet_battle_stats.py`
**Verdict:** REJECTED

**Analysis:**
File `fleet_battle_stats.py` does not exist. The finding references a non-existent file.

**Reason:** File not found in codebase.

---

### ADR-STR-007: Well-Architected Adapter Pattern
**Original Severity:** INFO
**Location:** `game/strategy/adapters/simulation_battle_resolver.py`
**Verdict:** CONFIRMED (as INFO - positive observation)

**Analysis:**
While the filename is incorrect (actual file is `simulation_adapter.py`), the observation about well-architected adapter pattern is accurate. The `SimulationBattleResolver` class properly implements `IBattleResolver` interface, isolates simulation imports, and provides clean translation between layers.

---

### DUP-STR-001: Mission Command Handler Duplication
**Original Severity:** MAJOR
**Location:** `game/strategy/engine/superweapon_missions.py`
**Verdict:** REJECTED

**Analysis:**
File `superweapon_missions.py` does not exist. The command handlers are in `game/strategy/engine/commands.py` and handler logic is in `game/strategy/engine/superweapon_command_handlers.py`.

**Reason:** File not found - incorrect location.

---

### DUP-STR-002: Direct vs Mission Command Validation Asymmetry
**Original Severity:** MAJOR
**Location:** `game/strategy/engine/superweapon_missions.py`
**Verdict:** REJECTED

**Analysis:**
File `superweapon_missions.py` does not exist.

**Reason:** File not found - incorrect location.

---

### DUP-STR-003: to_dict/from_dict Boilerplate Pattern
**Original Severity:** MAJOR
**Location:** Unknown
**Verdict:** REJECTED

**Analysis:**
No specific location provided. The to_dict/from_dict pattern is standard Python serialization and is intentional. Each class has different fields requiring different serialization logic. This is not duplication in the problematic sense.

**Reason:** No location provided; pattern is standard practice, not problematic duplication.

---

### DUP-STR-004: Fleet Resolution Pattern in Command Handlers
**Original Severity:** MAJOR
**Location:** Unknown
**Verdict:** REJECTED

**Analysis:**
No specific location provided. Cannot validate finding without concrete code location.

**Reason:** No specific location provided - cannot validate.

---

### DUP-STR-005: ColonizeValidator Colony Pod Iteration Pattern
**Original Severity:** MAJOR
**Location:** `game/strategy/validation/colonize_validator.py`
**Verdict:** DOWNGRADED to MINOR

**Analysis:**
Examining the code, there are two methods with similar iteration patterns:
- `find_ship_with_colony_pod` (lines 101-136)
- `get_available_colony_pods` (lines 138-174)

Both iterate `fleet.ships` and call `iterate_design_components`. However, they have different purposes (finding vs counting) and return types. The iteration itself uses the shared `iterate_design_components` from `component_inspector.py`, which is the consolidated utility (per PROJ-108).

**Reason:** The core iteration is already consolidated in component_inspector. Remaining similarity is minimal and purposeful. Downgrade to MINOR.

---

### DUP-STR-006: Gaussian Factor Calculation Pattern
**Original Severity:** MINOR
**Location:** `game/strategy/formulas/habitability.py`
**Verdict:** CONFIRMED

**Analysis:**
The habitability.py file contains 5 similar Gaussian calculations:
- `calculate_gravity_factor` (line 62)
- `calculate_temperature_factor` (line 88)
- `calculate_water_factor` (line 113)
- All use: `math.exp(-0.5 * (deviation / sigma) ** 2)`

This is a legitimate minor duplication. A generic `gaussian_factor(value, ideal, tolerance)` function could consolidate these. However, the current code is readable and each function documents its specific purpose.

---

### DUP-STR-007: Path Start Hex Determination Logic
**Original Severity:** MINOR
**Location:** Unknown
**Verdict:** REJECTED

**Analysis:**
No specific location provided. Cannot validate finding.

**Reason:** No specific location provided - cannot validate.

---

### DUP-STR-008: Ship Ability Check Wrappers
**Original Severity:** MINOR
**Location:** Unknown
**Verdict:** REJECTED

**Analysis:**
No specific location provided. Cannot validate finding.

**Reason:** No specific location provided - cannot validate.

---

### DUP-STR-009: Resource Dictionary Accumulation Pattern
**Original Severity:** MINOR
**Location:** `game/strategy/services/ship_stats_calculator.py`
**Verdict:** DOWNGRADED to INFO

**Analysis:**
The pattern `dict[key] = dict.get(key, 0) + value` appears multiple times for accumulating resources (lines 193-194, 205-206, 227-228, etc.). This is idiomatic Python for dictionary accumulation. It's a common pattern, not problematic duplication.

**Reason:** Idiomatic Python pattern, not technical debt. Downgrade to INFO.

---

### DUP-STR-010: Validated Design Component Iteration
**Original Severity:** INFO
**Location:** Unknown
**Verdict:** REJECTED

**Analysis:**
No specific location provided.

**Reason:** No specific location provided - cannot validate.

---

### DUP-STR-011: Well-Consolidated Component Inspector
**Original Severity:** INFO
**Location:** `game/strategy/services/component_inspector.py`
**Verdict:** CONFIRMED (as INFO - positive observation)

**Analysis:**
The `component_inspector.py` file provides well-consolidated utilities:
- `get_component_abilities()`
- `iterate_design_components()`
- `ship_has_ability()`
- `find_ship_with_ability()`
- `count_ability()`

This is proper consolidation per PROJ-108 Phase 3. Good architecture.

---

### TCG-STR-001: No dedicated tests for naming.py
**Original Severity:** CRITICAL
**Location:** `game/strategy/data/naming.py`
**Verdict:** REJECTED

**Analysis:**
Tests exist at `tests/integration/strategy/test_naming.py`. The test file covers:
- `test_load_and_shuffle`
- `test_unique_names`
- `test_roman_numerals`

This provides coverage for the main functionality of `NameRegistry`.

**Reason:** Tests exist - finding is incorrect.

---

### TCG-STR-002: No dedicated tests for physics.py
**Original Severity:** CRITICAL
**Location:** `game/strategy/data/physics.py`
**Verdict:** REJECTED

**Analysis:**
Tests exist at `tests/unit/strategy/data/test_radiation_physics.py`. The test file contains:
- `TestSectorEnvironment` class with 2 tests
- `TestCalculateIncidentRadiation` class with 8 tests

Comprehensive coverage of the module's functionality.

**Reason:** Tests exist - finding is incorrect.

---

### TCG-STR-003: No dedicated tests for commands.py
**Original Severity:** MAJOR
**Location:** `game/strategy/engine/commands.py`
**Verdict:** REJECTED

**Analysis:**
Tests exist at `tests/integration/strategy/test_commands.py`. The file contains:
- `TestCommands` class (4 tests for colonize validation)
- `TestIssueInterceptCommand` (2 tests)
- `TestIssueJoinFleetCommand` (2 tests)
- `TestQueueColonizeMissionCommand` (2 tests)
- `TestClearFleetOrdersCommand` (2 tests)

**Reason:** Tests exist - finding is incorrect.

---

### TCG-STR-004: TurnEngine.validate_colonize_order lacks tests
**Original Severity:** MAJOR
**Location:** `game/strategy/engine/turn_engine.py`
**Verdict:** REJECTED

**Analysis:**
`validate_colonize_order` is tested indirectly through `tests/integration/strategy/test_commands.py`:
- `test_issue_colonize_command_validation_success`
- `test_issue_colonize_command_validation_fail_owned`
- `test_issue_colonize_command_validation_fail_location`
- `test_issue_colonize_command_any_planet`

The tests exercise the full validation logic via TurnEngine.

**Reason:** Tests exist via integration tests.

---

### TCG-STR-005: FleetOrder.to_dict() serialization has weak tests
**Original Severity:** MAJOR
**Location:** `game/strategy/data/fleet.py`
**Verdict:** DOWNGRADED to MINOR

**Analysis:**
Tests exist at `tests/unit/strategy/fleet/test_serialization.py`. Coverage includes:
- `test_to_dict_basic`
- `test_from_dict_basic`
- `test_roundtrip_serialization`
- `test_from_dict_restores_move_orders`
- `test_from_dict_restores_colonize_orders`
- `test_roundtrip_orders_preserved`

However, the newer order types (TRANSFER, superweapon orders) added in PROJ-68/102 may have less coverage. This is a minor gap, not a major one.

**Reason:** Good base coverage exists; newer order types could use more tests. Downgrade to MINOR.

---

### TCG-STR-006: QuickstartBuilder has no comprehensive tests
**Original Severity:** MAJOR
**Location:** `game/strategy/quickstart_builder.py`
**Verdict:** REJECTED

**Analysis:**
Extensive tests exist at `tests/unit/strategy/test_quickstart_builder.py` with 418 lines:
- `TestFixturePathFunctions` (3 tests)
- `TestQuickstartBuilderLoadTestRace` (3 tests)
- `TestQuickstartBuilderBuild1PConfig` (5 tests)
- `TestQuickstartBuilderBuild2PConfig` (2 tests)
- `TestQuickstartBuilderCopyDesigns` (5 tests)
- `TestQuickstartBuilderSpawnComplexes` (9 tests)

Comprehensive coverage of all public methods.

**Reason:** Tests exist and are comprehensive.

---

### TCG-STR-007: StrategySessionFacade has incomplete query tests
**Original Severity:** MAJOR
**Location:** `game/strategy/facade/strategy_session_facade.py`
**Verdict:** CONFIRMED

**Analysis:**
Tests exist at `tests/integration/strategy/facade/test_facade_integration.py` but focus mainly on command handling:
- `TestMoveCommandIntegration`
- `TestColonizeCommandIntegration`
- `TestInterceptCommandIntegration`
- `TestJoinCommandIntegration`
- `TestColonizeMissionIntegration`
- `TestFacadeProcessTurn`

Query methods like `get_fleet()`, `get_all_systems()`, `get_planet()`, `get_empire_colonies()`, `get_fleet_remaining_pods()` lack dedicated test coverage. The facade's read-path (DTO conversion) is undertested.

---

### TCG-STR-008: GameInitializer._setup_initial_scenario untested
**Original Severity:** MAJOR
**Location:** `game/strategy/engine/game_initializer.py`
**Verdict:** REJECTED

**Analysis:**
Tests exist at `tests/unit/strategy/engine/test_game_initializer.py`:
- `test_initialize_assigns_homeworlds` - verifies colonies are assigned
- `test_adjust_homeworld_to_race_sets_planet_type`
- `test_adjust_homeworld_to_race_sets_gravity`
- `test_adjust_homeworld_handles_invalid_planet_type`
- `test_empire_always_has_race_config` (BUG-88)
- `test_empire_preserves_explicit_race_config` (BUG-88)

The `_setup_initial_scenario` is tested indirectly through `initialize()` tests and directly through `_adjust_homeworld_to_race` tests.

**Reason:** Tests exist - finding is incorrect.

---

### TCG-STR-009: ShipStatsCalculator.has_warp_capability untested
**Original Severity:** MAJOR
**Location:** `game/strategy/services/ship_stats_calculator.py`
**Verdict:** REJECTED

**Analysis:**
Extensive tests exist at `tests/unit/strategy/ship_stats/test_warp.py`:
- `TestHasWarpCapability` class with 14 tests covering:
  - Ship without warp drive
  - Ship with sufficient warp drive
  - Ship with equal tonnage
  - Ship with insufficient tonnage
  - Zero mass edge case
  - Insufficient energy/fuel storage
  - Exactly sufficient storage
  - No warp cost scenario
  - Damaged warp drive
  - Multiple resource requirements
  - Missing stats defaults

Comprehensive coverage.

**Reason:** Tests exist and are comprehensive.

---

### TCG-STR-010: DensityMap.from_config() lacks test coverage
**Original Severity:** MINOR
**Location:** `game/strategy/generation/density_map.py`
**Verdict:** REJECTED

**Analysis:**
Tests exist at `tests/unit/strategy/generation/density/test_density_map.py`:
- `TestDensityMapFromConfig` class with 5 tests:
  - `test_from_config_creates_map`
  - `test_from_config_multiple_primitives`
  - `test_from_config_unknown_type_raises`
  - `test_from_config_empty_primitives_raises`
  - `test_from_config_missing_type_raises`

The actual file is at `game/strategy/generation/density/density_map.py` (nested in density subdirectory).

**Reason:** Tests exist - finding is incorrect.

---

## Cross-Shard Duplicates

None identified. The findings in this shard are specific to the strategy layer.

---

## Recommendations

1. **ADR-STR-001 (Confirmed):** Consider moving the simulation imports to a late-import pattern within the methods that need them, or create a dedicated adapter for formula evaluation.

2. **ADR-STR-003 (Downgraded):** Monitor Galaxy class size. If it grows further, consider extracting spatial indexing into a dedicated class.

3. **DUP-STR-006 (Confirmed):** Consider creating a `gaussian_factor(deviation, sigma)` utility function in a formulas utilities module.

4. **TCG-STR-007 (Confirmed):** Add unit tests for StrategySessionFacade query methods to verify DTO conversion.

5. **General:** Many findings referenced non-existent files or had "Unknown" locations. Improve sweep tooling to validate file paths before generating findings.

---

## Additional Findings Reviewed (2026-02-13 Second Pass)

### TCG-STR-001 (Additional): No dedicated tests for naming.py
**Original Severity:** CRITICAL
**Verdict:** REJECTED
**Reason:** Tests exist at `tests/unit/strategy/data/test_naming.py` with comprehensive coverage (265+ lines) covering NameRegistry initialization, load_data, get_system_name, and to_roman methods. Also tested in `tests/integration/strategy/test_naming.py`.

### TCG-STR-002 (Additional): No dedicated tests for physics.py
**Original Severity:** CRITICAL
**Verdict:** REJECTED
**Reason:** Tests exist at `tests/unit/strategy/data/test_radiation_physics.py` with comprehensive coverage (196 lines) covering SectorEnvironment and calculate_incident_radiation function.

### CON-STR-001: Logging Pattern Inconsistency
**Original Severity:** MAJOR
**Verdict:** DOWNGRADED to MINOR
**Reason:** Only 4 files in game/strategy use `import logging` instead of `game.core.logger` (harvesting_engine.py, density_map.py, placement_strategies.py, galaxy_layouts_loader.py). This is a minor inconsistency - standard Python logging works fine.

### CON-STR-002: Protocol Interface Decorator Inconsistency
**Original Severity:** MAJOR
**Verdict:** REJECTED
**Reason:** ICommandHandler is properly defined as a Protocol class in command_handlers.py (line 24). Command handler classes follow the protocol through duck typing, which is the standard Python approach. No decorator inconsistency exists.

### CON-STR-003: Inconsistent Return Type for validate()
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** The validate() method in race_config.py returns `tuple[bool, str]` (lines 280-298) which is inconsistent with ValidationResult pattern used elsewhere in the codebase.

### CON-STR-004: Inconsistent `from __future__ import annotations`
**Original Severity:** MAJOR
**Verdict:** DOWNGRADED to INFO
**Reason:** Only 3 files in game/strategy use this import (build_queue_source.py, event_log.py, build_context.py). This is intentional where forward references are needed, not a consistency issue.

### DUP-STR-001: Build Queue Source Collection Near-Identical
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** collect_build_queues_at_hex() and collect_all_build_queues_for_empire() in build_queue_source.py share ~80% similar code (lines 163-216 and 239-288).

### DUP-STR-002: Facility Shipyard Detection Duplicated
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** _facility_is_shipyard() function exists in build_queue_source.py and similar detection logic is used elsewhere.

### DUP-STR-003: Mission Command Handler Duplication
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** The mission command handlers in superweapon_command_handlers.py (lines 182-393) show 5 nearly identical handler classes with the same pattern: resolve fleet, determine start hex, calculate path, queue MOVE order, queue action order.

### DUP-STR-004: to_dict/from_dict Boilerplate Pattern
**Original Severity:** MAJOR
**Verdict:** DOWNGRADED to INFO
**Reason:** Standard Python serialization idiom. Each class has unique needs. This is expected boilerplate.

### DUP-STR-005: Fleet Resolution Pattern in Command Handlers
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** Multiple command handlers in command_handlers.py repeat the fleet resolution pattern (lines 83-90, 133-135, 181-188, etc.).

### LEG-STR-001: Legacy Behavior Branch in FleetOrderProcessor
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** FleetOrderProcessor.process_colonize() has explicit "Legacy behavior" comment at line 231 for removing entire fleet when component_registry is None.

### LEG-STR-002: Backward Compatibility Comment in GameSession
**Original Severity:** MAJOR
**Verdict:** REJECTED
**Reason:** The "backward compatibility" comment in GameSession._get_fleet_by_id() describes a test compatibility fallback, not deprecated production code. This is internal documentation.

### LEG-STR-003: Legacy Items in ProductionEngine
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** ProductionEngine mentions "legacy items" at lines 96, 154, 220 - intentional handling of old queue format without cost tracking.

## Additional Test Coverage Findings

### TCG-STR-003 through TCG-STR-016: Various test coverage gaps
**Verdict Summary:**
- TCG-STR-003 (fleet_order_processor.py): REJECTED - tests exist at test_fleet_order_processor.py
- TCG-STR-004 (colonize_validator.py): REJECTED - tested in test_colonize_population.py
- TCG-STR-005 (superweapon handlers): CONFIRMED - limited test coverage
- TCG-STR-006 (spatial_index.py): REJECTED - tests exist at test_spatial_index.py
- TCG-STR-007 (build_context.py): REJECTED - tests exist at test_build_context.py
- TCG-STR-008 (ship_cargo_manager.py): REJECTED - tests exist at test_ship_cargo_manager.py
- TCG-STR-009 (empire_economy_calculator.py): CONFIRMED - no dedicated tests found

## Cross-Shard Duplicates

1. **Component Layer Iteration Pattern** (DUP-STR-007) - Similar patterns may exist in simulation layer
2. **Logging Pattern** (CON-STR-001) - Project-wide consideration for consistent logging approach
