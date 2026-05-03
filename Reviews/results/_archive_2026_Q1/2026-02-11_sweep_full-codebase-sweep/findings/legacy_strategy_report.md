# Legacy System Holdovers - Strategy Layer Report

**Scope:** `game/strategy/` (all subdirectories)
**Date:** 2026-02-11
**Files Scanned:** 87 Python files (exhaustive)
**Methodology:** 5-phase analysis (Dead Code, Compatibility Shims, Obsolete Patterns, Orphaned Resources, Incomplete Migrations)

---

## Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| MAJOR | 5 |
| MINOR | 9 |
| INFO | 5 |
| **Total** | **19** |

---

## Phase 1: Dead Code Paths

### LSH-001: Dead method `_generate_mass()` in PlanetGenerator

- **ID:** LSH-001
- **Severity:** MINOR
- **Location:** `game/strategy/data/planet_gen.py` line 382
- **Issue:** `PlanetGenerator._generate_mass()` is never called. It was replaced by `_generate_mass_constrained()` (line 172), which is the version actually invoked from `_generate_orbital_slots()` at line 166. The old method has different parameters (`is_companion`, `primary_mass`) compared to the constrained version (`mass_min`, `mass_max`, `mass_bias`).
- **Impact:** 30+ lines of dead code. Potential confusion about which mass generation method is authoritative.
- **Recommendation:** Delete `_generate_mass()` method entirely. It is superseded by `_generate_mass_constrained()`.
- **Effort:** Trivial (delete method, verify no callers)

### LSH-002: Duplicated `_find_system_at_location()` across two files

- **ID:** LSH-002
- **Severity:** MAJOR
- **Location:** `game/strategy/validation/superweapon_validator.py` line 36 AND `game/strategy/engine/superweapon_order_processor.py` line 47
- **Issue:** The same `_find_system_at_location()` logic is implemented identically in both `SuperweaponValidator` (as a static method) and `SuperweaponOrderProcessor` (as an instance method). Both iterate galaxy systems checking planets, stars, and warp points for location matches. This is code duplication, not a legacy holdover per se, but it creates a maintenance risk where a fix in one location would not propagate to the other.
- **Impact:** Bug fixes or optimizations must be applied in two places. A Galaxy-level method would be more appropriate.
- **Recommendation:** Extract to a Galaxy method (e.g., `galaxy.find_system_containing(location)`) or a shared utility function, then update both callers.
- **Effort:** Small (extract shared method, update 2 call sites)

### LSH-003: Duplicate `_calculate_maintenance_cost()` in two engines

- **ID:** LSH-003
- **Severity:** MAJOR
- **Location:** `game/strategy/engine/empire_economy_calculator.py` line 256 AND `game/strategy/engine/maintenance_engine.py` line 189
- **Issue:** Both `EmpireEconomyCalculator._calculate_maintenance_cost()` and `MaintenanceEngine._calculate_maintenance_cost()` implement the identical algorithm: iterate layers, handle both dict and list formats, sum `resource_cost`, apply 5% rate. Both use the same `MAINTENANCE_RATE = 0.05`. The economy calculator is read-only (for display), the maintenance engine is authoritative (actually deducts resources), but the formula must stay in sync.
- **Impact:** If maintenance formula changes, both files must be updated. Risk of display vs. actual divergence.
- **Recommendation:** Extract to a shared utility function (e.g., `calculate_maintenance_cost(design_data, rate=0.05)`) in a common module, then both engines call it.
- **Effort:** Small (extract function, update 2 callers)

---

## Phase 2: Compatibility Shims & Wrappers

### LSH-004: Backward compatibility O(n) fallback in `_get_fleet_by_id()`

- **ID:** LSH-004
- **Severity:** MAJOR
- **Location:** `game/strategy/engine/game_session.py` lines 208-232
- **Issue:** `GameSession._get_fleet_by_id()` first attempts O(1) lookup via `galaxy.get_fleet_by_id()`, then falls back to O(n) iteration over all empires' fleets. The comment explicitly states: "for backward compatibility with tests that don't register fleets with the galaxy." This is a backward-compatibility shim for test code that doesn't use the proper registration path.
- **Impact:** Tests that rely on this fallback mask registration bugs. The O(n) path is a performance concern at scale (though negligible currently). Per CLAUDE.md policy: "When a new system replaces an old one, ERADICATE the old system completely."
- **Recommendation:** Fix the test(s) that don't register fleets properly, then remove the O(n) fallback entirely.
- **Effort:** Medium (identify and fix affected tests, remove fallback)

