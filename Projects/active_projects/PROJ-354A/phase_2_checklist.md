# Phase 2: Tests + bridge verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-354A 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update all 5 existing test files for the new constructor signature; add new tests proving the new fields surface distinct values; verify the post-battle bridge to `ComponentState` still works.

See `plan.md` Phase 2 for full task details.

---

## Tasks

### Task 2.1: New TDD test — extractor produces distinct status values [Medium]
**File:** `tests/unit/simulation/test_battle_runner_component_hp.py` (extended) OR new `test_extract_component_states_status.py`
**Tests:** `pytest tests/unit/simulation/test_extract_component_states_status.py -v`

- [ ] Construct fake engine `Ship` with 3 components: `ACTIVE`/`DAMAGED`/`NO_AMMO`
- [ ] Call `_extract_component_states`; assert per-entry `status` strings match
- [ ] Assert JSON round-trip preserves all 3 statuses
- [ ] Verify: test passes after Phase 1

**Notes:**

### Task 2.2: Update existing test files for new constructor signature [Medium]
**Files (5):**
- `tests/unit/simulation/replay/test_serialization.py` (lines 131-134, 190 — 3 sites)
- `tests/unit/simulation/test_battle_spec.py` (lines 125-129)
- `tests/unit/simulation/test_battle_runner_component_hp.py` (lines 115-119)
- `tests/unit/simulation/test_battle_outcome.py` (multiple sites)
- `tests/unit/strategy/combat/test_post_battle_hook.py` (multiple sites)

**Tests:** `pytest tests/unit/simulation/replay/test_serialization.py tests/unit/simulation/test_battle_spec.py tests/unit/simulation/test_battle_runner_component_hp.py tests/unit/simulation/test_battle_outcome.py tests/unit/strategy/combat/test_post_battle_hook.py -v`

- [ ] For each file: find every `ComponentStateSpec(...)` and add `max_hp=` and `status=` (defaults `100.0`, `"ACTIVE"` for tests that don't care; specific values for tests that do)
- [ ] Run each file individually; confirm green
- [ ] Verify: all 5 files together green

**Notes:**

### Task 2.3: Verify post-battle hook bridge still works [Simple]
**File:** `game/strategy/combat/post_battle_hook.py` (read-only verification)
**Tests:** `pytest tests/unit/strategy/combat/test_post_battle_hook.py -v`

- [ ] Read `_apply_survivor_outcome` at lines 150-158; confirm named-field reads, not positional
- [ ] Run test file post-Task-2.2; should be green
- [ ] Verify: bridge ignores new fields gracefully — no code change needed

**Notes:**

### Task 2.4: Schema version regression test [Simple]
**File:** `tests/unit/simulation/replay/test_serialization.py`
**Tests:** `pytest tests/unit/simulation/replay/test_serialization.py -k schema_version -v`

- [ ] Add `test_replay_schema_version_is_2_0_0` asserting `REPLAY_SCHEMA_VERSION == "2.0.0"`
- [ ] Verify: passes

**Notes:**

### Task 2.5: Full sharded suite green [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run full sharded suite; compare to baseline (17256 passed + new tests)
- [ ] Acceptance: same pass count as baseline + new tests; zero regressions
- [ ] Investigate and fix any failures before Phase 3

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
