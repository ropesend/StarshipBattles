# Legacy System Holdovers Sweep: Simulation

## Summary
- **Shard:** Simulation
- **Files Scanned:** 69
- **Total Issues Found:** 12
- **Critical:** 0 | **Major:** 3 | **Minor:** 7 | **Info:** 2

## Findings

#### MAJOR: Dead Code - `_apply_results_to_fleet` Method is Unreachable
**ID:** LEG-SIM-001
**Location:** `game/simulation/battle_controller.py:656-672`
**Issue:** The `_apply_results_to_fleet` method has a `pass` body and is only called from `apply_results_to_fleets` after the mode handler path succeeds (line 626 returns). The comment explicitly states "exists as a fallback path but is not used in production." This is dead code that should be removed per project policy.
**Impact:** Maintenance burden, confusion about strategy layer responsibilities, untested code path.
**Recommendation:** Delete the `_apply_results_to_fleet` method entirely. The strategy layer (ConflictResolutionEngine) owns fleet update responsibility.
**Effort:** Simple

#### MAJOR: Unused Import - `copy` Module in battle_controller.py
**ID:** LEG-SIM-002
**Location:** `game/simulation/battle_controller.py:18`
**Issue:** The `copy` module is imported but never used anywhere in the file. No `copy.copy()` or `copy.deepcopy()` calls exist.
**Impact:** Minor code bloat, potential confusion about intended usage.
**Recommendation:** Remove the unused `import copy` statement.
**Effort:** Simple

#### MAJOR: Unused Import - `time` Module in battle_engine.py
**ID:** LEG-SIM-003
**Location:** `game/simulation/systems/battle_engine.py:56`
**Issue:** The `time` module is imported but never used anywhere in BattleEngine. No `time.time()`, `time.sleep()`, or other time calls exist.
**Impact:** Minor code bloat, vestigial import from previous timing code.
**Recommendation:** Remove the unused `import time` statement.
**Effort:** Simple

#### MINOR: Unused Import - `BattleEndCondition` in battle_controller.py
**ID:** LEG-SIM-004
**Location:** `game/simulation/battle_controller.py:24`
**Issue:** `BattleEndCondition` is imported alongside `BattleEndMode` but is never used directly in the file. Only `BattleEndMode` is used.
**Impact:** Minor code bloat.
**Recommendation:** Change import to `from game.simulation.systems.battle_end_conditions import BattleEndMode`.
**Effort:** Simple

#### MINOR: Unused Import - `log_debug` in battle_controller.py
**ID:** LEG-SIM-005
**Location:** `game/simulation/battle_controller.py:35`
**Issue:** `log_debug` is imported alongside `log_info` and `log_warning` but is never used in the file. Only `log_info` and `log_warning` are called.
**Impact:** Minor code bloat.
**Recommendation:** Remove `log_debug` from the import statement.
**Effort:** Simple

#### MINOR: Unused Import - `log_debug` in battle_state.py
**ID:** LEG-SIM-006
**Location:** `game/simulation/battle_state.py:19`
**Issue:** `log_debug` is imported alongside `log_warning` but is never used in the file. Only `log_warning` is called.
**Impact:** Minor code bloat.
**Recommendation:** Remove `log_debug` from the import statement.
**Effort:** Simple

#### MINOR: hasattr Checks on Known Dataclass Fields
**ID:** LEG-SIM-007
**Location:** `game/simulation/managers/battle_state_manager.py:127-129`
**Issue:** `validate_state()` uses `hasattr(state, 'mode')` and `hasattr(state, 'ships')` to check fields that are defined in the `BattleState` dataclass. These fields always exist on a properly constructed `BattleState` instance. This pattern suggests the code was written for backward compatibility with older state formats.
**Impact:** Confusion about whether these fields might be missing. The pattern implies state migration concerns that shouldn't exist per project policy.
**Recommendation:** Remove hasattr checks since BattleState is a dataclass with required fields. If validation is needed, check field values instead of existence.
**Effort:** Simple

#### MINOR: Defensive Fallback Comment Indicates Incomplete Migration
**ID:** LEG-SIM-008
**Location:** `game/simulation/battle_controller.py:628-635`
**Issue:** The comment "Defensive fallback for unexpected mode handler state" and the code that follows suggest a fallback path that should never execute if the system is properly configured. The comment indicates this was left "just in case" - contrary to project migration policy.
**Impact:** Untested code path, potential confusion.
**Recommendation:** If mode handler is always set when reaching `apply_results_to_fleets`, convert the fallback to an assertion or remove it entirely. The strategy layer should own this responsibility completely.
**Effort:** Simple

