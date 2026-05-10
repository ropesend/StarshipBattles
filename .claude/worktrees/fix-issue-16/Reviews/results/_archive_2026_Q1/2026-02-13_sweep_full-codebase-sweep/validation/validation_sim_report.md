# Validation Report: Simulation

## Summary
- **Shard:** Simulation (SIM)
- **Findings Reviewed:** 42
- **Confirmed:** 29
- **Downgraded:** 6
- **Rejected:** 7
- **Rejection Rate:** 16.7%

## Verdicts

#### Finding: ADR-SIM-001
**Original Severity:** CRITICAL
**Verdict:** CONFIRMED
**Reason:** Verified at `game/simulation/factories/ai_factory.py:56-58`. The factory imports `from game.ai.controller import AIController` and `from game.ai.interfaces import ShipControllableAdapter` directly. While this is isolated in a factory as intentional design, it still creates a layer violation where simulation imports from ai layer. The factory pattern mitigates but doesn't eliminate the architectural coupling.

#### Finding: CON-SIM-001
**Original Severity:** CRITICAL
**Verdict:** CONFIRMED
**Reason:** Verified at `game/simulation/systems/resource_manager.py:120-131`. `get_resource()` returns `Optional[ResourceState]` (None if not found), while `get_value()` returns 0.0 if not found. This inconsistency can mask bugs where code assumes a resource exists based on zero return value.

#### Finding: TCG-SIM-001
**Original Severity:** CRITICAL
**Verdict:** REJECTED
**Reason:** Tests exist. Found `tests/unit/entities/test_ship_stats.py` (6+ tests), `tests/unit/simulation/systems/test_ship_stats_phase_ordering.py`, and `tests/unit/simulation/systems/test_ship_stats_calculator_phases.py`. The finding claims "No corresponding unit test file exists" which is FALSE.

#### Finding: TCG-SIM-002
**Original Severity:** CRITICAL
**Verdict:** REJECTED
**Reason:** Tests exist. Found `tests/unit/entities/test_ship_stat_querier.py` with comprehensive tests (843 lines, 100+ test methods). The finding claims "No corresponding test file exists" which is FALSE.

#### Finding: TCG-SIM-003
**Original Severity:** CRITICAL
**Verdict:** REJECTED
**Reason:** Tests exist. Found `tests/unit/entities/test_ship_validator_helper.py` with tests for check_validity, get_validation_warnings, and get_missing_requirements. The finding claims "No unit tests exist" which is FALSE.

#### Finding: ADR-SIM-002
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** Verified at `game/simulation/systems/battle_engine.py:72-75`. TYPE_CHECKING block imports `from game.ai.controller import AIController`. While TYPE_CHECKING avoids runtime import, it represents architectural awareness of the ai layer.

#### Finding: ADR-SIM-003
**Original Severity:** MAJOR
**Verdict:** DOWNGRADED(MINOR)
**Reason:** BattleController is 848 lines exceeding 500-line threshold, but uses proper decomposition via BattleService, RetreatManager, BattleStateManager delegation. Complexity is inherent to orchestration.

#### Finding: ADR-SIM-004
**Original Severity:** MAJOR
**Verdict:** DOWNGRADED(INFO)
**Reason:** Ship is 810 lines but uses extensive composition (ShipStatsCalculator, ShipStatQuerier, ShipValidatorHelper, ShipCombatEngine, ShipSerializer). This is a core domain entity with inherent complexity.

#### Finding: ADR-SIM-005
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** Verified at `game/simulation/entities/ship.py:491-492` and `536-537`. Comments document "LATE IMPORT: services/__init__.py imports VehicleDesignService which imports Ship" with circular dependency workaround.

#### Finding: CON-SIM-002
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** Verified at `game/simulation/services/design_loader.py:118-133`. Lines 118-129 catch `json.JSONDecodeError`, `(KeyError, TypeError, ValueError)`, and `OSError`. Line 130 catches `(KeyError, TypeError, ValueError, json.JSONDecodeError)` which is UNREACHABLE dead code.