### LSH-005: Legacy fleet removal in `process_colonize()` when no registry

- **ID:** LSH-005
- **Severity:** MAJOR
- **Location:** `game/strategy/engine/fleet_order_processor.py` lines 228-232
- **Issue:** `process_colonize()` has a branch: when `component_registry is None`, it removes the entire fleet (comment: "Legacy behavior: remove entire fleet"). With a registry, it properly identifies and removes only the colony ship. The None-registry path is a compatibility shim for code paths that don't inject the registry.
- **Impact:** Any caller that passes `component_registry=None` gets incorrect game behavior (whole fleet removed instead of single ship). Per project policy, old systems should be eradicated.
- **Recommendation:** Make `component_registry` required (non-optional). Update all callers to always provide it. Remove the legacy branch.
- **Effort:** Medium (audit callers, make parameter required, update tests)

### LSH-006: `project_path_as_dicts()` backward compatibility wrapper

- **ID:** LSH-006
- **Severity:** MINOR
- **Location:** `game/strategy/services/fleet_navigation_service.py` line 403
- **Issue:** `project_path_as_dicts()` is described in its docstring as "for backward compatibility." It wraps `project_path()` and converts the output to a list of dicts. The method is actively used by `pathfinding.py:project_fleet_path()` (line 273) and has tests. This was deferred from cleanup in both PROJ-15 and PROJ-35.
- **Impact:** Minimal performance impact. The dict format may be needed by UI consumers. This is a known deferred cleanup item.
- **Recommendation:** Evaluate whether callers can be updated to use `project_path()` directly. If the dict format is genuinely needed by UI, rename the method to remove the "backward compatibility" framing and document it as the canonical dict-format API.
- **Effort:** Small (evaluate callers, rename or remove)

### LSH-007: `PlayerConfig.to_dict()` backward compatibility conditional

- **ID:** LSH-007
- **Severity:** MINOR
- **Location:** `game/strategy/engine/game_config.py` line 78
- **Issue:** Comment says "Only include race fields if set (backwards compatibility)" in the `to_dict()` serialization. This conditionally omits `race_config`, `flag_id`, `portrait_id` fields when they are falsy. Per project policy, save files are disposable and don't need migration.
- **Impact:** Minimal. The conditional serialization is overly cautious but doesn't cause bugs.
- **Recommendation:** Remove the conditional; always serialize all fields. Old saves are rejected by strict version checking already.
- **Effort:** Trivial

### LSH-008: `Planet.from_dict()` backward compatibility for populations

- **ID:** LSH-008
- **Severity:** MINOR
- **Location:** `game/strategy/data/planet.py` line 355
- **Issue:** Comment says "Deserialize populations (default empty for backward compat)." The `from_dict()` method defaults `populations` to an empty list when the key is absent from serialized data. Since `SaveGameService` uses strict version checking (v2.0.0 only), old saves are rejected entirely, making this default unnecessary.
- **Impact:** Negligible. The default is harmless but misleading about why it exists.
- **Recommendation:** Remove the "backward compat" comment. Keep the default empty list as defensive coding (not backward compatibility).
- **Effort:** Trivial (change comment only)

---

## Phase 3: Obsolete Patterns

### LSH-009: Duplicate `to_roman()` function in naming.py vs planet_naming.py

- **ID:** LSH-009
- **Severity:** MAJOR
- **Location:** `game/strategy/data/naming.py` line 54 (as `NameRegistry.to_roman()`) AND `game/strategy/data/planet_naming.py` line 19 (as standalone `to_roman()`)
- **Issue:** Two independent implementations of Roman numeral conversion exist. `NameRegistry.to_roman()` handles 1-3999 range using the traditional subtractive approach, while `planet_naming.to_roman()` handles 1-39 range with a more compact implementation. The `NameRegistry.to_roman()` is only called from tests (test_naming.py), while `planet_naming.to_roman()` is the one used in production by `assign_body_names()`. The NameRegistry version is effectively dead production code.
- **Impact:** Two implementations that could diverge. Confusion about which is authoritative. The NameRegistry version serves no production purpose.
- **Recommendation:** Remove `NameRegistry.to_roman()`. If any callers need the extended range (1-3999), have them call `planet_naming.to_roman()` (possibly extended to handle the full range).
- **Effort:** Small (remove method, update test imports)

### LSH-010: Design-thinking comments in `find_path_interstellar()`

