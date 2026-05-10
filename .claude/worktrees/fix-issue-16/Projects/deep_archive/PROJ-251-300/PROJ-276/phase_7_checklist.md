# Phase 7: Update Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-276 7`

**Status:** Complete
**Objective:** All test files × `component_damage` occurrences migrated. Some are renames; some assert lossy behavior and need rewriting.

---

## Tasks

### Task 7.1: Audit test classifications [Simple]
**File:** `findings/component_damage_test_audit.md` (created Phase 1)
**Tests:** N/A

- [x] Re-read Phase 1's test audit
- [x] Classified: DELETE (4 empty-dict args), RENAME (1 field rename), REWRITE (11 per-instance), MODULE-SCOPE DELETE (strategy ship_stats/* — already gone in Phase 2)
- [x] No test asserted the lossy-flatten as a contract (Phase 1 audit confirmed)

**Notes:** Most test migrations happened inline during Phases 3, 5, and 6 since tests blocked testmon. Phase 7 cleaned up the stragglers.

### Task 7.2: Simple rename migrations [Medium]
**File:** Multiple (per audit)
**Tests:** `pytest tests/unit/strategy/ -n 12`

- [x] `tests/unit/strategy/test_ship_display_formatter.py:28` — changed `ship.component_damage = {}` → `ship.components = {}`
- [x] `tests/unit/strategy/test_fleet_capability_calculator_di.py:142` — removed stale `'component_damage': {}` dict key from save-data fixture
- [x] `tests/integration/resource_system/test_resource_pipeline.py:276` — removed `'component_damage': {'engine_0': 50}` from backward-compat test save (backward-compat test is about `component_toggles`, this field was incidental)
- [x] All 32 affected tests pass

**Notes:**

### Task 7.3: Lossy-assertion rewrites [Complex]
**File:** Multiple
**Tests:** `pytest tests/unit/strategy/ -n 12`

- [x] `tests/unit/strategy/test_ship_instance_damage.py` — two tests rewritten to seed `components` directly with `ComponentState` objects and assert per-instance damage (done during Phase 6)
- [x] `tests/unit/strategy/ship_instance/test_cost_queries.py` — `test_get_warp_resource_costs_damaged_warp_drive` migrated to construct `ComponentState` for the damaged warp drive (done during Phase 6)
- [x] `tests/unit/strategy/ship_instance/test_validation.py` — `test_optional_fields_have_defaults` asserts on `ship.components == {}` instead of `component_damage` (done during Phase 6)
- [x] No dedicated "lossy behavior" assertion existed — so no rewrite-to-new-behavior was needed
- [x] Multi-instance positive test was already added in Phase 3 (`test_per_instance_damage_only_targets_matching_instance`) and Phase 4 (`test_per_instance_damage_applied_via_component_state`)

**Notes:** Phase 1's audit finding ("no test asserts lossy behavior as a contract") held up — no behavioral tests needed deep rewrites.

### Task 7.4: Serializer tests [Medium]
**File:** `tests/unit/strategy/ship_instance/test_ship_instance_serializer.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/test_ship_instance_serializer.py -v`

- [x] 5 occurrences migrated (all in Phase 5):
  - Fixture `full_ship`: `component_damage={...}` → `components={ComponentState(...)}`
  - `test_round_trip_preserves_all_fields`: assertion updated to check `components` round-trip
  - `test_clone_preserves_data`: updated to check `components` equivalence
  - `test_clone_deep_copies_mutable_fields`: uses `components[new_key] = ComponentState(...)` to verify isolation
- [x] Two NEW tests added:
  - `test_to_dict_does_not_emit_legacy_component_damage_key` — proves the key is gone from saves
  - `test_from_dict_ignores_legacy_component_damage_key` — proves old saves load without crashing
- [x] All 12 serializer tests pass

**Notes:**

### Task 7.5: Roundtrip integration [Medium]
**File:** `tests/integration/save_load/test_roundtrip_ships.py`
**Tests:** `pytest tests/integration/save_load/test_roundtrip_ships.py -v`

- [x] `test_component_damage` replaced with `test_per_instance_component_state_round_trip` (done in Phase 5)
- [x] New test covers multi-instance case: `laser_1#0` at 5 HP + `laser_1#1` at 40 HP round-trips with per-instance HP intact
- [x] All 10 roundtrip tests pass

**Notes:**

### Task 7.6: Full suite final [Simple]
**File:** N/A
**Tests:** `pytest tests/unit/strategy/ tests/integration/strategy/ tests/integration/save_load/ tests/integration/fleet_combat/`

- [x] Targeted suites: 3462 passed, 2 skipped, 1 pre-existing unrelated ImportError
- [x] Grep `tests/ component_damage` returns ONLY migration artifacts (tests that assert the key is gone / explanatory comments)
- [x] Baseline expanded: added multi-instance positive tests at bridge, design-stats, and serializer layers

**Notes:** Zero tests now USE `component_damage` as a field or dict-key to drive production behavior.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update plan.md
- [x] Run `python Projects/scripts/validate_phase.py PROJ-276 7`
