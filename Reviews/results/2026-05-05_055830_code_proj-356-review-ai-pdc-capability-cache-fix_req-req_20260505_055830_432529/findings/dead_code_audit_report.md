# PROJ-356 Code Review: Cache Consumer Audit + Dead Code Hunter

> **Date:** 2026-05-05
> **Review scope:** PDC-related cache keys (`has_pdc`, `pdc_components`) and legacy `PDCAbility` references
> **Pre-computed verified:** `_eval_has_weapons_rule` reads only `has_weapons`. `_eval_pdc_arc_rule` does NOT read the cache. `is_in_pdc_arc` does its own component lookup. No consumer reads `has_pdc` or `pdc_components`.

---

## Summary

- **Total issues found:** 10
- **Critical:** 2, **Major:** 3, **Minor:** 3, **Info:** 2

---

## Findings

### CRITICAL: `has_pdc` and `pdc_components` cache keys computed but never read by any consumer

**ID:** DC-001
**Location:** Writer: `game/ai/controller.py:231,236-237` (lines 231, 236-237). No reader exists anywhere in production code.
**Issue:** `_build_capabilities_cache` iterates all weapon components per entity, filters for PDC weapons via `has_pdc_ability()`, and stores the results as `'has_pdc': bool` and `'pdc_components': List[Component]`. No code path reads these keys. The only cache consumers are:

- `_eval_has_weapons_rule` (`target_evaluator.py:184`) — reads only `'has_weapons'`
- `_eval_capability_rule` (`target_evaluator.py:241`) — dispatches to `_eval_pdc_arc_rule` without passing the cache at all

**Impact:** Wasted CPU in a hot path (called every targeting evaluation cycle, O(n) per entity). Additionally misleading for future developers — the presence of computed PDC data suggests PDC-aware targeting rules use it, which they don't.

**Recommendation:** Either (a) wire `_eval_pdc_arc_rule` to accept and use the cache (pass `ship_capabilities_cache` from `_eval_capability_rule` and read `pdc_components` instead of calling `is_in_pdc_arc` for the full component lookup), or (b) remove the PDC key computation from `_build_capabilities_cache` until a consumer exists.

**Effort:** Medium

---

### CRITICAL: `is_in_pdc_arc` imported but never used in `controller.py`

**ID:** DC-002
**Location:** `game/ai/controller.py:76`
**Issue:** `is_in_pdc_arc` is imported from `game.ai.combat_utils` on line 76 but is never referenced anywhere in the controller file (469 lines, confirmed by full-file grep). This is a dead import.
**Impact:** Unnecessary namespace pollution and maintenance overhead. Suggests the function was once called from the controller and removed without cleaning up the import.

**Recommendation:** Remove `is_in_pdc_arc` from the import tuple at line 76.

**Effort:** Simple

---

### MAJOR: `is_in_pdc_arc` does redundant full component lookups — cached PDC data sits unused

**ID:** DC-003
**Location:** `game/ai/combat_utils.py:214-222`, `game/ai/target_evaluator.py:218-238`
**Issue:** `_eval_pdc_arc_rule` (target_evaluator.py:218) receives only `stat_helpers` — it does NOT receive `ship_capabilities_cache`. When it calls `stat_helpers['is_in_pdc_arc'](ship, candidate)`, `is_in_pdc_arc` performs a full `get_components_by_ability('WeaponAbility')` call to retrieve ALL weapon components (combat_utils.py:214-222), then iterates and filters via `has_pdc_ability()` (line 233). Meanwhile, `controller._build_capabilities_cache` already computed the pre-filtered `pdc_components` list and `has_pdc` boolean — but `_eval_pdc_arc_rule` cannot see it.

**Impact:** Redundant O(n) component lookups in a hot path called per-target, per-tick during combat AI scoring. The `_build_capabilities_cache` docstring (controller.py:187-189) claims the cache converts "O(n*m) component lookups ... to O(n) lookups," but PDC arc rules are not covered by this optimization — they bypass the cache entirely.

**Recommendation:** Pass `ship_capabilities_cache` from `_eval_capability_rule` to `_eval_pdc_arc_rule`. Use `cache[candidate_id]['pdc_components']` for the component check in `_eval_pdc_arc_rule` (validating positions/arcs still required), or optionally extend `is_in_pdc_arc` to accept a pre-filtered component list instead of doing its own lookup.

