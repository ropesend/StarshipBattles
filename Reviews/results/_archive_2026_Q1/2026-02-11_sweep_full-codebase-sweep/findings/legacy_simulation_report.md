# Legacy System Holdovers Sweep: Simulation

## Summary
- **Shard:** Simulation (SIM)
- **Files Scanned:** 76 Python files
- **Total Issues Found:** 21
- **Critical:** 3 | **Major:** 8 | **Minor:** 7 | **Info:** 3

## Findings

---

### Phase 1: Dead Code Paths

#### CRITICAL: Empty ABILITY_CLASS_MAP dict still imported and checked at runtime
**ID:** LEG-SIM-001
**Location:** `game/simulation/components/abilities/__init__.py:111`, `game/simulation/components/ability_manager.py:165,191`
**Issue:** `ABILITY_CLASS_MAP = {}` is defined as an empty dict (line 111 of `__init__.py`) with comment "(Legacy shortcuts removed)". However, `AbilityManager._ensure_ability_instances()` still imports and iterates over it at line 191: `target_cls_name = ABILITY_CLASS_MAP.get(name)`. This code path always returns `None` from the empty dict, making the entire `ABILITY_CLASS_MAP` lookup block dead code that executes on every component initialization.
**Impact:** Wasted runtime cycles on every component ability resolution. Creates confusion about whether the map is still used or expected to have entries. PROJ-53 cleared entries but left the infrastructure.
**Recommendation:** Delete `ABILITY_CLASS_MAP` from `__init__.py` and remove the lookup block in `ability_manager.py`. All ability resolution should go through the ABILITY_REGISTRY.
**Effort:** Simple

---

#### MAJOR: ability_aggregator dict-format branch is dead code
**ID:** LEG-SIM-002
**Location:** `game/simulation/entities/ability_aggregator.py:134-137`
**Issue:** `isinstance(comp.ability_instances, dict)` branch contains only `pass`. The `ability_instances` attribute is always a list (initialized in `Component.__init__`), never a dict. This branch was likely a compatibility path for an older format that no longer exists.
**Impact:** Dead code that misleads developers about possible data formats. Makes the function appear to handle two formats when it only handles one.
**Recommendation:** Delete the `elif isinstance(comp.ability_instances, dict): pass` block.
**Effort:** Simple

---

#### MAJOR: persistence.py ShipIO calls Ship.from_dict without required registries parameter
**ID:** LEG-SIM-003
**Location:** `game/simulation/systems/persistence.py:92`
**Issue:** `Ship.from_dict(data)` is called without the required `registries=` keyword argument. `ShipSerializer.from_dict()` (which Ship.from_dict delegates to) raises `TypeError` if `registries is None`. This means the `load_design_dialog()` function in `ShipIO` would crash at runtime if ever called.
**Impact:** The entire `ShipIO.load_design_dialog()` method is broken. Production code uses `ShipIOAdapter` (in `game/ui/services/`) which wraps `ShipIO` but the underlying method is non-functional. This is a dead code path that would fail if reached.
**Recommendation:** Either fix the DI by passing `registries=` parameter, or mark/delete ShipIO as deprecated since `ShipIOAdapter` is the intended production API.
**Effort:** Medium

---

#### MAJOR: persistence.py imports tkinter (UI dependency in simulation layer)
**ID:** LEG-SIM-004
**Location:** `game/simulation/systems/persistence.py:3`
**Issue:** `import tkinter` at the top of a simulation-layer module. ShipIO uses tkinter file dialogs (`filedialog.askopenfilename`, `filedialog.asksaveasfilename`) for save/load. This violates the layer separation principle (simulation should have no UI dependencies). The `ShipIOAdapter` in `game/ui/services/` was created specifically to wrap this, but the simulation-layer module still has the tkinter import.
**Impact:** Importing this module in a headless environment (CI, server) would fail if tkinter is not installed. Layer boundary violation.
**Recommendation:** Move ShipIO to `game/ui/` layer or delete it entirely since `ShipIOAdapter` exists as the production replacement.
**Effort:** Medium

---

