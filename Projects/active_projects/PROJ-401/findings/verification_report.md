# PROJ-401 Verification Report

**Date:** 2026-05-09
**Branch:** `feat/03c-phase-aware-execution`
**Source bug:** REMEDIATION_PLAN.md B-02 (Tier 1) — Passenger-load validator accepts missing `species_id` while executor no-ops.

## Bug confirmation

The bug was reproduced live before the fix: with the unmodified validator, the new regression test (`test_validate_rejects_passenger_load_with_missing_species_id`) failed on `assert not result.is_valid` — `_validate_load` returned `ValidationResult.success()` for `cargo_type="passengers"`, `direction="load"`, `species_id=None`. This matched the reviewer probe in B-02 exactly.

## Fix

`game/strategy/validation/transfer_validator.py` — added an early rejection at the top of the `cargo_type == "passengers"` block of `_validate_load`:

```python
if species_id is None:
    return ValidationResult.error(
        f"Passenger load on {planet.name} requires a species selection.",
        code="MISSING_SPECIES_ID"
    )
```

Error code `MISSING_SPECIES_ID` mirrors the snake-upper convention used by adjacent codes (`NO_CARGO_SPACE`, `NO_POPULATION`). The check is placed before capacity / population lookups so it fails fast before any `fleet.resources` access.

## Tests

- New regression: `tests/unit/strategy/validation/test_transfer_validator_robustness.py::test_validate_rejects_passenger_load_with_missing_species_id` — RED before fix, GREEN after.
- Updated 4 callers that were implicitly relying on the gap by passing `species_id=None`: `test_validate_accepts_fleet_at_system_center` (added populations + species), and `test_load_passengers_success` / `test_load_fails_when_fleet_full` / `test_load_fails_when_colony_empty` in `tests/integration/strategy/transfer/test_transfer_validation.py` (added `species_id="human"`).
- Broader selector `pytest tests/ -k "transfer or load_population or passengers" -q`: **326 passed, 0 failed**.

## Deferrals

`_validate_unload` and `_validate_fleet_transfer` accept `species_id=None` for passengers without rejection. PROJ-393 only deleted the LOAD-side fallback, so the contract on those branches is unchanged for now. Logged in `decisions.md` for follow-up triage. Not fixed here — out of PROJ-401 scope.

## Status

Phase 1 complete. Awaiting user smoke verification.
