# Phase 4: Migrate `ship_design_stats.py` (4 sites)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-276 4`

**Status:** Complete
**Objective:** Small migration — 4 sites. Mirror the Phase 2 pattern.

---

## Tasks

### Task 4.1: Audit the 4 sites [Simple]
**File:** `game/simulation/entities/ship_design_stats.py`
**Tests:** N/A

- [x] Per Phase 1 audit: 4 sites total — 2 DEFs (L19 param, L31 docstring, L103 helper def) + 2 READs (L58 condition, L60 `_lookup_damage` call)
- [x] All READs — design stats are computed, not mutated
- [x] Aggregation: applies `component_damage` dict to each Ship component's current_hp BEFORE `ship.recalculate_stats()`

**Notes:** Only one production caller actually passes `component_damage`: `ship_instance.py::get_calculated_stats`. The `production_spawner.py` caller doesn't pass damage. All other callers are tests.

### Task 4.2: Migrate per-site [Medium]
**File:** `game/simulation/entities/ship_design_stats.py`
**Tests:** `pytest tests/unit/simulation/systems/test_ship_design_stats.py -v`

- [x] Wrote TDD-red tests first: (a) `test_damage_does_not_affect_mass` using new `components=` kwarg and (b) `test_per_instance_damage_applied_via_component_state` observing warp_max_tonnage; (c) `test_missing_component_state_entry_leaves_hp_unchanged`
- [x] Renamed parameter `component_damage: Optional[Dict[str, int]]` → `components: Optional[Dict[str, ComponentState]]`
- [x] Deleted `_lookup_damage` helper (the fuzzy prefix matcher is no longer needed — canonical key format is `{comp_id}#{idx}`)
- [x] Replaced damage-application loop with per-id index iteration over `ship.iter_components()` matching `component_state_key(comp.id, idx)`
- [x] Updated `game/strategy/data/ship_instance.py:347` caller to pass `components=self.components` instead of `self.component_damage`
- [x] All 24 design_stats tests pass; incremental regression suite clean (only pre-existing unrelated failures)

**Notes:** The fuzzy `comp_id_N` prefix-match fallback is gone — `ComponentState` keys are always `{comp_id}#{idx}`. Legacy saves without `components` gracefully get full-HP defaults (via `_build_full_hp_components_from_design` which already runs on `ShipInstance.create`).

### Task 4.3: Verify integration [Simple]
**File:** N/A
**Tests:** `pytest tests/unit/simulation/systems/test_ship_design_stats.py tests/integration/ -n 12`

- [x] `grep "component_damage" game/simulation/entities/ship_design_stats.py` returns ZERO hits
- [x] `grep "calculate_design_stats.*component_damage"` returns ZERO hits — no call sites pass the old kwarg
- [x] Incremental regression suite: 267 passed + pre-existing unrelated failures only

**Notes:**

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update plan.md
- [x] Run `python Projects/scripts/validate_phase.py PROJ-276 4`
