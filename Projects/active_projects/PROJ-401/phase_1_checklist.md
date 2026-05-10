# Phase 1: Validator rejects missing species_id on passenger load

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-401 1`
> 2. Only proceed if output shows PASSED

**Status:** Complete
**Objective:** Make `TransferValidator` reject the exact passenger-load shape the executor now no-ops, so validation and execution agree.

---

## Tasks

### Task 1.1: Read validator and executor to confirm contract [Simple]
**File:** `game/strategy/validation/transfer_validator.py:189-223` + `game/strategy/engine/order_handlers/transfer_branches.py:101-111`
**Tests:** N/A

- [x] Read `_validate_load` to see how `species_id` is currently used and what other error_codes look like.
- [x] Read `transfer_branches.py:101-111` to confirm what executor requires.
- [x] Choose error_code identifier and message phrasing consistent with existing codes in the validator.
- [x] Record the chosen identifier in `decisions.md`.

**Notes:** Existing codes in `_validate_load`: `NO_CARGO_SPACE`, `NO_POPULATION`, `NO_STAGING_ITEMS`, `NO_POD_CAPACITY`. Picked `MISSING_SPECIES_ID` to match the snake-upper convention. Executor at `transfer_branches.py:105-111` warns + returns 0 when `species_id is falsy` — validator must mirror that contract.

### Task 1.2: TDD — write failing regression test [Medium]
**File:** `tests/unit/strategy/validation/test_transfer_validator_robustness.py`
**Tests:** `pytest tests/unit/strategy/validation/test_transfer_validator_robustness.py -k missing_species_id -v`

- [x] Add a test that calls `TransferValidator.validate(cargo_type="passengers", direction="load", species_id=None, ...)` with otherwise-valid args and asserts `is_valid=False` with the new error_code.
- [x] Run the test against unmodified production — confirm it fails (validation currently returns `is_valid=True`).

**Notes:** Test added as `test_validate_rejects_passenger_load_with_missing_species_id`. Initial run confirmed RED on `assert not result.is_valid` (validator returned success).

### Task 1.3: Implement the validator change [Simple]
**File:** `game/strategy/validation/transfer_validator.py`
**Tests:** `pytest tests/unit/strategy/validation/test_transfer_validator_robustness.py -v`

- [x] Inside the `cargo_type == "passengers"` block of `_validate_load`, add an early rejection when `species_id is None` (or equivalent missing check).
- [x] Run the regression test — should pass.
- [x] Run the full validator test module — should pass with no regressions.

**Notes:** Inserted check at the top of the `cargo_type == "passengers"` branch of `_validate_load`, before the capacity / population checks, with a PROJ-401 reference comment. Module result: 3 passed.

### Task 1.4: Run broader transfer/passenger suite to confirm no callers were silently relying on the gap
**Tests:** `pytest tests/ -k "transfer or load_population or passengers" -q`

- [x] Run focused selector. Should pass.
- [x] If anything fails: triage. If a test was passing a `None` species_id and expecting success, that test was encoding the bug and should be updated.

**Notes:** Initial run: 3 failures in `tests/integration/strategy/transfer/test_transfer_validation.py` (`test_load_passengers_success`, `test_load_fails_when_fleet_full`, `test_load_fails_when_colony_empty`) — they passed `species_id=None` implicitly. Updated each to pass `species_id="human"` (matching the conftest default species). Also fixed `test_validate_accepts_fleet_at_system_center` in the robustness file (added populations + species_id). Final: 326 passed.

### Task 1.5: Closeout
- [x] Update Phase 1 status to `Complete`
- [x] Update plan.md Quick Status + Current State
- [x] Update `Projects/projects_index.md` row for PROJ-401 to `Complete`
- [x] Both validators pass
- [x] Commit `PROJ-401 phase 1: validator rejects missing species_id on passenger load + regression`

**Notes:** See verification_report.md for the full post-implementation summary.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] `pytest tests/ -k "transfer or load_population or passengers"` passes
- [x] `python Projects/scripts/validate_phase.py PROJ-401 1` PASSED
- [x] `python Projects/scripts/validate_audit_ready.py PROJ-401` PASSED