#### MAJOR: designs.py hardcoded ship factories only called from tests and scripts
**ID:** LEG-SIM-005
**Location:** `game/simulation/designs.py:11-66`
**Issue:** `create_brick()` and `create_interceptor()` are hardcoded ship factory functions that manually construct ships by calling `add_component()` repeatedly with hardcoded component IDs. These are only used by: `tests/unit/builder/test_designs.py`, `tests/unit/performance/stress_test.py`, `tests/unit/performance/profile_simulation.py`, and `scripts/verify_determinism_current.py`. No production code imports from `game.simulation.designs`.
**Impact:** Maintenance burden when component IDs change. Duplicates what JSON ship designs provide. The entire module is test/script infrastructure masquerading as production code.
**Recommendation:** Move to `tests/helpers/` or `scripts/` since no production code depends on it. Or delete and replace test usages with JSON-based ship loading.
**Effort:** Medium

---

#### MINOR: FORMULA_* string constants are documentation-only, never used in calculations
**ID:** LEG-SIM-006
**Location:** `game/simulation/physics_constants.py:27-29`
**Issue:** `FORMULA_MAX_SPEED`, `FORMULA_ACCELERATION`, `FORMULA_TURN_SPEED` are string constants containing human-readable formula descriptions (e.g., `"max_speed = (total_thrust * K_SPEED) / mass"`). They are only referenced in `tests/unit/simulation/test_physics_constants.py` to verify their string content. No production code uses them.
**Impact:** Minimal. They serve as documentation, but they are tests that just verify string content, not formula correctness.
**Recommendation:** Keep as documentation or move to docstrings. The test assertions that verify string content provide no value.
**Effort:** Simple

---

### Phase 2: Compatibility Shims & Wrappers

#### CRITICAL: resource_manager.py re-exports ability classes from old location
**ID:** LEG-SIM-007
**Location:** `game/simulation/systems/resource_manager.py:211-222`
**Issue:** The bottom of `resource_manager.py` contains a compatibility re-export block:
```python
# --- Ability System ---
# Forwarding to new module
from game.simulation.components.abilities.resources import (
    ResourceConsumption,
    ResourceStorage,
    ResourceGeneration,
)
```
Multiple callers still import these classes from the old location (`from game.simulation.systems.resource_manager import ResourceConsumption`), including: `ship_validator.py`, `ship_stats.py`, `ability_manager.py`, `stats_config.py` (UI), and at least 8 test files. The canonical location is `game.simulation.components.abilities.resources`.
**Impact:** Violates the project policy: "When a new system replaces an old one, ERADICATE the old system completely." The re-export creates confusion about which module is authoritative for these classes. New developers may import from either location.
**Recommendation:** Update ALL import sites to use `game.simulation.components.abilities.resources` directly, then delete the re-export block.
**Effort:** Medium

---

#### CRITICAL: component.py uses get_default_registry_provider (old singleton pattern)
**ID:** LEG-SIM-008
**Location:** `game/simulation/components/component.py:65,502,557,656`
**Issue:** `component.py` imports and uses `get_default_registry_provider` (the old singleton provider pattern) in three module-level functions: `load_components_data()` (line 502), `load_components()` (line 557), and `load_modifiers()` (line 656). The project has migrated to `RegistryManager.instance()` and strict DI via `registries=` parameter throughout PROJ-50. `ship_loader.py` already has the comment "PROJ-50: Removed get_default_registry_provider import - use RegistryManager instead."
**Impact:** These functions use the old singleton access pattern while the rest of the simulation layer uses the new DI pattern. This creates an inconsistency in how registries are accessed, making the migration incomplete.
**Recommendation:** Migrate `load_components_data()`, `load_components()`, and `load_modifiers()` to accept `registries` parameter (DI) or use `RegistryManager.instance()`.
**Effort:** Medium

---

#### MAJOR: String-based missile type checking is a compatibility shim
**ID:** LEG-SIM-009
**Location:** `game/simulation/entities/projectile.py:87,95,106` and `game/simulation/projectile_manager.py:150`
**Issue:** Four locations use dual type checking: `self.type == AttackType.MISSILE or self.type == 'missile'`. The string `'missile'` fallback is a compatibility shim for cases where the type might be a raw string instead of the `AttackType` enum. Since the AttackType enum is the canonical type system, the string check is legacy.
**Impact:** Creates confusion about whether string types are still valid. Each type check is more complex than needed. If someone passes a string type, it works silently instead of failing fast.
**Recommendation:** Remove the `or self.type == 'missile'` checks. Ensure all projectile creation uses `AttackType` enum values.
**Effort:** Simple