#### Finding: CON-SIM-003
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** Verified at `game/simulation/entities/projectile.py:161,167,179`. Found magic numbers: `* 100` at line 161, `* 0.01` at line 167, and `45` degrees at line 179 for missile guidance without named constants.

#### Finding: CON-SIM-004
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** Ship.add_component() calls `get_or_create_validator()` which uses singleton pattern, bypassing DI for the validator.

#### Finding: CON-SIM-005
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** Verified at `game/simulation/components/abilities/resources.py`. ResourceConsumption uses `resource_name` (line 26), while ResourceStorage and ResourceGeneration use `resource_type` for the same concept.

#### Finding: CON-SIM-006
**Original Severity:** MAJOR
**Verdict:** DOWNGRADED(MINOR)
**Reason:** Type hint gaps exist but are less critical for mixin methods. This is a code quality improvement, not a major issue.

#### Finding: CON-SIM-007
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** Verified at `game/simulation/factories/ai_factory.py:35`. `__init__(self, grid: 'SpatialGrid')` uses positional parameter, inconsistent with keyword-only pattern used by other DI classes.

#### Finding: CON-SIM-008
**Original Severity:** MAJOR
**Verdict:** DOWNGRADED(MINOR)
**Reason:** Magic numbers in targeting/combat systems exist but impact is limited. Downgrade to MINOR.

#### Finding: DUP-SIM-001
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** Verified at `game/simulation/battle_state.py`. ComponentState, ShipState, ProjectileState, BattleState, and BattleResults all have manual to_dict/from_dict methods with significant boilerplate.

#### Finding: DUP-SIM-002
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** Verified at `game/simulation/components/abilities/resources.py`. ResourceConsumption, ResourceStorage, and ResourceGeneration share identical structure patterns.

#### Finding: DUP-SIM-003
**Original Severity:** MAJOR
**Verdict:** DOWNGRADED(MINOR)
**Reason:** Team iteration patterns are natural domain logic repetition. The pattern is simple and readable.

#### Finding: TCG-SIM-004
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** `game/simulation/designs.py` (69 lines) contains factory functions create_brick() and create_interceptor() without dedicated test file for these functions.

#### Finding: TCG-SIM-005
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** ResourceRegistry edge cases need better coverage (register_storage multiple times, negative rates, reset_stats behavior, etc.)

#### Finding: TCG-SIM-006
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** BattleController state transition tests are incomplete (pause/resume, time dilation, edge case end conditions).

#### Finding: TCG-SIM-007
**Original Severity:** MAJOR
**Verdict:** DOWNGRADED(MINOR)
**Reason:** Formula system has 16+ tests. Core functionality is covered; edge cases are enhancement rather than critical gap.

#### Finding: TCG-SIM-008
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** ProjectileManager has tests for basic operations but guidance system integration tests are limited.

#### Finding: TCG-SIM-009
**Original Severity:** MAJOR
**Verdict:** DOWNGRADED(MINOR)
**Reason:** 55 tests for battle state serialization is reasonable coverage. Edge cases are nice-to-have.

#### Finding: TCG-SIM-010
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** DamageCalculator tests (47) lack comprehensive armor type interaction tests for emissive, crystalline armor and layer penetration.

#### Finding: CON-SIM-009
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** Abbreviated parameter names like `p_speed`, `t_pos`, `t_vel` exist in targeting system. More descriptive names would improve readability.

#### Finding: CON-SIM-010
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** Mixed logging initialization patterns exist. Some modules use `logging.getLogger()` while others use `game.core.logger` wrappers.

#### Finding: CON-SIM-011
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** STAT_BINDINGS type hint inconsistency exists between marker abilities (with type hint) and superweapons (without).

#### Finding: CON-SIM-012
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** sync_data() implementation is inconsistent across abilities. Some implement it, others rely on base class no-op.