- **ID:** LSH-010
- **Severity:** MINOR
- **Location:** `game/strategy/data/pathfinding.py` lines 51-63
- **Issue:** The `find_path_interstellar()` function contains stream-of-consciousness development notes left in the code as comments: "Wait, galaxy.systems is keyed by location. We need a name lookup or pass the object map differently. Let's assume we can get system object." and "Optimization: Build name_to_system cache or linear search?" These read like design thinking/scratch notes rather than documentation.
- **Impact:** Code readability. These comments describe uncertainty rather than explain the chosen approach.
- **Recommendation:** Replace with concise comments explaining the actual approach taken. Remove the deliberation text.
- **Effort:** Trivial

### LSH-011: Two layer format handling in multiple engine files

- **ID:** LSH-011
- **Severity:** MINOR
- **Location:** `game/strategy/engine/maintenance_engine.py` line 207-211, `game/strategy/engine/empire_economy_calculator.py` line 274-280, `game/strategy/data/design_metadata.py` lines 174, 218
- **Issue:** Multiple files handle two different layer formats in `design_data`: (1) Dict format `{"CORE": {"components": [...]}}` and (2) List format `{"HULL": [{...}]}`. The dict format is flagged as "Old layer format" in design_metadata.py. If the old dict format is truly obsolete, this dual handling should be unified.
- **Impact:** Every new engine that processes design_data must remember to handle both formats. Increases code complexity.
- **Recommendation:** Determine if the dict format is still produced anywhere. If not, remove the dict-format handling branches and add a migration step or validation that rejects the old format.
- **Effort:** Medium (audit all design_data producers, remove old format support if safe)

---

## Phase 4: Orphaned Resources

### LSH-012: Module-level mutable caches without invalidation

- **ID:** LSH-012
- **Severity:** MINOR
- **Location:** `game/strategy/data/homeworld_presets.py` line 16 (`_presets_cache`) AND `game/strategy/data/build_queue_source.py` line 24 (`_production_rates_cache`)
- **Issue:** Both modules use module-level mutable caches (`_presets_cache`, `_production_rates_cache`) that persist for the entire process lifetime. `homeworld_presets.py` has a `clear_cache()` function (line 131) for test cleanup, but `build_queue_source.py` has no cache invalidation mechanism. These are global mutable state that can leak between test runs.
- **Impact:** Test isolation issues. Cache can serve stale data if JSON files change during development. Not a "legacy" issue but a pattern that conflicts with DI-first architecture.
- **Recommendation:** For `build_queue_source.py`, add a `clear_cache()` function (matching `homeworld_presets.py` pattern). Long-term, consider injecting these as dependencies rather than using module-level caches.
- **Effort:** Trivial (add clear_cache), Small (convert to DI)

### LSH-013: Unused `experience` field on `ShipInstance`

- **ID:** LSH-013
- **Severity:** INFO
- **Location:** `game/strategy/data/ship_instance.py` line 64
- **Issue:** `ShipInstance` has an `experience: int = 0` field with the comment "For future crew/veteran system." This field is never read, written to, or serialized beyond its default value. It is a placeholder for a feature that doesn't exist yet.
- **Impact:** Minimal. One unused field.
- **Recommendation:** Keep if the crew/veteran system is planned for near-term development. Remove if the feature is indefinitely deferred to avoid YAGNI clutter.
- **Effort:** Trivial

### LSH-014: `sprite_preview` field on `DesignMetadata` is unused

- **ID:** LSH-014
- **Severity:** INFO
- **Location:** `game/strategy/data/design_metadata.py` line 35
- **Issue:** `DesignMetadata` has `sprite_preview: Optional[str] = None` with comment "Base64 encoded image (future)". This field is never populated or read.
- **Impact:** Minimal. One unused field.
- **Recommendation:** Same as LSH-013 - keep or remove based on feature roadmap.
- **Effort:** Trivial

---

## Phase 5: Incomplete Migrations

### LSH-015: `ShipInstance.to_ship()` transitional registries parameter

- **ID:** LSH-015
- **Severity:** MINOR
- **Location:** `game/strategy/data/ship_instance.py` line 499
- **Issue:** The `to_ship()` method has a comment: "registries: Optional GameRegistries for DI. If None, uses global fallback (transitional - will be required in Phase 6)." This indicates the method was supposed to make `registries` mandatory in a later phase, but that migration is incomplete. The global fallback remains.
- **Impact:** Code path using global state instead of DI. Violates the DI-first pattern established elsewhere.
- **Recommendation:** Complete the migration: make `registries` required (non-optional), update all callers to pass it explicitly, remove the global fallback.
- **Effort:** Medium (audit all callers of `to_ship()`, update them)

### LSH-016: `PopulationEngine._get_race_config()` single-species fallback