---

#### MAJOR: Multiple hasattr/getattr checks for always-present Ship attributes
**ID:** LEG-SIM-010
**Location:** Multiple files (see details below)
**Issue:** Several files use defensive `hasattr()` or `getattr()` checks for Ship attributes that are always initialized in `Ship.__init__()`:

1. `battle_state.py:201` - `hasattr(ship, 'current_target')` - `current_target` is always set in Ship.__init__
2. `battle_state.py:212` - `getattr(ship, 'ai_strategy', 'standard_ranged')` - always set in Ship.__init__
3. `battle_state.py:215` - `getattr(ship, 'angle', 0)` - always set in Ship.__init__
4. `battle_state.py:317` - `hasattr(ship, 'retreat_status')` - set by RetreatManager
5. `ship_formation.py:91,109` - `hasattr(ship, 'formation')` - always set in Ship.__init__
6. `ship_combat_engine.py:180` - `hasattr(ship, 'resources')` - always initialized in Ship.__init__
7. `retreat_manager.py:170` - `hasattr(ship, 'retreat_status')` - should always exist on ships in retreat context

**Impact:** These defensive checks are vestiges of when Ship attributes were optional or added dynamically. They add noise to the code and mask potential bugs (if the attribute truly were missing, the hasattr would silently skip important logic).
**Recommendation:** Remove the `hasattr`/`getattr` guards and access attributes directly. If an attribute is truly optional, document it explicitly.
**Effort:** Simple

---

#### MINOR: shots_hit attribute dynamically added instead of initialized
**ID:** LEG-SIM-011
**Location:** `game/simulation/projectile_manager.py:173-175` and `game/simulation/combat/weapon_firing_system.py:214-216`
**Issue:** Both `ProjectileManager._record_hit()` and `WeaponFiringSystem` use `hasattr(comp/p.source_weapon, 'shots_hit')` to check if the attribute exists before incrementing it. The attribute is lazily initialized with `comp.shots_hit = 0` if missing. This pattern suggests `shots_hit` was added after the original Component design and was never properly added to `Component.__init__()`.
**Impact:** Minor inefficiency and code smell. The `hasattr` check runs on every hit.
**Recommendation:** Initialize `shots_hit = 0` (and `shots_fired = 0`) in `Component.__init__()` so they always exist.
**Effort:** Simple

---

#### MINOR: combat_endurance.py legacy fallback for reload_time
**ID:** LEG-SIM-012
**Location:** `game/simulation/entities/combat_endurance.py:69-71`
**Issue:** Comment reads `# Fallback to component attribute (Legacy)` followed by `reload_t = getattr(c, 'reload_time', 1.0)`. This is a fallback for when the WeaponAbility doesn't provide a reload_time through the ability system.
**Impact:** Small. The ability system always provides reload_time for weapon abilities, so this fallback likely never triggers.
**Recommendation:** Verify via testing that the ability path always succeeds, then remove the legacy fallback.
**Effort:** Simple

---

### Phase 3: Obsolete Patterns

#### MAJOR: ResourceDependencyRule has dual-path validation (ability vs raw data)
**ID:** LEG-SIM-013
**Location:** `game/simulation/validation/ship_validator.py:346-380`
**Issue:** `ResourceDependencyRule._do_validate()` has two code paths:
1. Lines 346-361: Uses `ability_instances` (V2 ability system) to check ResourceConsumption/ResourceStorage.
2. Lines 362-380: `else` fallback that accesses `getattr(c, 'abilities', {})` as raw dicts for "uninitialized components".

The fallback path uses the old raw-dict ability format (`abilities['ResourceConsumption']`), which is the pre-ability-system pattern. All components now have `ability_instances` initialized, so the fallback is dead code.
**Impact:** The fallback path is untested dead code that uses the old data format. It creates confusion about which data format is canonical.
**Recommendation:** Delete the `else` branch (lines 362-380). All components have `ability_instances`.
**Effort:** Simple

---