#### Finding: CON-SIM-013
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** Method verb conventions are inconsistent (get_ vs calculate_ for similar operations).

#### Finding: CON-SIM-014
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** Missing exports in services/__init__.py for SimulationDesignLoader and reload_registries_from_directory.

#### Finding: CON-SIM-015
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** File naming convention inconsistency - ability_aggregator.py doesn't use ship_ prefix like other ship-related extractions.

#### Finding: CON-SIM-016
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** PROJ comment format varies across files.

#### Finding: DUP-SIM-004
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** Vector2 conversion pattern duplicated in projectile_manager.py.

#### Finding: DUP-SIM-005
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** Resource color mapping duplicated across resource abilities' get_ui_rows methods.

#### Finding: DUP-SIM-006
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** ship_id_map lookup pattern repeated 4 times in RetreatManager.

#### Finding: DUP-SIM-007
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** Validation pattern similar structure in modifier_schema.py validation functions.

#### Finding: LEG-SIM-006
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** Verified at `game/simulation/components/ability_manager.py:57-65`. The fallback for "Module Identity Drift in tests" using `cls.__name__` check is documented as intentional tech debt.

#### Finding: LEG-SIM-007
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** Verified at `game/simulation/components/component.py:199-223`. hasattr pattern with fallback for _ability_index exists for edge cases.

#### Finding: LEG-SIM-NEW-001
**Original Severity:** MINOR
**Verdict:** REJECTED
**Reason:** Duplicate of CON-SIM-002 (same dead code exception handling was already reported).

#### Finding: TCG-SIM-011
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** Weapon ability tests are split across files, which may lead to coverage gaps.

#### Finding: TCG-SIM-012
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** Defense ability tests lack explicit stacking rule tests.

#### Finding: TCG-SIM-013
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** Propulsion abilities missing turn rate limit and boundary tests.

#### Finding: TCG-SIM-014
**Original Severity:** MINOR
**Verdict:** REJECTED
**Reason:** Finding claims DesignLoader has no tests but `tests/unit/simulation/services/test_simulation_design_loader.py` exists with 8 tests.

#### Finding: TCG-SIM-015
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** AIController interface tests are shallow (8 tests). Could be more robust.

#### Finding: TCG-SIM-016
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** ShipValidator tests (50) lack multi-rule failure scenarios and validation order independence tests.

#### Finding: ADR-SIM-007
**Original Severity:** INFO
**Verdict:** CONFIRMED
**Reason:** Extensive TYPE_CHECKING usage (30+ files) is noted. This is valid Python practice but the volume indicates tight coupling.

#### Finding: CON-SIM-017
**Original Severity:** INFO
**Verdict:** CONFIRMED
**Reason:** ResourceRegistry naming deviation from Manager pattern is noted but semantically correct.

#### Finding: CON-SIM-018
**Original Severity:** INFO
**Verdict:** CONFIRMED
**Reason:** Positive finding - good facade/delegate pattern usage in ShipCombatEngine and BattleController.

#### Finding: DUP-SIM-008
**Original Severity:** INFO
**Verdict:** CONFIRMED
**Reason:** Natural similarity in state dataclasses is expected and acceptable domain modeling.

#### Finding: LEG-SIM-009
**Original Severity:** INFO
**Verdict:** CONFIRMED
**Reason:** TechPresetLoader usage noted - primarily for tests/standalone mode.

#### Finding: TCG-SIM-017
**Original Severity:** INFO
**Verdict:** CONFIRMED
**Reason:** Test organization feedback noted - simulation tests spread across multiple directories.

#### Finding: TCG-SIM-018
**Original Severity:** INFO
**Verdict:** CONFIRMED
**Reason:** No performance tests for large battles noted - valid observational finding.

## Cross-Shard Duplicates

- **LEG-SIM-NEW-001** is a duplicate of **CON-SIM-002** (both report the same dead code exception handling in design_loader.py)

No other cross-shard duplicates detected within the SIM shard.
