# PROJ-382 Phase 5 — LOC Ceiling Split Review

**Reviewer:** OpenCode (agent_loc_splits_report)
**Date:** 2026-05-08
**Scope:** Phase 5 file decompositions + deferred Task 5.4

---

## Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 0     |
| MAJOR    | 2     |
| MINOR    | 3     |
| INFO     | 5     |
| **Total**| **10** |

---

## 1. planetary.py → planetary/ Package Decomposition

### FINDING-01: INFO — Re-export `__init__.py` is 59 LOC (above Pattern #36 ~30 LOC guideline but proportionate)

**File:** `game/simulation/components/abilities/planetary/__init__.py:1-59`
**Evidence:** 59-line re-export list containing 18 abilities across 6 `from .X import (...)` blocks plus `__all__`. Pattern #36 states re-export shims should be "small (≤ ~30 LOC)".
**Assessment:** The sub-module boundaries are semantically meaningful (shields, stabilizers, resource/economy, stat modifiers, terraforming, environmental — each a coherent grouping of 2-4 abilities). The 59 lines are driven by 18 distinct ability exports, not by padding. The Pattern #36 "When NOT to use" clause warns against "a permanent two-path import surface" — this is not the case here; the decomposition IS genuine. The 30 LOC guideline is for simpler shims (1-3 re-exports); 59 lines for 18 names is proportionate.

Also verified: `planetary.py` no longer exists (glob confirmed empty), so the package `planetary/__init__.py` is the sole resolution target for `from .planetary import X`. All legacy import paths continue to work.

**Recommendation:** Accept as-is. The shim is recognized as temporary under Pattern #36 and is pinned to PROJ-382. Future retirement should align with migration tracked in the project body.

---

### FINDING-02: MAJOR — Dead duplicate `_STORM_SCOPES` in `shields.py`

**File:** `game/simulation/components/abilities/planetary/shields.py:139-144`
**Evidence:**
```python
_STORM_SCOPES = [
    AbilityScope.SELF, AbilityScope.SECTOR, AbilityScope.ALLIED_SECTOR,
    AbilityScope.PLAYER_SECTOR, AbilityScope.ENEMY_SECTOR,
    AbilityScope.SYSTEM, AbilityScope.ALLIED_SYSTEM,
    AbilityScope.PLAYER_SYSTEM, AbilityScope.ENEMY_SYSTEM,
]
```
Neither `PlanetaryShieldAbility` nor `RadiationShieldAbility` reference `_STORM_SCOPES`. The canonical copy lives in `_shared.py:12-17` and is correctly imported by `stat_modifiers.py:13` and `environmental.py:13`. The `shields.py` copy is an untreated split artifact from the original 913-LOC `planetary.py` where all constants lived in the same file.
**Assessment:** Dead code at module level. Could confuse a future maintainer who sees `_STORM_SCOPES` in `shields.py` and assumes it's used locally or that it's the canonical definition. Also inflates the module's LOC by 6 lines for no reason.
**Recommendation:** Delete lines 139-144 from `shields.py`.

---

### FINDING-03: MINOR — Dead UI color imports in 6 planetary sub-modules

**File:** `game/simulation/components/abilities/planetary/shields.py:13-16`, `stabilizers.py:13-16`, `resource_modifiers.py:13-16`, `stat_modifiers.py:14-17`, `terraforming.py:13-16`, `environmental.py:14-17`
**Evidence:** Every sub-module imports the full tuple `(HINT_ACCURACY, HINT_DEFAULT, HINT_WARP_ENERGY, HINT_COLONIZE, HINT_SHIELD_CAP, HINT_DAMAGE)` from `..ui_colors`, but each sub-module only uses a subset:
- `shields.py`: uses HINT_WARP_ENERGY, HINT_DEFAULT, HINT_SHIELD_CAP — **HINT_ACCURACY, HINT_DAMAGE unused**
- `stabilizers.py`: uses HINT_WARP_ENERGY, HINT_SHIELD_CAP, HINT_DEFAULT — **HINT_ACCURACY, HINT_COLONIZE, HINT_DAMAGE unused**
- `resource_modifiers.py`: uses HINT_COLONIZE, HINT_ACCURACY, HINT_SHIELD_CAP — **HINT_DEFAULT, HINT_WARP_ENERGY, HINT_DAMAGE unused**
- `stat_modifiers.py`: uses HINT_SHIELD_CAP, HINT_DAMAGE, HINT_WARP_ENERGY, HINT_DEFAULT — **HINT_ACCURACY, HINT_COLONIZE unused**
- `terraforming.py`: uses HINT_COLONIZE, HINT_ACCURACY, HINT_WARP_ENERGY, HINT_DEFAULT — **HINT_SHIELD_CAP, HINT_DAMAGE unused**
- `environmental.py`: uses HINT_DAMAGE, HINT_DEFAULT, HINT_WARP_ENERGY — **HINT_ACCURACY, HINT_COLONIZE, HINT_SHIELD_CAP unused**
**Assessment:** Copy-pasted import blocks from the original monolithic `planetary.py` where all constants were needed. Each sub-module now has 2-3 unused imports. Low impact but violates clean-code practice and inflates diff surfaces on re-imports.
**Recommendation:** Trim each sub-module's UI color import to only the constants it actually uses.

