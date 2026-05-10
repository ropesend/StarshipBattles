# Legacy System Holdovers Sweep: Simulation

## Summary
- **Shard:** Simulation
- **Files Scanned:** 68
- **Total Issues Found:** 9
- **Critical:** 0 | **Major:** 4 | **Minor:** 4 | **Info:** 1

## Findings

#### MAJOR: Empty Factory Module (Dead Package)
**ID:** LEG-SIM-001
**Location:** `game/simulation/factories/__init__.py:1-12`
**Issue:** The factories package is empty and serves no purpose. The docstring explicitly states: "This package is now empty but kept for potential future simulation-layer factories that don't have cross-layer dependencies." PROJ-126 moved AIControllerFactory to game/ai/.
**Impact:** Orphaned module creates confusion about project structure. "Kept for potential future use" violates project policy against leaving dead code around.
**Recommendation:** Delete the entire `game/simulation/factories/` directory
**Effort:** Simple

#### MAJOR: Incomplete Migration - StrategyBattleModeHandler.apply_results() is a Stub
**ID:** LEG-SIM-002
**Location:** `game/simulation/combat/battle_mode_handler.py:225-240`
**Issue:** The apply_results() method builds mapping variables (surviving_by_name, destroyed_by_name, escaped_by_name) but never uses them. The comment states "implementation blocked by PROJ-41: Fleet/ShipInstance integration". The method signature and structure exist but does nothing.
**Impact:** Strategy mode battles don't actually apply results to fleets. This is an incomplete migration that may mask bugs where battle outcomes should affect fleet state.
**Recommendation:** Either complete the implementation or remove the stub code and document that apply_results is intentionally a no-op until PROJ-41 completes
**Effort:** Medium (requires understanding PROJ-41 scope)

#### MAJOR: Defensive getattr/hasattr Usage on Core Ship Attributes
**ID:** LEG-SIM-003
**Location:** Multiple files - see details
**Issue:** Extensive use of getattr with defaults on attributes that should always exist on Ship objects. Examples:
- `game/simulation/battle_state.py:212-225` - Uses getattr for ai_strategy, angle, current_shields, max_shields, is_derelict, retreat_status
- `game/simulation/combat/weapon_firing_system.py:63,177,250,277` - Uses getattr for is_derelict, max_targets, facing_angle, missile_hp
- `game/simulation/combat/damage_calculator.py:47,54` - Uses getattr for emissive_armor, crystalline_armor
- `game/simulation/combat/targeting_system.py:101,104,152,154,159,200` - Uses getattr for is_alive, team_id, type, velocity

These suggest either: (1) incomplete migration from old Ship class structure, or (2) defensive programming against objects that aren't actually Ship instances.
**Impact:** Creates confusion about the actual Ship interface. If these attributes don't always exist, there's a bug. If they always exist, the getattr is unnecessary defensive code that masks interface understanding.
**Recommendation:** Audit each usage - if attributes always exist on Ship, remove getattr. If not, fix Ship initialization to always provide these attributes.
**Effort:** Medium (requires careful analysis of each case)

#### MAJOR: Hasattr Checks for ability_instances on Components
**ID:** LEG-SIM-004
**Location:** Multiple files:
- `game/simulation/entities/ability_aggregator.py:101,206`
- `game/simulation/entities/ship_stats.py:281`
- `game/simulation/entities/combat_endurance.py:42`
**Issue:** Code checks `if hasattr(comp, 'ability_instances')` before accessing. The ability_instances list is always initialized in Component.__init__, so this check suggests the code was written when ability_instances might not exist (legacy pattern) or handles non-Component objects.
**Impact:** Unnecessary defensive code that obscures the actual Component interface contract.
**Recommendation:** Remove hasattr checks since ability_instances is always present. If the code handles non-Component objects, add type annotations/guards.
**Effort:** Simple

#### MINOR: V1 Modifier Format Check Still Present
**ID:** LEG-SIM-005
**Location:** `game/simulation/components/modifier_schema.py:36,50`
**Issue:** The ModifierDefinition constructor raises ValueError for "deprecated V1 format (dict-based effects)". This error-checking code remains even though all V1 modifiers should have been migrated. If there are no V1 modifiers left in data files, this is dead validation code.
**Impact:** Minor maintenance burden - the check runs every time a modifier is loaded but should never trigger.
**Recommendation:** Verify no V1 modifiers exist in data/modifiers.json, then remove the V1 format check
**Effort:** Simple

#### MINOR: Projectile Type String Conversion Pattern
**ID:** LEG-SIM-006
**Location:** `game/simulation/entities/projectile.py:47-53`
**Issue:** The Projectile.__init__ checks `if isinstance(proj_type, str)` and converts string types to AttackType enum. Comment says "Log warning but allow fallback for extensibility". This suggests a migration period where proj_type could be either string or enum.
**Impact:** If all callers now pass AttackType enum, this fallback is dead code. If some callers still pass strings, they should be updated.
**Recommendation:** Audit all Projectile instantiations. If all pass AttackType enum, remove string handling.
**Effort:** Simple

#### MINOR: Legacy Comment References (PROJ-106 Legacy Path Removed Notes)
**ID:** LEG-SIM-007
**Location:** `game/simulation/systems/battle_engine.py:270,322,470`
**Issue:** Multiple comments state "PROJ-106: Legacy path removed. All production code now uses ai_factory." followed by raising ValueError. The comments correctly document the migration, but the term "legacy path" in the error messages may confuse users.
**Impact:** Minor - error messages reference "legacy" behavior that no longer exists
**Recommendation:** Simplify error messages to just state what is required, not what was removed
**Effort:** Simple

#### MINOR: Stale Docstring Reference to Legacy Behavior
**ID:** LEG-SIM-008
**Location:** `game/simulation/systems/battle_engine.py:177-178`
**Issue:** Docstring says "If None, imports from game.ai directly (legacy behavior)" for ai_factory parameter. But this legacy behavior was removed (PROJ-106) - the code now raises ValueError if ai_factory is None and no ai_controllers are provided.
**Impact:** Misleading documentation
**Recommendation:** Update docstring to reflect current behavior (ai_factory is required unless ai_controllers provided)
**Effort:** Simple

#### INFO: reset_component_caches() Function Appears Unused in Production
**ID:** LEG-SIM-009
**Location:** `game/simulation/components/component.py:468-473`
**Issue:** The reset_component_caches() function exists but grep shows only its definition, no callers. It delegates to ComponentCacheManager.reset(). The ComponentCacheManager singleton pattern may be a holdover from an earlier architecture.
**Impact:** If unused, this is dead code. May be used only in tests.
**Recommendation:** Search test files for usage. If only test usage, consider moving to test utilities. If unused entirely, delete.
**Effort:** Simple (verification needed)

## Top 5 Priority Issues

1. **LEG-SIM-002 (MAJOR)** - StrategyBattleModeHandler.apply_results() stub: Creates false sense that strategy battles apply fleet effects when they don't. Either complete or clearly document as no-op.

2. **LEG-SIM-003 (MAJOR)** - Defensive getattr/hasattr on Ship attributes: Most impactful code clarity issue. The Ship class interface is unclear when code defensively accesses attributes that should always exist.

3. **LEG-SIM-001 (MAJOR)** - Empty factories module: Low effort, high clarity win. Delete the empty package.

4. **LEG-SIM-004 (MAJOR)** - Hasattr checks for ability_instances: Clarifies Component interface contract. Simple fix once verified.

5. **LEG-SIM-008 (MINOR)** - Stale docstring: Quick documentation fix that prevents confusion about ai_factory parameter behavior.