#### MAJOR: WeaponAbility.recalculate() uses hasattr for always-present base attributes
**ID:** LEG-SIM-014
**Location:** `game/simulation/components/abilities/weapons.py:155-163`
**Issue:** `WeaponAbility.recalculate()` starts with `pass` (dead statement at line 152), then uses `hasattr(self, '_base_damage')`, `hasattr(self, '_base_range')`, `hasattr(self, '_base_reload')`, and `hasattr(self, '_base_firing_arc')` checks. These `_base_*` attributes are always set in `WeaponAbility.__init__()` (lines 67, 82, 97, 109), so the `hasattr` checks always pass.
**Impact:** Unnecessary defensive checks that add visual noise. The leading `pass` statement is dead code.
**Recommendation:** Remove the `pass` and all `hasattr` checks. Access `_base_*` attributes directly.
**Effort:** Simple

---

#### MINOR: CargoStorage uses string layer instead of AbilityLayer enum
**ID:** LEG-SIM-015
**Location:** `game/simulation/components/abilities/cargo.py:29`
**Issue:** `layer = 'strategic'` uses a raw string instead of `AbilityLayer.STRATEGIC`. All other strategic abilities (WarpJump, StrategicMovement, ColonizePlanet, superweapons) use the `AbilityLayer.STRATEGIC` enum.
**Impact:** Inconsistency. The string `'strategic'` might not match in `applies_to_layer()` comparisons that use the Flag enum.
**Recommendation:** Change to `layer = AbilityLayer.STRATEGIC` and add the import.
**Effort:** Simple

---

#### MINOR: ability_manager.py has [KNOWN_ISSUE] workaround for module identity drift
**ID:** LEG-SIM-016
**Location:** `game/simulation/components/ability_manager.py:57`
**Issue:** Comment reads `[KNOWN_ISSUE] Fallback for Module Identity Drift in tests.` followed by a `__name__` fallback for isinstance checks. This workaround handles cases where the same class is imported from different module paths, causing isinstance to fail.
**Impact:** Test infrastructure workaround that should be addressed at the root cause (consistent import paths) rather than with runtime workarounds.
**Recommendation:** Investigate and fix the inconsistent import paths that cause module identity drift, then remove the workaround.
**Effort:** Complex

---

### Phase 4: Orphaned Resources

#### MINOR: Ship.base_mass is always 0.0 - vestigial attribute
**ID:** LEG-SIM-017
**Location:** `game/simulation/entities/ship.py:86-87` and `game/simulation/entities/ship.py:429`
**Issue:** `ship.base_mass = 0.0` is set in both `Ship.__init__()` and `Ship.change_class()` with comment "base_mass is always 0.0 - Hull component provides all base mass via ShipStatsCalculator". The `ShipStatsCalculator` at line 89 computes `ship.mass = ship.current_mass + ship.base_mass`, but since `base_mass` is always 0.0, this is equivalent to `ship.mass = ship.current_mass`.
**Impact:** Vestigial attribute from when ships had intrinsic mass separate from components. Adds confusion by suggesting ships can have non-zero base mass.
**Recommendation:** Remove `base_mass` and simplify `ship.mass = ship.current_mass` in ShipStatsCalculator.
**Effort:** Simple

---

#### MINOR: Duplicate shield_regen_cost initialization in ShipStatsCalculator
**ID:** LEG-SIM-018
**Location:** `game/simulation/entities/ship_stats.py:114-115`
**Issue:** `ship.shield_regen_cost = 0` appears on two consecutive lines (114 and 115). This is a simple copy-paste error.
**Impact:** No functional impact, just code noise.
**Recommendation:** Delete one of the duplicate lines.
**Effort:** Simple

---

### Phase 5: Incomplete Migrations

#### MAJOR: _apply_results_to_fleet is a complete stub blocked by PROJ-41
**ID:** LEG-SIM-019
**Location:** `game/simulation/battle_controller.py:645-665`
**Issue:** `_apply_results_to_fleet()` method body is just `pass`. Called from `apply_results_to_fleets()` at lines 634 and 639. The docstring explains: "BLOCKING DEPENDENCY: This method cannot be implemented until PROJ-41 (Fleet/ShipInstance Integration)". Similarly, `StrategyBattleModeHandler.apply_results()` at `battle_mode_handler.py:235` is also a stub blocked by PROJ-41.
**Impact:** Strategy battles that use fleet integration cannot propagate battle results back to fleets. The entire `apply_results_to_fleets()` method (lines 617-643) has a fallback path that duplicates mode handler logic, working around the stub.
**Recommendation:** Track PROJ-41 as a blocker. When implementing, also clean up the duplicated fallback logic in `apply_results_to_fleets()`.
**Effort:** Complex (requires PROJ-41 implementation)

