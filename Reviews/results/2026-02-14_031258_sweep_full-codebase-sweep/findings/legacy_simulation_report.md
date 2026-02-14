# Legacy System Holdovers Sweep: Simulation

## Summary
- **Shard:** Simulation
- **Files Scanned:** 69
- **Total Issues Found:** 10
- **Critical:** 0 | **Major:** 3 | **Minor:** 5 | **Info:** 2

## Findings

#### MAJOR: Unused designs.py Factory Functions
**ID:** LEG-SIM-001
**Location:** `game/simulation/designs.py:11-69`
**Issue:** Two factory functions `create_brick()` and `create_interceptor()` are defined but never called anywhere in the codebase. These appear to be legacy test helpers that were superseded by the JSON-based design system and DesignLibrary.
**Impact:** Dead code adds maintenance burden and creates confusion about which ship creation methods are authoritative.
**Recommendation:** Delete the entire designs.py file if these functions are no longer needed, or move to test utilities if still useful for testing.
**Effort:** Simple

#### MAJOR: Unused BattleConfig.isolated Field
**ID:** LEG-SIM-002
**Location:** `game/simulation/battle_config.py:48`
**Issue:** The `isolated: bool = True` field in BattleConfig is defined but never read. No code checks `config.isolated` to determine behavior. The hypothetical mode handler hardcodes `should_clone_ships()` to return True regardless of this field.
**Impact:** Configuration field that does nothing creates confusion about expected behavior and is a source of potential bugs if someone assumes it works.
**Recommendation:** Either implement the intended functionality (checking config.isolated in HypotheticalBattleModeHandler) or remove the field entirely.
**Effort:** Simple

#### MAJOR: Unused validate_state Method in BattleStateManager
**ID:** LEG-SIM-003
**Location:** `game/simulation/managers/battle_state_manager.py:113-132`
**Issue:** The `validate_state()` method is defined but never called anywhere in the codebase. It appears to be dead code from an incomplete migration or feature that was never integrated.
**Impact:** Dead code adds to cognitive load when reading the BattleStateManager class.
**Recommendation:** Delete the method if validation is handled elsewhere, or integrate it into state restoration workflows if needed.
**Effort:** Simple

#### MINOR: Unused Documentation Constants in physics_constants.py
**ID:** LEG-SIM-004
**Location:** `game/simulation/physics_constants.py:27-29`
**Issue:** Three string constants (`FORMULA_MAX_SPEED`, `FORMULA_ACCELERATION`, `FORMULA_TURN_SPEED`) are defined as documentation references but never imported or used anywhere in the codebase.
**Impact:** Minor clutter in the physics constants module.
**Recommendation:** Either delete these constants or move the formula documentation to docstrings.
**Effort:** Simple

#### MINOR: Singleton Pattern in ComponentCacheManager
**ID:** LEG-SIM-005
**Location:** `game/simulation/components/component.py:435-465`
**Issue:** ComponentCacheManager uses a thread-safe singleton pattern (`_instance` class attribute with double-checked locking). While this is intentional for caching purposes, it's worth noting as the project has generally moved toward dependency injection patterns.
**Impact:** Makes testing harder as global state persists between tests (though reset_cache() method exists). Not a legacy holdover per se, but a deviation from the DI pattern used elsewhere.
**Recommendation:** Consider if this singleton could be replaced with a scoped cache injected via registries. Low priority as it has a clear purpose.
**Effort:** Complex

#### MINOR: KNOWN_ISSUE Comment for Module Identity Drift
**ID:** LEG-SIM-006
**Location:** `game/simulation/components/ability_manager.py:57-60`
**Issue:** A `[KNOWN_ISSUE]` comment documents a fallback for "Module Identity Drift" in tests, where isinstance() fails due to class object identity. This is documented as "intentional tech debt" from Phase 2.
**Impact:** Test isolation workaround that complicates the ability lookup code. The fallback check (`ab.__class__.__name__`) adds overhead.
**Recommendation:** Monitor if this workaround is still necessary with current test setup. May be able to remove if test module reloading patterns have changed.
**Effort:** Medium

#### MINOR: Excessive hasattr() Checks
**ID:** LEG-SIM-007
**Location:** Multiple files (ability_manager.py, battle_state.py, ship_formation.py, component.py)
**Issue:** There are 25+ uses of `hasattr()` checks throughout the simulation layer. While some are legitimate (checking for optional attributes), many appear to be defensive programming against incomplete objects or legacy compatibility. Examples:
- `if hasattr(ship, 'formation'):` in ship_formation.py
- `if hasattr(state, 'mode'):` in battle_state_manager.py
- `if hasattr(self, '_ability_index')` in component.py
**Impact:** Defensive hasattr() checks can mask bugs by silently skipping code paths. They also suggest incomplete confidence in object contracts.
**Recommendation:** Review each hasattr() usage. For well-defined objects, replace with proper attribute access or Protocol type hints. For optional features, document the expected cases.
**Effort:** Medium

#### MINOR: Fallback Comments Suggesting Incomplete Migration
**ID:** LEG-SIM-008
**Location:** Multiple files (ship.py:341,346,396, component.py:203,213,222, battle_engine.py:535)
**Issue:** Several comments mention "fallback" behavior:
- "Fallback if no layers defined in vehicle class" (ship.py:346)
- "Fallback if no mass limits defined" (ship.py:396)
- "Fallback: delegate to AbilityManager" (component.py:203,213,222)
- "Fallback (should never reach here)" (battle_engine.py:535)

While these are defensive defaults, they suggest edge cases that may not be exercised. The "should never reach here" comment in battle_engine.py is particularly concerning as it implies untested code paths.
**Impact:** Untested fallback paths could contain bugs.
**Recommendation:** Add test coverage for fallback scenarios or remove if truly unreachable.
**Effort:** Medium

#### INFO: Clean Migration Indicators
**ID:** LEG-SIM-009
**Location:** Throughout simulation layer
**Issue:** The codebase shows excellent signs of completed migrations:
- PROJ-50: Strict DI comments indicate fallback patterns were removed
- PROJ-42, PROJ-43, PROJ-126: Clean AI factory injection pattern
- No ImportError fallback patterns detected
- No deprecated/legacy/compat naming found in function/class names
- No TODO/FIXME comments found in simulation layer
**Impact:** Positive indicator that previous cleanup efforts were thorough.
**Recommendation:** Continue current practices.
**Effort:** N/A

#### INFO: Healthy Ability System Architecture
**ID:** LEG-SIM-010
**Location:** `game/simulation/components/abilities/`, `game/simulation/entities/ability_aggregator.py`
**Issue:** The ability system shows clean two-stage aggregation (collect then apply), proper use of AbilityStatBinding, and consistent polymorphic patterns via get_primary_value(). No evidence of inline component logic or direct mutation patterns that were replaced.
**Impact:** Positive indicator that the ability system migration is complete.
**Recommendation:** Use as reference pattern for future similar work.
**Effort:** N/A

## Top 5 Priority Issues

1. **LEG-SIM-001 (MAJOR):** Delete unused designs.py factory functions - immediate clutter removal
2. **LEG-SIM-002 (MAJOR):** Fix or remove BattleConfig.isolated field - eliminates misleading API
3. **LEG-SIM-003 (MAJOR):** Delete unused validate_state() method - immediate dead code removal
4. **LEG-SIM-004 (MINOR):** Remove unused physics formula constants - quick cleanup
5. **LEG-SIM-007 (MINOR):** Review hasattr() defensive checks - longer-term code quality improvement
