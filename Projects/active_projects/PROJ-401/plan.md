# PROJ-401: Tier 1 B-02 — Passenger-load validator missing-`species_id` rejection

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Add validator rejection + regression | Complete | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-09
**Active Phase:** Closeout
**Last Action:** Phase 1 complete — `MISSING_SPECIES_ID` rejection added, regression test landed, broader transfer/passenger suite (326 tests) green
**Next Action:** User verification
**Blockers:** None

## Overview
PROJ-393 Phase 3 deleted the implicit "first species" passenger-load fallback in `transfer_branches.py:101-111`, so the executor now logs a warning and transfers 0 when `species_id` is None. But `TransferValidator._validate_load` still gates the species check on `if species_id:`, which means missing `species_id` passes validation. Validation and execution disagree — orders pass validation, get queued, then no-op at runtime. This project tightens the validator to reject what the executor will no-op.

## Goals
- Validator must return `is_valid=False` (with a new error_code, e.g. `MISSING_SPECIES_ID`) when `cargo_type == "passengers"`, `direction == "load"`, and `species_id is None`.
- Add a regression test asserting validation rejects this exact case.

## Scope
**In:**
- One change in `game/strategy/validation/transfer_validator.py` inside `_validate_load`.
- One regression test in the corresponding test file.

**Out:**
- The other PROJ-393 deferrals (`fleet_id` deletion, `view=None` migration, Combat Lab vars) — these were closed by PROJ-397.
- Any rework of `transfer_branches.py` — the executor is already correct.

## Key Files
| Component | File Path |
|-----------|-----------|
| Validator | `game/strategy/validation/transfer_validator.py` |
| Validator tests | `tests/unit/strategy/validation/test_transfer_validator.py` (confirm path) |
| Executor (read-only ref) | `game/strategy/engine/order_handlers/transfer_branches.py` |

## Source Evidence (REMEDIATION_PLAN B-02)
- `game/strategy/validation/transfer_validator.py:215-221` — `_validate_load` species check gated on `if species_id:`.
- `game/strategy/engine/order_handlers/transfer_branches.py:101-111` — executor now requires `species_id`.
- Reviewer probe: `TransferValidator.validate(..., cargo_type="passengers", direction="load", species_id=None, skip_location_check=True)` returned `is_valid=True`.
- PROJ-393 review (`Reviews/results/2026-05-09_proj-380-399-implementation-review/PROJ-393_report.md`)

## Verification
- [ ] Phase 1 checklist complete
- [ ] New regression test passes against fixed validator
- [ ] `pytest tests/ -k "transfer or load_population or passengers" -q` passes
- [ ] `python Projects/scripts/validate_audit_ready.py PROJ-401` passes
- [ ] User verified