**Effort:** Medium

---

### MAJOR: Misleading PERF comment in `_score_and_sort_enemies` claims PDC arc benefits from caching

**ID:** DC-004
**Location:** `game/ai/controller.py:272`
**Issue:** The comment reads:
```python
# PERF: Pre-compute capability checks once for all candidates
# Avoids redundant component lookups for has_weapons, pdc_arc rules
```
In reality, pdc_arc rules do NOT use the cache. Only `has_weapons` rules benefit.
**Impact:** This stale claim misleads maintainers into thinking `_eval_pdc_arc_rule` is cache-aware when it is not. The performance claim is false.

**Recommendation:** Remove `pdc_arc` from the comment line. Change to: `# Avoids redundant component lookups for has_weapons rules.`

**Effort:** Simple

---

### MAJOR: Stale docstring in `_eval_has_weapons_rule` references defunct try/except

**ID:** DC-005
**Location:** `game/ai/target_evaluator.py:174-176`
**Issue:** The docstring states:
```
Previously crashed in the cache-miss fallback; outer try/except silently dropped
the missile from scoring.
```
The outer try/except was removed in PROJ-272 Phase 3 when the code was refactored to use protocol checks (`is_combat_ship`, `is_projectile`) instead of try/except guards. There is no try/except wrapping target evaluation in the current code. The docstring describes historical behavior that no longer exists.
**Impact:** Developers reading this docstring may waste time searching for a try/except block that doesn't exist, or make decisions based on inaccurate assumptions about error handling.

**Recommendation:** Remove the 2-line historical note (lines 174-176 commented text). The docstring's first paragraph (lines 172-173) accurately describes current behavior.

**Effort:** Simple

---

### MINOR: `AbilityManager.has_pdc_ability_static` — dead code with zero callers

**ID:** DC-006
**Location:** `game/simulation/components/ability_manager.py:317-322`
**Issue:** Static method marked `DEPRECATED: Use instance has_pdc_ability() instead.` Confirmed zero callers anywhere in the codebase (production or tests) via full-tree grep. This is graveyard code that should have been deleted when PROJ-241 converted `AbilityManager` from a static namespace to a stateful delegate.

Fellow deprecated siblings in the same file also have zero production callers:
- `has_ability_static` (line 306) — has 1 test-only caller (`test_ability_manager.py:145`)
- `get_ability_static` (line 298) — zero callers
- `get_abilities_static` (line 291) — has 1 test-only caller (`test_ability_manager.py:137`)
- `get_ui_rows_static` (line 325) — has 1 test-only caller (`test_ability_manager.py:153`)
- `instantiate_abilities_static` (line 333) — zero callers

**Impact:** Violates `docs/03_CONVENTIONS.md` §6.6 System Migration Policy: "When a new system replaces an old one, **eradicate the old system completely**. No fallback paths, no backward compatibility layers." These 6 deprecated static methods have been retained for at least one PROJ cycle past their deprecation date. Dead code increases maintenance burden and confuses contributors about the canonical API.

**Recommendation:** Delete all 6 deprecated static methods. (Two test files reference `has_ability_static`, `get_abilities_static`, `get_ui_rows_static`; those tests should use instance methods instead.) Schedule as a separate cleanup PROJ to avoid scope creep on PROJ-356.

**Effort:** Medium (requires test updates to remove test-only callers)

---

### MINOR: `evaluate()` docstring documents unused cache keys as if they were active API

**ID:** DC-007
**Location:** `game/ai/target_evaluator.py:286-287`
**Issue:** The `evaluate()` method's docstring documents:
```
Structure: {ship_id: {'has_weapons': bool, 'weapon_components': List,
                       'has_pdc': bool, 'pdc_components': List}}
```
`has_pdc` and `pdc_components` have no consumer anywhere in the codebase. Documenting them in the primary API entry point implies they are actively read, which is inaccurate.
**Impact:** Developers reading the `evaluate()` API may build callers that depend on these keys being populated, only to find they're never consumed internally.
**Recommendation:** If these keys are intended as future-use markers, mark them explicitly: add `# Reserved: not yet consumed` or `# Future: planned for PDC arc cache optimization`. Otherwise, remove them from the docstring until a consumer exists.

