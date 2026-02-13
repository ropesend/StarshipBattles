# Validation Report: Simulation

## Summary
- **Shard:** Simulation (SIM)
- **Findings Reviewed:** 33
- **Confirmed:** 21
- **Downgraded:** 6
- **Rejected:** 6
- **Rejection Rate:** 18%

## Verdicts

### Architecture Findings

#### Finding: ADR-SIM-001
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** Verified - `game/simulation/battle_controller.py:718` contains late import `from game.ai.ai_factory import AIControllerFactory` which violates simulation->core-only rule. PROJ-126 acknowledged but left late import as convenience.

---

#### Finding: ADR-SIM-002
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** Verified - TYPE_CHECKING import at line 72-74 includes `from game.ai.controller import AIController`. However, TYPE_CHECKING imports create no runtime dependency; downgrade to Minor per validation guidelines.

---

#### Finding: ADR-SIM-003
**Original Severity:** Major
**Verdict:** REJECTED
**Reason:** Already addressed by PROJ-126. Per phase_2_checklist.md Task 2.3: "FALSE POSITIVE - 873 lines with proper Strategy pattern (BattleModeHandler), delegation to RetreatManager, BattleStateManager. Well-architected, not a god class."

---

#### Finding: ADR-SIM-004
**Original Severity:** Major
**Verdict:** REJECTED
**Reason:** Already addressed by PROJ-126. Per phase_2_checklist.md Task 2.4: "FALSE POSITIVE - 810 lines with proper composition (ShipFormation, ShipStatsCalculator, ShipCombatEngine), mixins and delegation. Well-architected, not a god class."

---

#### Finding: ADR-SIM-005
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - Late import at ship.py:492 and 537 for ModifierService is documented but does exist. Comment notes "LATE IMPORT: services/__init__.py imports VehicleDesignService which imports Ship". Documented intentional pattern.

---

#### Finding: ADR-SIM-006
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified - game/engine layer is used by simulation (SpatialGrid, CollisionSystem, PhysicsBody). This is an architectural observation, not a violation. The game/engine layer role is unclear in documentation.

---

#### Finding: ADR-SIM-007
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified - component.py is 723 lines with ComponentCacheManager singleton and factory functions at module level. Approaching threshold but not exceeding it. Valid observation.

---

### Consistency Findings

#### Finding: CON-SIM-001
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified - `ResourceRegistry.get_resource()` returns Optional[ResourceState] at line 120-121, while `get_value()` returns 0.0 for missing resources at line 123-126. Inconsistent "not found" convention confirmed.

---

#### Finding: CON-SIM-002
**Original Severity:** Major
**Verdict:** REJECTED
**Reason:** Location is "Unknown" - unverifiable claims cannot be acted on. Finding refers to multiple files but provides no specific locations to validate.

---

#### Finding: CON-SIM-003
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** Verified - Boolean prefixes (is_, has_, can_) are used consistently by semantic meaning: `is_alive` (state), `has_ability()` (presence), `can_fire()` (capability). This is actually good practice, not a real inconsistency. Downgrade.

---

#### Finding: CON-SIM-004
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** Verified - Parameter ordering is mostly consistent (ship first, then component). The finding itself notes "pattern is mostly consistent". Minor style concern at most.

---

#### Finding: CON-SIM-005
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified - Ship and Component expose both facade methods (take_damage()) and direct sub-manager access (health_manager property). Two access patterns exist, creating API inconsistency.

---

#### Finding: CON-SIM-006
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - Mixed underscore prefixes: `_registries`, `_cached_hp_ratio` (underscore) vs `stats`, `modifiers`, `ability_instances` (no underscore). Genuine naming inconsistency.

---

#### Finding: CON-SIM-007
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - `modifiers.py:10-12` uses `import logging; logger = logging.getLogger(__name__)` while other files use `from game.core.logger import log_warning`. Genuine inconsistency.

---

#### Finding: CON-SIM-008
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - design_loader.py:70-82 catches specific exceptions and returns None, while other code may re-raise. Exception handling patterns vary across the module.

---

#### Finding: CON-SIM-009
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - `WeaponAbility`, `ProjectileWeaponAbility` have Ability suffix while `ResourceConsumption`, `CombatPropulsion` do not. Genuine naming inconsistency confirmed in propulsion.py.

---

#### Finding: CON-SIM-010
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** File `game/simulation/projectile.py` does not exist. Constants are defined in `game/simulation/entities/projectile.py`. The location is incorrect.

---

#### Finding: CON-SIM-011
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**Reason:** Verified but finding itself acknowledges "pattern is mostly sensible (get=lookup, find=search, calculate=compute, load=I/O)". This is observation not issue.

---

#### Finding: CON-SIM-012
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - retreat_manager.py:132-134 has callable parameters with inconsistent type hints. Some methods lack type hints for callbacks entirely.

---

#### Finding: CON-SIM-013
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**Reason:** Verified - Mixed use of dataclasses vs regular classes. Finding itself notes "Current usage is reasonable, just document the guideline." Not actionable.

---

#### Finding: CON-SIM-014
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified - Import organization varies, TYPE_CHECKING blocks placed inconsistently. Valid observation.

---

#### Finding: CON-SIM-015
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified - `__init__.py` files vary in export patterns. Main exports curated API, subpackages vary. Valid observation.

