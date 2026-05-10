# Legacy System Holdovers Sweep: Simulation

## Summary
- **Shard:** Simulation
- **Files Scanned:** 69
- **Total Issues Found:** 11
- **Critical:** 0 | **Major:** 3 | **Minor:** 6 | **Info:** 2

## Findings

#### MAJOR: Module Identity Drift Fallback in AbilityManager
**ID:** LEG-SIM-001
**Location:** `game/simulation/components/ability_manager.py:57-65`
**Issue:** The `get_abilities()` method contains a documented fallback that checks `__class__.__name__` when `isinstance()` fails due to "Module Identity Drift" during test reloads. This is labeled as `[KNOWN_ISSUE]` with comment: "Ref: Phase 2 Task 2.5 audit - documented as intentional tech debt."
**Impact:** This is a workaround for test isolation issues that adds complexity to a hot-path method. The MRO traversal on every ability lookup adds overhead.
**Recommendation:** Consider using consistent module import patterns in tests to eliminate the identity drift issue, then remove this fallback path.
**Effort:** Medium

#### MAJOR: Singleton Pattern in Component Cache Manager
**ID:** LEG-SIM-002
**Location:** `game/simulation/components/component.py:435-465`
**Issue:** `ComponentCacheManager` uses a thread-safe singleton pattern with `_instance` class variable. While the project has moved toward DI, this singleton pattern persists for caching component and modifier definitions loaded from JSON files.
**Impact:** Makes testing harder, requires manual `reset()` calls between tests, and contradicts the DI pattern used elsewhere in the codebase. The singleton manages global state that could conflict with test isolation.
**Recommendation:** Consider refactoring to inject the cache manager as a dependency or integrate caching into GameRegistries.
**Effort:** Complex

#### MAJOR: Dead Fallback Code in BattleController._apply_results_to_fleet
**ID:** LEG-SIM-003
**Location:** `game/simulation/battle_controller.py:656-672`
**Issue:** The method `_apply_results_to_fleet` is documented as "exists as a fallback path but is not used in production - the strategy layer owns fleet update responsibility." The method body is just `pass`, making it dead code. The calling method `apply_results_to_fleets` (lines 608-654) has a "defensive fallback" block that can theoretically reach this code but should never execute.
**Impact:** Dead code creates confusion about where fleet updates happen. Comments suggest this was part of an incomplete migration.
**Recommendation:** Delete `_apply_results_to_fleet` and the fallback block in `apply_results_to_fleets` since mode handlers now handle all result application.
**Effort:** Simple

#### MINOR: Defensive hasattr Checks for Attributes That Should Always Exist
**ID:** LEG-SIM-004
**Location:** Multiple files - see details below
**Issue:** Multiple `hasattr()` checks exist for attributes that are always initialized in constructors, suggesting old compatibility concerns:
- `battle_state.py:201` - `hasattr(ship, 'current_target')` - Ship always has current_target
- `battle_state.py:598,602` - `hasattr(engine, 'end_condition')` - BattleEngine always has end_condition
- `projectile.py:139` - `hasattr(self.owner, 'combat_engine')` - Ship always has combat_engine property
- `ship.py:221` - `hasattr(self, '_combat_engine')` - This is the lazy init pattern, acceptable
- `component.py:200,209,219` - `hasattr(self, '_ability_index')` - Component always has _ability_index after init
**Impact:** Adds unnecessary checks that clutter code and suggest uncertainty about object state.
**Recommendation:** Audit each hasattr check and remove those for attributes that are guaranteed by constructors.
**Effort:** Simple

#### MINOR: getattr with Defaults for Always-Present Attributes
**ID:** LEG-SIM-005
**Location:** Multiple files - extensive use
**Issue:** Extensive use of `getattr(obj, 'attr', default)` for attributes that should always exist. Examples:
- `targeting_system.py:101,104,152,154,159` - Checks like `getattr(candidate, 'is_alive', True)` for Ship objects
- `projectile.py:19` - `getattr(owner, 'team_id', -1)` where owner is always a Ship
- `ship_physics.py:28,34,82` - Defensive getattr for Ship's own attributes
**Impact:** Suggests historical uncertainty about object interfaces that has since been resolved. Adds unnecessary runtime overhead.
**Recommendation:** Review each usage; replace with direct attribute access where attributes are guaranteed.
**Effort:** Simple

#### MINOR: Stale Docstring Reference to Removed Fallback
**ID:** LEG-SIM-006
**Location:** `game/simulation/services/modifier_service.py:7-8`
**Issue:** Module docstring references "PROJ-42: Simplified DI pattern with _get_modifiers_fallback()" followed by "PROJ-50: Removed fallback pattern - strict DI required." The `_get_modifiers_fallback()` no longer exists, but the docstring documents its past existence.
**Impact:** Minor documentation cruft - confusing for readers trying to understand the code history.
**Recommendation:** Simplify docstring to just state current pattern without referencing removed code.
**Effort:** Simple