**Effort:** Simple

---

### MINOR: `_build_capabilities_cache` docstring advertises unused keys symmetrically

**ID:** DC-008
**Location:** `game/ai/controller.py:204-211`
**Issue:** The `_build_capabilities_cache` docstring Returns section documents the same `has_pdc`/`pdc_components` keys with no consumer. This is the symmetric counterpart to DC-007 — the writer documents keys no reader reads.
**Impact:** Same as DC-007. Creates a false expectation that the full cache surface is actively consumed.
**Recommendation:** Same as DC-007 — label as reserved/future or remove until a consumer exists.

**Effort:** Simple

---

### INFO: No `PDCAbility` string references in production code — migration is clean

**ID:** DC-009
**Location:** N/A (confirmed absence)
**Issue:** Full-tree grep for `PDCAbility` across `game/` returned zero matches. The migration from class-named PDC (`PDCAbility` string check) to tag-based PDC (`has_pdc_ability()`) is clean at the production code level. No silent fallback to the legacy `has_ability('PDCAbility')` path exists in production code.
**Impact:** Positive finding. No cleanup required.
**Recommendation:** None.

---

### INFO: Test-only `PDCAbility` string in `test_controllable_adapter_edge_cases.py`

**ID:** DC-010
**Location:** `tests/unit/ai/test_controllable_adapter_edge_cases.py:231`
**Issue:** Test uses `'PDCAbility'` as a passthrough probe value to verify the adapter delegates `get_components_by_ability(name, ...)` to the underlying ship verbatim. The string `PDCAbility` is arbitrary — any ability class name would work. This is not a contract about controller PDC discovery.
**Impact:** Already documented in `PROJ-356/decisions.md` (2026-05-04 entry: "just a passthrough probe value, not a contract"). Not a production concern. However, a reference to a non-existent ability class name in a test file could confuse a future contributor who searches for `PDCAbility` without reading the surrounding context.
**Recommendation:** Leave as-is per existing project decision. (Decisions.md: "Renaming would obscure intent without improving coverage.")

---

## Compatibility Shim & Fallback Audit

Per the task's directive to look for compatibility shims, fallback paths, and backward-compatibility layers:

- **`game/ai/target_evaluator.py:9`** — Module docstring: "defensive programming with fallback behavior". This refers to the general pattern of logging errors and continuing (e.g., `safe_distance` wrapper), not a legacy-compatibility shim. Normal defensive pattern, not a concern.
- **`game/ai/target_evaluator.py:185-190`** — `_eval_has_weapons_rule` fallback. When the cache misses, it falls back to `candidate.get_components_by_ability('WeaponAbility')`. This is a legitimate cache-miss path, not a compatibility shim.
- **`game/ai/combat_utils.py:215-222`** — `is_in_pdc_arc` has two paths: one for `IControllable` (uses `.get_components_by_ability()` directly) and one for raw `Ship` objects (uses `getattr` with a `callable` guard). The `getattr` path is a runtime type-check workaround for a circular import constraint (cannot import `Ship` at module level in `combat_utils.py`). This is a structural workaround, not a compatibility shim.
- **No `PDCAbility` class or string references found in production code** — confirmed clean.
- **No `compat`, `backward_compat`, `graveyard`, or `shim` named code in `game/ai/`** — confirmed clean.

**Conclusion:** No backward-compatibility shims or legacy fallbacks were found related to PDC cache keys or `PDCAbility`.

---

## Top 5 Priority Issues

1. **DC-001 (CRITICAL):** `has_pdc`/`pdc_components` keys computed but never read — wasted CPU in hot path. Wire `_eval_pdc_arc_rule` to use the cache or remove the computation.
2. **DC-002 (CRITICAL):** `is_in_pdc_arc` unused import in `controller.py:76` — dead import, delete.
3. **DC-003 (MAJOR):** `is_in_pdc_arc` does redundant full component lookup — cached PDC data bypassed. Pass cache through to `_eval_pdc_arc_rule`.
4. **DC-004 (MAJOR):** Stale PERF comment at `controller.py:272` claims pdc_arc rules benefit from caching — they don't. Fix the comment.
5. **DC-005 (MAJOR):** Stale docstring in `_eval_has_weapons_rule` references defunct try/except — remove historical note.