---

#### Finding: CON-SIM-016
**Original Severity:** Info
**Verdict:** REJECTED
**Reason:** Not an issue - this is a positive observation ("Two-stage aggregation pattern well-documented"). Info-level observations that are not issues should be rejected.

---

#### Finding: CON-SIM-017
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - propulsion.py shows duplicate recalculate() patterns across CombatPropulsion, ManeuveringThruster, StrategicMovement. STAT_BINDINGS system could auto-generate these.

---

### Legacy Findings

#### Finding: LEG-SIM-001
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified - `game/simulation/factories/__init__.py` is empty with docstring "This package is now empty but kept for potential future". PROJ-126 moved factory to AI layer but left empty package.

---

#### Finding: LEG-SIM-002
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified - `battle_mode_handler.py:225-240` apply_results() builds mappings but comment at line 235 states "implementation blocked by PROJ-41". Incomplete stub confirmed.

---

#### Finding: LEG-SIM-003
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** Verified - getattr with defaults used in battle_state.py:212-225 for ai_strategy, angle, shields. However, these are likely for serialization compatibility, not legacy code. Downgrade from Major to Minor.

---

#### Finding: LEG-SIM-004
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified - hasattr checks at ability_aggregator.py:101, ship_stats.py:281, combat_endurance.py:42 for `ability_instances` which is always initialized in Component.__init__. Unnecessary defensive code.

---

#### Finding: LEG-SIM-005
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - modifier_schema.py:36-52 has V1 format check that raises ValueError. If all V1 modifiers migrated, this is dead validation code.

---

#### Finding: LEG-SIM-006
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - projectile.py:47-53 checks `isinstance(proj_type, str)` and converts to AttackType enum with fallback warning. Legacy string handling pattern.

---

#### Finding: LEG-SIM-007
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - battle_engine.py:270,322 contain comments "PROJ-106: Legacy path removed" with ValueError raises. Comments reference legacy behavior that no longer exists.

---

#### Finding: LEG-SIM-008
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - battle_engine.py:178 docstring says "If None, imports from game.ai directly (legacy behavior)" but PROJ-106 removed this behavior. Stale documentation.

---

#### Finding: LEG-SIM-009
**Original Severity:** Info
**Verdict:** REJECTED
**Reason:** reset_component_caches() is used in tests (found in conftest.py, test_component_cache.py, test_seeker_multi_ability.py). Not dead code - used for test isolation.

---

### Test Coverage Findings

Note: The test coverage simulation findings in the report do not use SIM IDs. The simulation test coverage findings appear to be from a separate agent without SIM prefixed IDs.

From examination of the simulation test coverage report findings:

#### Finding: [CRITICAL] combat_endurance.py - No Direct Unit Tests
**Original Severity:** Critical
**Verdict:** REJECTED
**Reason:** Tests exist at `tests/unit/simulation/entities/test_combat_endurance.py` and `tests/unit/combat/test_combat_endurance.py`. Finding is factually incorrect.

---

#### Finding: [CRITICAL] ship_stats.py - ShipStatsCalculator Phase Methods Not Directly Tested
**Original Severity:** Critical
**Verdict:** DOWNGRADED(Minor)
**Reason:** Finding acknowledges "test_ship_stats_calculator_phases.py exists" but wants more granular tests. This is enhancement suggestion, not critical gap.

---

#### Finding: [MAJOR] WarpJump Ability - Incomplete Test Coverage
**Original Severity:** Major
**Verdict:** REJECTED
**Reason:** Tests exist at `tests/unit/abilities/test_warp_jump.py` with TestWarpJumpAbility class covering layer, scopes, max_tonnage. Finding claims "No tests found" but tests exist.

---

#### Finding: [MAJOR] StrategicMovement Ability - No Scope Testing
**Original Severity:** Major
**Verdict:** REJECTED
**Reason:** Tests exist at `tests/unit/abilities/test_strategic_movement.py` with scope tests at lines 28-43 (test_strategic_movement_allowed_scopes, test_strategic_movement_default_scope_is_self). Finding is factually incorrect.

---

#### Finding: [MAJOR] SimulationDesignLoader - Error Path Testing
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** Tests exist at `tests/unit/simulation/services/test_simulation_design_loader.py`. Finding wants more error path tests - this is enhancement, not missing coverage.

---

## Statistics Summary

| Category | Confirmed | Downgraded | Rejected |
|----------|-----------|------------|----------|
| Architecture (ADR-SIM-*) | 4 | 1 | 2 |
| Consistency (CON-SIM-*) | 10 | 4 | 3 |
| Legacy (LEG-SIM-*) | 7 | 1 | 1 |
| **SIM-Prefixed Total** | **21** | **6** | **6** |

**Note on Test Coverage:** The test coverage simulation findings in the sweep report do not use SIM-prefixed IDs. They appear unnumbered in the detailed report. For completeness, 5 test coverage findings were also validated (0 CONFIRMED, 2 DOWNGRADED, 3 REJECTED) as shown above, but these are supplementary to the primary SIM-prefixed findings.

**Note on Duplication:** The duplication report for simulation contains no SIM-prefixed IDs - all duplication findings are ID'd as UNK-* or Major/Minor headings without standard IDs. These were not included in this validation scope per the instructions to extract IDs containing "-SIM-".