---

#### MAJOR: is_v2_format() implies V1 format still exists
**ID:** LEG-SIM-020
**Location:** `game/simulation/components/modifier_schema.py:22`
**Issue:** `is_v2_format()` function validates that a modifier uses the V2 array-based effects format. Its existence implies V1 (dict-based) modifiers might still be encountered. The modifiers.py file confirms "V1 handler functions were removed in Phase 7 cleanup". If V1 is fully eradicated, the function name is misleading.
**Impact:** Creates confusion about whether V1 format is still supported. Used only in tests, never in production code paths.
**Recommendation:** Rename to `is_valid_modifier_format()` or `validate_modifier_effects_format()` to remove the V1/V2 naming. Or delete if only tests need it.
**Effort:** Simple

---

#### INFO: ShipStatsCalculator._check_mass_limits hardcodes default mass budget
**ID:** LEG-SIM-021
**Location:** `game/simulation/entities/ship_stats.py:474`
**Issue:** `ship.max_mass_budget = 1000 # Default` is set before looking up the actual value from vehicle_classes. This hardcoded default is a fallback for when the vehicle class definition doesn't specify mass_budget. The value 1000 appears to be arbitrary.
**Impact:** If a vehicle class is missing mass_budget, ships silently get 1000 mass budget instead of failing loudly.
**Recommendation:** Consider raising an error or warning if mass_budget is not defined in the vehicle class, rather than silently defaulting.
**Effort:** Simple

---

#### INFO: TechPresetLoader has no production callers
**ID:** LEG-SIM-022
**Location:** `game/simulation/systems/tech_preset_loader.py:23`
**Issue:** `TechPresetLoader` is defined in the simulation layer but has no imports from any production code in `game/`. It is only imported from `tests/unit/systems/test_tech_preset_loader.py`. The class was created during workshop refactoring but may not have been wired into the actual workshop UI.
**Impact:** 200 lines of code with no production callers. The test coverage exists but the feature is disconnected from the application.
**Recommendation:** Either wire TechPresetLoader into the workshop/builder UI as intended, or move to a `_future/` or remove if the feature direction has changed.
**Effort:** Medium

---

#### INFO: EmpireStorageAbility uses non-standard stat key 'storage_mult'
**ID:** LEG-SIM-023
**Location:** `game/simulation/components/abilities/harvester.py:72`
**Issue:** `EmpireStorageAbility.recalculate()` calls `self.get_effective_stat('storage_mult', 1.0)` but `storage_mult` is not defined in `StatKey` enum (`stat_keys.py`). Other abilities use `StatKey.CAPACITY_MULT` for capacity scaling. This means modifiers targeting `storage_mult` would need to use a raw string key rather than the enum.
**Impact:** Inconsistency with the stat key system. Storage modifiers for empire buildings would bypass the `StatKey` enum validation.
**Recommendation:** Either add `STORAGE_MULT` to `StatKey` enum, or use `StatKey.CAPACITY_MULT` like other storage abilities.
**Effort:** Simple

---

## Top 5 Priority Issues

1. **LEG-SIM-007 (CRITICAL)** - resource_manager.py re-exports ability classes. 12+ callers import from the old location. This is the largest active compatibility shim in the simulation layer, directly violating the project's eradication policy. Fix all import sites, then delete the re-exports.

2. **LEG-SIM-008 (CRITICAL)** - component.py uses `get_default_registry_provider`. Three module-level functions use the old singleton pattern while the rest of the project has migrated to DI/RegistryManager. This is an incomplete PROJ-50 migration.

3. **LEG-SIM-003 (MAJOR) + LEG-SIM-004 (MAJOR)** - persistence.py is broken (missing registries DI) and violates layer boundaries (tkinter import). The entire ShipIO class in the simulation layer should be deprecated in favor of the UI-layer ShipIOAdapter.

4. **LEG-SIM-009 (MAJOR)** - String-based missile type checking. Four locations use `'missile'` string fallback alongside `AttackType.MISSILE` enum. Clean enum usage throughout would eliminate this.

5. **LEG-SIM-019 (MAJOR)** - `_apply_results_to_fleet()` stub blocked by PROJ-41 with duplicated fallback logic in the caller. This is a known architectural gap, but the workaround code adds maintenance burden.
