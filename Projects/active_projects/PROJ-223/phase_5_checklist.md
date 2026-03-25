# Phase 5: Full GameSession Round-Trip

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-223 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** End-to-end verification with richly-populated game state through SaveGameService.

---

## Tasks

### Task 5.1: Comprehensive GameSession round-trip [Complex]
**File:** `tests/integration/save_load/test_full_roundtrip.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_full_roundtrip.py`

- [ ] Create richly-populated game state with diverse content
- [ ] Save via SaveGameService.save_game()
- [ ] Load via SaveGameService.load_game()
- [ ] Deep-compare all fields across entire game state tree
- [ ] Verify process_turn() works after load
- [ ] Verify re-save succeeds and matches

**Notes:** Ultimate integration test.

### Task 5.2: Multi-cycle save/load/play test [Medium]
**File:** `tests/integration/save_load/test_full_roundtrip.py` (extend)
**Tests:** `pytest tests/integration/save_load/test_full_roundtrip.py`

- [ ] Test Save → Load → Process 3 turns → Save → Load → Verify
- [ ] Test turn_number, events, fleet movement across cycles

**Notes:**

### Task 5.3: JSON format stability test [Simple]
**File:** `tests/integration/save_load/test_full_roundtrip.py` (extend)
**Tests:** `pytest tests/integration/save_load/test_full_roundtrip.py`

- [ ] Test to_dict() output is fully JSON-serializable
- [ ] Test all dict keys are strings
- [ ] Test no non-serializable objects in output

**Notes:**

### Task 5.4: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] All tests pass, no regressions

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ -n 12` — all tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
