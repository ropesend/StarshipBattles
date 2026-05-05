# Phase 1: Failing Test + One-Line Fix

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-356 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** none
**Review Mode:** standard
**Files (planned):** game/ai/controller.py, tests/unit/ai/test_capability_cache_pdc.py, tests/unit/ai/test_controllable_adapter_edge_cases.py
**Objective:** Replace the dead `has_ability('PDCAbility')` filter in the AI capability cache with a tag-based `has_pdc_ability()` check. Lock in correct behavior with a regression test that fails on current main.

---

## Tasks

### Task 1.1: Audit consumers of `pdc_components` / `'has_pdc'` cache entries [Simple]
**File:** Read-only audit across `game/ai/` and `game/simulation/combat/`
**Tests:** None (research)

- [ ] Grep for `pdc_components` and `'has_pdc'` (and `"has_pdc"`) across `game/`
- [ ] List every consumer in [decisions.md](decisions.md) under a "Consumer audit" row
- [ ] For each consumer: note whether the silently-empty cache changes observable AI behavior today
- [ ] If a consumer was relying on `'has_pdc' == True` and getting `False`, surface to user before fixing — fixing the cache may flip targeting behavior

**Notes:**

---

### Task 1.2: Write failing regression test [Simple]
**File:** `tests/unit/ai/test_capability_cache_pdc.py` (new)
**Tests:** `pytest tests/unit/ai/test_capability_cache_pdc.py -v`

- [ ] Test 1: ship with a weapon component carrying a `pdc`-tagged ability appears in `cache[entity_id]['pdc_components']` and `'has_pdc'` is True
- [ ] Test 2: ship with a non-PDC `WeaponAbility` is in `weapon_components` but NOT in `pdc_components` and `'has_pdc'` is False
- [ ] Test 3: ship with no weapons does not appear in cache
- [ ] Run on current main — verify tests 1 and 2 FAIL (test 1's `pdc_components` is empty; test 2's `'has_pdc'` happens to pass but verify both tests are red on main first)
- [ ] Use the existing `is_combat_ship` / `get_capability_cache_key` plumbing; mirror fixture style from `test_controllable_adapter_edge_cases.py`

**Notes:**

---

### Task 1.3: Apply one-line fix [Simple]
**File:** `game/ai/controller.py:229`
**Tests:** `pytest tests/unit/ai/test_capability_cache_pdc.py -v`

- [ ] Replace `pdc_weapons = [w for w in weapons if w.has_ability('PDCAbility')]` with `pdc_weapons = [w for w in weapons if w.has_pdc_ability()]`
- [ ] Verify regression tests now PASS
- [ ] No other edits to `_build_capabilities_cache`

**Notes:**

---

### Task 1.4: Update existing fixture assertion [Simple]
**File:** `tests/unit/ai/test_controllable_adapter_edge_cases.py:231`
**Tests:** `pytest tests/unit/ai/test_controllable_adapter_edge_cases.py -v`

- [ ] Read lines 231 and 233 — these assert that `get_components_by_ability('PDCAbility', operational_only=False)` is the call shape
- [ ] If the test is asserting the *adapter* delegates correctly, leave it (delegation contract unchanged); if it's verifying the controller's PDC discovery path, rewrite to assert `has_pdc_ability()` is consulted
- [ ] Document the choice in [decisions.md](decisions.md)

**Notes:**

---

### Task 1.5: Sharded suite green [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run full sharded suite
- [ ] No regressions; new regression test is included in the count
- [ ] If a test now fails because the cache started returning the right answer, treat that as a real bug surfaced by the fix — investigate before weakening any test

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to closure / awaiting user verification
- [ ] Update [manifest.md](manifest.md) if files outside the planned set were touched