- **ID:** LSH-016
- **Severity:** INFO
- **Location:** `game/strategy/engine/population_engine.py` lines 122-151
- **Issue:** `_get_race_config()` always returns the empire's own `race_config` as a fallback, even when `race_id` doesn't match. Comment says "Future: look up in multi-species registry." This means all alien species on a colony are treated as the empire's own species for growth calculations.
- **Impact:** Incorrect population growth for multi-species colonies (not yet a gameplay scenario). The fallback masks what should be a "species not found" case.
- **Recommendation:** When multi-species is implemented, replace the fallback with proper registry lookup. For now, document the limitation clearly.
- **Effort:** Deferred (depends on multi-species feature)

### LSH-017: `EmpireEconomyCalculator` placeholder production sources

- **ID:** LSH-017
- **Severity:** INFO
- **Location:** `game/strategy/engine/empire_economy_calculator.py` lines 83-88, 96-98
- **Issue:** Five production source categories (`ship_production`, `trade_production`, `tribute_production`, `mining_production`) and two expense categories (`tribute_expenses`, `construction_expenses`) are initialized to zero dicts with comments "Placeholder production sources (future implementation)". The snapshot dataclass defines all these fields, but they're never populated.
- **Impact:** UI will show zero for these categories. The dataclass fields and zero-initialization are dead code paths that add complexity.
- **Recommendation:** Remove the placeholder fields from `EmpireEconomySnapshot` and the zero-initialization code. Add them back when the features are actually implemented (YAGNI principle).
- **Effort:** Small (remove fields and initialization code)

### LSH-018: Production engine "legacy items without cost tracking"

- **ID:** LSH-018
- **Severity:** MINOR
- **Location:** `game/strategy/engine/production_engine.py` lines 96, 154, 220
- **Issue:** The production engine has three references to "legacy items without cost tracking": items in the construction queue that lack `cost_per_tick` or `total_cost` fields. At line 154, these items are skipped for resource consumption. At line 220, they fall back to "old behavior" (completing after turns_remaining reaches zero without any resource check). This is a compatibility shim for queue items created before the PROJ-75 resource consumption system.
- **Impact:** Any queue item without cost tracking gets built for free (no resource consumption). This could mask bugs where new queue items fail to include cost data.
- **Recommendation:** Audit all code paths that create construction queue items to ensure they include cost tracking. Once confirmed, remove the legacy skip/fallback branches.
- **Effort:** Medium (audit queue item creation, remove legacy branches)

### LSH-019: `fleet_order_processor.py` species tracking TODO

- **ID:** LSH-019
- **Severity:** INFO
- **Location:** `game/strategy/engine/fleet_order_processor.py` line 350
- **Issue:** TODO comment: "If we ever track species in fleet cargo, use species_id here." Currently `process_transfer()` uses "Legacy/Default: use first species" logic when unloading passengers without species tracking.
- **Impact:** Multi-species passenger transfer not supported. The TODO indicates a known limitation.
- **Recommendation:** Implement species-aware cargo tracking when multi-species gameplay is developed.
- **Effort:** Deferred

---

## Cross-Cutting Observations

### Patterns Not Found (Clean Areas)

The following areas were scanned and found to be clean of legacy holdovers:

1. **Facade layer** (`game/strategy/facade/`): Clean CQRS-lite pattern with immutable DTOs. No legacy code.
2. **Interface layer** (`game/strategy/interfaces/`): Clean ABC contracts with proper DI support.
3. **Events system** (`game/strategy/events/`): Clean, modern implementation.
4. **Validation layer** (`game/strategy/validation/`): Well-structured validators with clear error codes.
5. **Generation layer** (`game/strategy/generation/`): Clean strategy pattern with density maps and loaders.
6. **Systems layer** (`game/strategy/systems/`): `DesignLibrary`, `RaceLibrary`, `SaveGameService` are all modern with strict version checking.
7. **Formulas** (`game/strategy/formulas/`): Pure functions with no dependencies on old patterns.
8. **Adapters** (`game/strategy/adapters/`): Clean bridge between strategy and simulation layers.

### Architecture Health

The strategy layer is in good overall health. The major decomposition work (PROJ-86/87/88/89) has been successful:
- Facade/delegate pattern is consistently applied
- DI is used throughout (though with some transitional fallbacks noted above)
- Interfaces are well-defined for all sub-engines
- Save format uses strict versioning (rejects old saves)

The findings are predominantly MINOR/INFO severity, with the MAJOR items being code duplication and backward-compatibility shims that should be cleaned up to prevent maintenance burden.
