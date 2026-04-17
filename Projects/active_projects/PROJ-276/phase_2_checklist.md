# Phase 2: Migrate `ship_stats_calculator.py` (TDD, 20 sites)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-276 2`

**Status:** Not Started
**Objective:** The biggest migration — 20 READ sites in the stat calculation hot path. Each site migrated with per-instance test coverage.

---

## Tasks

### Task 2.1: Parity test infrastructure [Medium]
**File:** `tests/unit/strategy/services/test_ship_stats_parity.py` (NEW)
**Tests:** `pytest tests/unit/strategy/services/test_ship_stats_parity.py -v`

- [ ] Write a parametrized test: for each ship in `tests/fixtures/strategy_entities.py`, compute stats two ways:
  - Legacy: via `component_damage` dict (pre-migration)
  - New: via `components` dict (post-migration)
- [ ] Assert IDENTICAL results for SINGLE-instance ships (the common case)
- [ ] Run — initially this test uses only one code path; after migration it compares the migrated code to a snapshot
- [ ] Use approach: pickle baseline stats for each fixture ship BEFORE migration starts (Phase 1 or early Phase 2)

**Notes:**

### Task 2.2: Multi-instance behavior test [Medium]
**File:** `tests/unit/strategy/services/test_ship_stats_multi_instance.py` (NEW)
**Tests:** `pytest tests/unit/strategy/services/test_ship_stats_multi_instance.py -v`

- [ ] Test: ship with 3 seeker missiles, damage applied to instance #2 only
- [ ] Legacy (pre-migration): flatten to `component_damage[seeker_id] = low_hp` — all 3 seekers report low HP
- [ ] New (post-migration): only `components["seeker#1"].current_hp` is low — seekers #0 and #2 are full HP
- [ ] The test ASSERTS the new behavior (will fail pre-migration, pass post-migration)
- [ ] Document this as the "expected behavior change" in notes

**Notes:**

### Task 2.3: Migrate READ sites 1-5 [Complex]
**File:** `game/strategy/services/ship_stats_calculator.py`
**Tests:** `pytest tests/unit/strategy/services/ -n 12`

- [ ] Per audit: sites 1-5 (by line number order)
- [ ] For each: identify the iteration context; use `components[component_state_key(component_id, instance_index)].current_hp` pattern
- [ ] Run parity test after each — must stay green for single-instance ships
- [ ] Run full strategy test suite after 5 sites

**Notes:**

### Task 2.4: Migrate READ sites 6-10 [Complex]
**File:** `game/strategy/services/ship_stats_calculator.py`
**Tests:** `pytest tests/unit/strategy/services/ -n 12`

- [ ] Same pattern
- [ ] Run parity and integration tests after

**Notes:**

### Task 2.5: Migrate READ sites 11-15 [Complex]
**File:** `game/strategy/services/ship_stats_calculator.py`
**Tests:** `pytest tests/unit/strategy/services/ -n 12`

- [ ] Same pattern
- [ ] Run parity and integration tests after

**Notes:**

### Task 2.6: Migrate READ sites 16-20 [Complex]
**File:** `game/strategy/services/ship_stats_calculator.py`
**Tests:** `pytest tests/unit/strategy/services/ -n 12`

- [ ] Same pattern
- [ ] After the last site: `grep -n "component_damage" game/strategy/services/ship_stats_calculator.py` returns ZERO
- [ ] Full strategy tests green

**Notes:**

### Task 2.7: Verify multi-instance test now passes [Simple]
**File:** `tests/unit/strategy/services/test_ship_stats_multi_instance.py`
**Tests:** `pytest tests/unit/strategy/services/test_ship_stats_multi_instance.py -v`

- [ ] Previously FAILING test now PASSES
- [ ] This is the behavioral win: multi-instance ships correctly represent partial damage

**Notes:**

### Task 2.8: Perf check [Simple]
**File:** N/A
**Tests:** `pytest tests/performance/ -n 1 -v`

- [ ] Run performance suite
- [ ] Compare stat-calc hot-path timing to previously-recorded baseline
- [ ] No regression >10% (lookups against `components` dict are O(1) same as `component_damage`)
- [ ] If regression detected, document in `findings/perf_regression.md` and optimize

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update plan.md
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-276 2`