#### MINOR: Excessive hasattr Checks in Serialization Code
**ID:** LEG-SIM-009
**Location:** `game/simulation/battle_state.py:201-203, 401-407, 598-603`
**Issue:** Multiple `hasattr` checks exist for accessing attributes on Ship, Projectile, and BattleEngine objects. While some are legitimate (checking for optional attributes), others like `hasattr(engine, 'end_condition')` check for attributes that should always exist on a BattleEngine instance.
**Impact:** Suggests old/new system compatibility concerns that shouldn't exist.
**Recommendation:** Audit each hasattr usage. For attributes that always exist on properly constructed objects, remove the hasattr check and access directly.
**Effort:** Medium

#### MINOR: Vestigial Format Version Comment
**ID:** LEG-SIM-010
**Location:** `game/simulation/entities/ship_serialization.py:38`
**Issue:** The format version is set to "2.0" with a comment "PROJ-42 Phase 4: Explicit format version". This implies version 1.0 existed, but per project policy, old save formats are not migrated - they are discarded. The version field adds no value if there's no migration code.
**Impact:** Minor confusion about whether format versions matter.
**Recommendation:** Either remove the version field entirely (saves are disposable) or add a comment clarifying its purpose (e.g., debugging only).
**Effort:** Simple

#### INFO: Module Identity Drift Known Issue
**ID:** LEG-SIM-011
**Location:** `game/simulation/components/ability_manager.py:57`
**Issue:** Comment states "[KNOWN_ISSUE] Fallback for Module Identity Drift in tests." This is a documented workaround for a test environment issue, not production code.
**Impact:** None in production, but indicates a test infrastructure issue that could be addressed.
**Recommendation:** Track this as a test infrastructure improvement task, not a legacy code issue.
**Effort:** N/A

#### INFO: PROJ Reference Comments Throughout
**ID:** LEG-SIM-012
**Location:** Multiple files
**Issue:** Numerous comments reference PROJ-XX tickets explaining why code was changed. These are historical context, not legacy holdovers. Examples: PROJ-42, PROJ-43, PROJ-49, PROJ-50, PROJ-113, PROJ-126, PROJ-132.
**Impact:** None - helpful documentation of refactoring history.
**Recommendation:** Keep these comments. They provide valuable context for understanding the codebase evolution.
**Effort:** N/A

## Top 5 Priority Issues

1. **LEG-SIM-001 (MAJOR):** Dead `_apply_results_to_fleet` method with empty body. Should be deleted per project policy against fallback paths.

2. **LEG-SIM-002 (MAJOR):** Unused `copy` import in battle_controller.py. Trivial fix but indicates vestigial code.

3. **LEG-SIM-003 (MAJOR):** Unused `time` import in battle_engine.py. Trivial fix but indicates vestigial code from timing code that was removed.

4. **LEG-SIM-008 (MINOR):** Defensive fallback code in `apply_results_to_fleets` that contradicts project migration policy. Should be converted to assertion or removed.

5. **LEG-SIM-009 (MINOR):** Excessive hasattr checks in serialization code. Some are legitimate but others check for always-present attributes, suggesting old compatibility concerns.

## Overall Assessment

The simulation layer is in good shape. No critical issues were found. The codebase shows evidence of thorough refactoring (PROJ-42, PROJ-43, PROJ-50, etc.) with proper dependency injection patterns and layer separation.

The main findings are:
1. A few unused imports (trivial cleanup)
2. One dead method (`_apply_results_to_fleet`) that should be removed
3. Some hasattr checks that are overly defensive

The extensive PROJ-XX comments indicate a well-documented refactoring history. The simulation layer properly uses:
- Registry pattern for component/modifier lookup
- Dependency injection via `registries` parameter
- Protocols (IAIController, IAIControllerFactory) for layer decoupling
- Template method pattern for validation rules
- Strategy pattern for battle mode handling

No backward compatibility layers or deprecated systems were found. The "fallback" code paths that exist are documented as defensive (not active compatibility shims).
