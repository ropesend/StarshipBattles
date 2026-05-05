# Phase 2: Tests + bridge verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-354A 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update all 5 existing test files for the new constructor signature; add new tests proving the new fields surface distinct values; verify the post-battle bridge to `ComponentState` still works.

See `plan.md` Phase 2 for full task details.

---

## Tasks

### Task 2.1: New TDD test — extractor produces distinct status values [Medium]
**File:** `tests/unit/simulation/test_battle_runner_component_hp.py` (extended) OR new `test_extract_component_states_status.py`
**Tests:** `pytest tests/unit/simulation/test_extract_component_states_status.py -v`

- [x] Construct fake engine `Ship` with 3 components: `ACTIVE`/`DAMAGED`/`NO_AMMO`
- [x] Call `_extract_component_states`; assert per-entry `status` strings match
- [x] Assert JSON round-trip preserves all 3 statuses
- [x] Verify: test passes after Phase 1

**Notes:**

### Task 2.2: Update existing test files for new constructor signature [Medium]
**Files (5):**
- `tests/unit/simulation/replay/test_serialization.py` (lines 131-134, 190 — 3 sites)
- `tests/unit/simulation/test_battle_spec.py` (lines 125-129)
- `tests/unit/simulation/test_battle_runner_component_hp.py` (lines 115-119)
- `tests/unit/simulation/test_battle_outcome.py` (multiple sites)
- `tests/unit/strategy/combat/test_post_battle_hook.py` (multiple sites)

**Tests:** `pytest tests/unit/simulation/replay/test_serialization.py tests/unit/simulation/test_battle_spec.py tests/unit/simulation/test_battle_runner_component_hp.py tests/unit/simulation/test_battle_outcome.py tests/unit/strategy/combat/test_post_battle_hook.py -v`

- [x] For each file: find every `ComponentStateSpec(...)` and add `max_hp=` and `status=` (defaults `100.0`, `"ACTIVE"` for tests that don't care; specific values for tests that do)
- [x] Run each file individually; confirm green
- [x] Verify: all 5 files together green

**Notes:**

### Task 2.3: Verify post-battle hook bridge still works [Simple]
**File:** `game/strategy/combat/post_battle_hook.py` (read-only verification)
**Tests:** `pytest tests/unit/strategy/combat/test_post_battle_hook.py -v`

- [x] Read `_apply_survivor_outcome` at lines 150-158; confirm named-field reads, not positional
- [x] Run test file post-Task-2.2; should be green
- [x] Verify: bridge ignores new fields gracefully — no code change needed

**Notes:**

### Task 2.4: Schema version regression test [Simple]
**File:** `tests/unit/simulation/replay/test_serialization.py`
**Tests:** `pytest tests/unit/simulation/replay/test_serialization.py -k schema_version -v`

- [x] Add `test_replay_schema_version_is_2_0_0` asserting `REPLAY_SCHEMA_VERSION == "2.0.0"`
- [x] Verify: passes

**Notes:**

### Task 2.5: Full sharded suite green [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Run full sharded suite; compare to baseline (17256 passed + new tests)
- [x] Acceptance: same pass count as baseline + new tests; zero regressions
- [x] Investigate and fix any failures before Phase 3

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