---

### FINDING-04: INFO — `03_CONVENTIONS.md` references stale `planetary.py` path

**File:** `docs/03_CONVENTIONS.md:71`
**Evidence:** Line 71 reads: `planetary.py: PlanetaryShieldAbility, StrategicResourceGenerationAbility.` — but `planetary.py` is now the `planetary/` package.
**Assessment:** Documentation drift. The import path works identically (`from ...planetary import X` resolves through `__init__.py`), but the convention listing should reflect the package structure. This is a doc-audit item.
**Recommendation:** Update line 71 to reference the package: `planetary/: PlanetaryShieldAbility, StrategicResourceGenerationAbility, ...`.

---

## 2. battle_engine.py Split

### FINDING-05: INFO — battle_engine.py decomposition is clean and cohesive

**File:** `game/simulation/systems/battle_engine.py` (493 LOC), `battle_logger.py` (84 LOC), `boundary_enforcement.py` (122 LOC), `attack_processor.py` (97 LOC), `battle_setup.py` (141 LOC)
**Evidence:**
- `battle_logger.py` — one class, one responsibility (toggleable file-based event recorder)
- `boundary_enforcement.py` — three free functions for per-tick boundary check + ExitPolicy dispatch (NONE/DESTROY/RETREAT/BOUNCE)
- `attack_processor.py` — four free functions for attack collection + dispatch (projectile/beam/launch)
- `battle_setup.py` — three free functions for start-of-battle state assembly (start_teams, initialize_start_state, log_initial_status)

All helpers use the clean `engine`-as-explicit-first-parameter pattern with TYPE_CHECKING import guards for `BattleEngine`. The main `battle_engine.py` delegates via thin wrapper methods (1-2 lines each). No circular dependencies at runtime.

LOC verified: 493 (under 500, claim confirmed).

**Assessment:** Model extraction following Pattern #5 (Facade/Delegate). Each sub-module extracts a genuine, single-responsibility chunk. This is the gold standard for how LOC splits should be done.
**Recommendation:** None.

---

## 3. fleet_navigation_service.py Split

### FINDING-06: INFO — fleet_navigation_service.py decomposition is clean and cohesive

**File:** `game/strategy/services/fleet_navigation_service.py` (495 LOC), `fleet_path_projection.py` (202 LOC), `fleet_warp_resolution.py` (96 LOC)
**Evidence:**
- `fleet_path_projection.py` — multi-turn UI projection loop, tick consumption, and action-order projection. Genuine standalone responsibility.
- `fleet_warp_resolution.py` — warp-path resolution: composing path-to-WP + reciprocal exit lookup. Genuine standalone responsibility.

The main service delegates via thin wrappers. `fleet_path_projection.py` uses a deferred import (`from ... import NavigationState, PathSegment` inside `project_path_inner`) to avoid circular module-load dependencies — acceptable.

LOC verified: 495 (under 500, claim confirmed).

**Assessment:** Good decomposition. Both extractions are semantically cohesive.
**Recommendation:** None.

---

## 4. conflict_resolution_engine.py Split

### FINDING-07: INFO — conflict_resolution_engine.py decomposition is clean and cohesive

**File:** `game/strategy/engine/conflict_resolution_engine.py` (487 LOC), `conflict_modifier_collection.py` (93 LOC)
**Evidence:**
- `conflict_modifier_collection.py` — two functions: `lookup_environmental_effects` and `collect_team_modifiers`. Coherent responsibility: pre-battle modifier collection.

The main engine delegates via thin wrappers.

LOC verified: 487 (under 500).

**Assessment:** Clean extraction. One additional note: `conflict_modifier_collection.py:84` carries a broad `except Exception` with the required `# Intentional broad catch: ...` comment — properly annotated per conventions.
**Recommendation:** None.

---

## 5. Deferred Task 5.4: superweapon_order_processor.py

