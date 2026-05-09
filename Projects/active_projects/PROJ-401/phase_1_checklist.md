# Phase 1: Validator rejects missing species_id on passenger load

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-401 1`
> 2. Only proceed if output shows PASSED

**Status:** Not Started
**Objective:** Make `TransferValidator` reject the exact passenger-load shape the executor now no-ops, so validation and execution agree.

---

## Tasks

### Task 1.1: Read validator and executor to confirm contract [Simple]
**File:** `game/strategy/validation/transfer_validator.py:189-223` + `game/strategy/engine/order_handlers/transfer_branches.py:101-111`
**Tests:** N/A

- [ ] Read `_validate_load` to see how `species_id` is currently used and what other error_codes look like.
- [ ] Read `transfer_branches.py:101-111` to confirm what executor requires.
- [ ] Choose error_code identifier and message phrasing consistent with existing codes in the validator.
- [ ] Record the chosen identifier in `decisions.md`.

**Notes:**

### Task 1.2: TDD — write failing regression test [Medium]
**File:** test file alongside the validator (confirm exact path)
**Tests:** `pytest tests/unit/strategy/validation/test_transfer_validator.py -k species_id -v`

- [ ] Add a test that calls `TransferValidator.validate(cargo_type="passengers", direction="load", species_id=None, ...)` with otherwise-valid args and asserts `is_valid=False` with the new error_code.
- [ ] Run the test against unmodified production — confirm it fails (validation currently returns `is_valid=True`).

**Notes:**

### Task 1.3: Implement the validator change [Simple]
**File:** `game/strategy/validation/transfer_validator.py`
**Tests:** `pytest tests/unit/strategy/validation/test_transfer_validator.py -v`

- [ ] Inside the `cargo_type == "passengers"` block of `_validate_load`, add an early rejection when `species_id is None` (or equivalent missing check).
- [ ] Run the regression test — should pass.
- [ ] Run the full validator test module — should pass with no regressions.

**Notes:**

### Task 1.4: Run broader transfer/passenger suite to confirm no callers were silently relying on the gap
**Tests:** `pytest tests/ -k "transfer or load_population or passengers" -q`

- [ ] Run focused selector. Should pass.
- [ ] If anything fails: triage. If a test was passing a `None` species_id and expecting success, that test was encoding the bug and should be updated.

**Notes:**

### Task 1.5: Closeout
- [ ] Update Phase 1 status to `Complete`
- [ ] Update plan.md Quick Status + Current State
- [ ] Update `Projects/projects_index.md` row for PROJ-401 to `Complete`
- [ ] Both validators pass
- [ ] Commit `PROJ-401 phase 1: validator rejects missing species_id on passenger load + regression`

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] `pytest tests/ -k "transfer or load_population or passengers"` passes
- [ ] `python Projects/scripts/validate_phase.py PROJ-401 1` PASSED
- [ ] `python Projects/scripts/validate_audit_ready.py PROJ-401` PASSED