#### MINOR: Similar Stale Documentation in vehicle_design_service.py
**ID:** LEG-SIM-007
**Location:** `game/simulation/services/vehicle_design_service.py:7`
**Issue:** Same pattern - docstring says "PROJ-50: Removed fallback pattern - strict DI required" documenting past state.
**Impact:** Minor documentation cruft.
**Recommendation:** Clean up docstrings to describe current state, not migration history.
**Effort:** Simple

#### MINOR: Fallback Comment in battle_engine.py
**ID:** LEG-SIM-008
**Location:** `game/simulation/systems/battle_engine.py:535`
**Issue:** Comment "# Fallback (should never reach here)" in `is_battle_over()` method suggests defensive coding for impossible state. If it truly can never be reached, the code path is dead.
**Impact:** Dead code path with no practical effect.
**Recommendation:** Either remove the comment and return statement, or add an assertion to catch unexpected states during development.
**Effort:** Simple

#### MINOR: Unused Parameter in _apply_results_to_fleet
**ID:** LEG-SIM-009
**Location:** `game/simulation/battle_controller.py:656-672`
**Issue:** Method accepts `team_id`, `surviving`, `destroyed`, `escaped` parameters but the body is just `pass`. This is related to LEG-SIM-003.
**Impact:** Unused parameters indicate incomplete implementation or dead code.
**Recommendation:** Delete the method entirely (part of LEG-SIM-003 fix).
**Effort:** Simple (same fix as LEG-SIM-003)

#### INFO: Documented Technical Debt in ability_manager.py
**ID:** LEG-SIM-010
**Location:** `game/simulation/components/ability_manager.py:60`
**Issue:** Comment explicitly documents intentional tech debt: "Ref: Phase 2 Task 2.5 audit - documented as intentional tech debt."
**Impact:** This is properly documented technical debt, not forgotten legacy code. The team made a conscious decision to accept this.
**Recommendation:** Track in a tech debt backlog; address when test infrastructure is improved.
**Effort:** N/A (documented decision)

#### INFO: Consistent Use of Fallback Patterns in Data Loading
**ID:** LEG-SIM-011
**Location:** `game/simulation/services/registry_loader.py:76-88`, `game/simulation/entities/ship.py:346-354`
**Issue:** Several "fallback" patterns exist for handling missing data files or configuration:
- `registry_loader.py` has `find_file()` helper with test_ prefix fallback
- `ship.py` has fallback layer definitions if none defined in vehicle class
These are legitimate defaults, not legacy compatibility shims.
**Impact:** None - these are valid defensive patterns for handling optional/missing configuration.
**Recommendation:** None needed - these are appropriate fallback patterns.
**Effort:** N/A

## Top 5 Priority Issues

1. **LEG-SIM-003: Dead Fallback Code in BattleController** - Simple fix to remove clearly dead code documented as "not used in production." This creates confusion about where fleet updates happen.

2. **LEG-SIM-002: Singleton Pattern in ComponentCacheManager** - Contradicts the DI pattern used elsewhere and makes testing harder. Should be considered for refactoring when the component system is next touched.

3. **LEG-SIM-001: Module Identity Drift Fallback** - Documented tech debt that adds complexity to a frequently-called method. Should be prioritized when test infrastructure is improved.

4. **LEG-SIM-004/005: Defensive hasattr/getattr Usage** - Minor but pervasive pattern suggesting historical uncertainty. A sweep to clean these up would improve code clarity.

5. **LEG-SIM-006/007: Stale Documentation** - Minor cleanup task to remove references to removed code patterns.

---

## Analysis Summary

The simulation layer is in good shape overall. The major migrations (PROJ-50 strict DI, PROJ-58 combat mixin removal, God Class decomposition) have been largely completed. The remaining issues fall into three categories:

1. **Documented Tech Debt** (LEG-SIM-001, LEG-SIM-010): Conscious decisions with known tradeoffs, properly documented.

2. **Dead/Vestigial Code** (LEG-SIM-003, LEG-SIM-008): Small amounts of code that survived cleanup passes, easy to remove.

3. **Defensive Coding Patterns** (LEG-SIM-004, LEG-SIM-005): hasattr/getattr checks that were likely needed historically but are now redundant given the strict typing and DI patterns in place.

The singleton pattern in ComponentCacheManager (LEG-SIM-002) is the most significant architectural holdover, but it serves a legitimate caching purpose and doesn't create immediate problems.
