# Phase 5: Add a registry-purity guard

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-428 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_4
**Review Mode:** standard
**Files (planned):**
- `tests/unit/strategy/turn_engine/test_turn_phase_registry_purity.py` (or `test_tick_phase_descriptors.py`)

**Objective:** Add an AST-driven test that prevents future regressions of
the registry-as-data contract.

---

## Tasks

### Task 5.1: AST guard — no module-level functions [Simple]
**File:** `tests/unit/strategy/turn_engine/test_turn_phase_registry_purity.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_phase_registry_purity.py`

- [ ] Parse `turn_phase_registry.py` with the `ast` module.
- [ ] Assert there are zero top-level `FunctionDef` and `AsyncFunctionDef`
      nodes.
- [ ] Confirm the test passes against the post-Phase-4 code.

**Notes:**

### Task 5.2: AST guard — no gameplay engine imports [Simple]
**File:** `tests/unit/strategy/turn_engine/test_turn_phase_registry_purity.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_phase_registry_purity.py`

- [ ] Walk the registry module's `Import` and `ImportFrom` nodes.
- [ ] Assert `PlanetModifierEffectEngine` and `MinefieldResolver` are not
      imported (and ideally that nothing from gameplay engine modules is).
- [ ] Confirm the test passes against the post-Phase-4 code.

**Notes:**

### Task 5.3: Golden descriptor list assertions [Simple]
**File:** `tests/unit/strategy/turn_engine/test_turn_phase_registry_purity.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_phase_registry_purity.py`

- [ ] Assert that `DEFAULT_TICK_PHASE_LIST` has the expected phase keys
      in the expected order with the expected timing buckets.
- [ ] Assert the same for `DEFAULT_END_OF_TURN_PHASE_LIST`.
- [ ] Confirm tests pass against the post-Phase-4 code.

**Notes:**

### Task 5.4: Verify the guard fails when violated [Simple]

- [ ] In a scratch experiment, reintroduce a dummy module-level function
      in `turn_phase_registry.py` and confirm the AST guard fails.
- [ ] Revert the experimental change.
- [ ] Verify: focused turn-engine suite is green.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/strategy/turn_engine/ -x` is green
- [ ] Update status at top of this file to `Complete (Committed)`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6