### FINDING-08: MAJOR — Deferral rationale for superweapon_order_processor.py is weak; a straightforward extraction path exists

**File:** `game/strategy/engine/superweapon_order_processor.py:1-723` (723 LOC, 223 over ceiling)
**Evidence:** The deferral rationale stated: "extracting closures requires a state-bag type or threading engine refs through every closure." However:

1. **The exact same pattern was successfully used** in `battle_setup.py`, `boundary_enforcement.py`, and `attack_processor.py` — all pass the engine/processor as an explicit first parameter rather than `self`. The closures in the 5 process methods (`process_implode_planet`, `process_stellerate_star`, `process_open_warp_point`, `process_close_warp_point`, `process_create_dyson_sphere`) capture `self` only to access `self._event_bus`, `self._get_empire_mutator()`, `self._check_blocking_stabilizer()`, and `self._finalize_superweapon()`. These can all be accessed via an explicit `processor` parameter — the closures already receive `self` implicitly and would simply receive it explicitly instead.

2. **The closures are not "over engine state"** — they close over `self` (the processor instance), which is a normal class reference. No special "state-bag type" is needed.

3. **Mechanical extraction path:**
   - Keep the central `execute_superweapon` dispatcher (lines 150-332, ~180 LOC) plus helper methods (`_finalize_superweapon`, `_get_empire_mutator`, `_check_blocking_stabilizer`, `_get_reference_planet`, `_stabilizer_target_label` — together ~120 LOC) in `superweapon_order_processor.py` (~350 LOC after tucking into one class).
   - Extract each of the 5 process methods into separate files under `game/strategy/engine/superweapon_handlers/` (one handler per superweapon type), following the `battle_setup.py` pattern. Each handler takes `processor` as a parameter and calls `processor.execute_superweapon(...)`.
   - Total LOC: main processor ~350, 5 handlers ~50-80 each.

4. **This is not a genuine architectural deferral** — it's a mechanical refactor following an already-proven pattern in the same PROJ cycle. The 723 LOC file has persisted over the ceiling through Phase 5.

**Assessment:** Remediation candidate, not a true architectural block. The file's structure (central dispatcher + 5 per-type methods) naturally decomposes into a coordinator + handler package. The closure-over-`self` argument does not withstand scrutiny when the same Phase 5 batch already extracted 12+ methods into free functions using the exact same explicit-parameter pattern.

**Recommendation:** Schedule extraction as a priority item in the next LOC sweep (PROJ-382 Phase 6 or equivalent). Follow the `battle_setup.py` / `attack_processor.py` pattern: free functions in handler modules that receive the `SuperweaponOrderProcessor` instance as an explicit parameter.

---

## 6. Minor Style / Drift Items

### FINDING-09: MINOR — Misplaced `logger` assignment between import blocks in `battle_engine.py`

**File:** `game/simulation/systems/battle_engine.py:59`
**Evidence:** Line 59 `logger = logging.getLogger(__name__)` sits between `from game.core.math import Vector2` (line 57) and `from game.engine.spatial import SpatialGrid` (line 60), breaking the three-block import grouping convention (`docs/03_CONVENTIONS.md:153-159`).
**Assessment:** Minor style issue — does not affect functionality but violates the documented import convention.
**Recommendation:** Move `logger = logging.getLogger(__name__)` after all `from` imports (after line 80), before the class definition.

---

### FINDING-10: MINOR — `_shared.py` naming implies shared utilities but only contains one constant

**File:** `game/simulation/components/abilities/planetary/_shared.py:1-17`
**Evidence:** The module is named `_shared.py` but contains only `_STORM_SCOPES`. The underscore prefix correctly marks it as internal.
**Assessment:** Minor naming concern — the name `_shared` could attract unrelated shared code in future, creating a kitchen-sink module. Not a bug.
**Recommendation:** If additional shared constants are needed, consider renaming to something more specific (e.g., `_storm_scopes.py` or `_constants.py`). Low priority.

---

## Verification Notes

- All 4 splits verified under 500 LOC ceiling: battle_engine.py (493), fleet_navigation_service.py (495), conflict_resolution_engine.py (487), planetary/ (largest sub-module is stat_modifiers.py at 233).
- `planetary.py` confirmed deleted — no name collision with `planetary/` package.
- All legacy imports `from game.simulation.components.abilities.planetary import X` resolve through `planetary/__init__.py`.
- No circular import issues found — all helper modules use TYPE_CHECKING guards for cross-references.
- `superweapon_order_processor.py` at 723 LOC is the sole remaining ceiling violation from the Phase 5 scope.
