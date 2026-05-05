# Phase 1: Schema fields + extractor + serializer

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-354A 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add `max_hp` and `status` to `ComponentStateSpec`, populate them in the extractor, round-trip them in the serializer, bump the schema version.

See `plan.md` Phase 1 for full task details.

---

## Tasks

### Task 1.1: Write failing test for new fields (TDD) [Simple]
**File:** `tests/unit/simulation/replay/test_serialization.py`
**Tests:** `pytest tests/unit/simulation/replay/test_serialization.py -k component_state -v`

- [x] Add `test_component_state_spec_round_trip_includes_max_hp_and_status` (see plan.md Task 1.1)
- [x] Run; confirm fails with `TypeError: ComponentStateSpec.__init__() got unexpected keyword argument 'max_hp'`
- [x] Verify: test exists, fails for right reason

**Notes:**

### Task 1.2: Add `max_hp` and `status` fields to `ComponentStateSpec` [Simple]
**File:** `game/simulation/battle_spec.py`
**Tests:** `pytest tests/unit/simulation/test_battle_spec.py tests/unit/simulation/replay/test_serialization.py`

- [x] Extend dataclass at line 86-99 (see plan.md Task 1.2 for exact code)
- [x] Verify: Task 1.1 test passes alone

**Notes:**

### Task 1.3: Update serializer round-trip [Simple]
**File:** `game/simulation/replay/replay_serialization.py`
**Tests:** `pytest tests/unit/simulation/replay/test_serialization.py -v`

- [x] Update `_component_state_to_dict` at line 241-247 (add max_hp, status keys)
- [x] Update `_component_state_from_dict` at line 250-256 (read max_hp, status keys)
- [x] Verify: round-trip test passes end-to-end

**Notes:**

### Task 1.4: Update `_extract_component_states` [Medium]
**File:** `game/simulation/battle_runner.py`
**Tests:** `pytest tests/unit/simulation/test_battle_runner_component_hp.py -v`

- [x] Update extractor at line 622-643 to read `comp.max_hp` and `comp.status.name` (see plan.md Task 1.4 for exact code, including defensive `hasattr(status_obj, "name")`)
- [x] Verify: existing test fails as expected (Phase 2 fixes constructor calls)

**Notes:**

### Task 1.5: Bump `REPLAY_SCHEMA_VERSION` [Simple]
**File:** `game/simulation/replay/replay_serialization.py`
**Tests:** `pytest tests/unit/simulation/replay/test_serialization.py -k version -v`

- [x] Change `REPLAY_SCHEMA_VERSION` at line 70 from `"1.0.0"` to `"2.0.0"`
- [x] Search for hardcoded `"1.0.0"` strings in tests; update specific-version pins (NOT version-drift tests)
- [x] Verify: schema version pinned correctly

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
