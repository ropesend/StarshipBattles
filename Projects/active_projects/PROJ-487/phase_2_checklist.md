# Phase 2: Migrate test callers + delete deprecated wrappers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-487 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate the ~56 test call sites of the fuel wrappers to the generic consumable API, then delete the four wrappers (~16 LOC).

---

## Tasks

### Task 2.1: Migrate the test suite callers
**File:** `tests/unit/strategy/data/test_facility_resource_tracking.py` + related test files
**Tests:** `pytest tests/unit/strategy/`

- [ ] Grep `tests/` for `\.add_fuel\b`, `\.get_fuel_storage\b`, `\.withdraw_fuel\b`, `\.get_max_fuel_storage\b`
- [ ] For each call site, replace with the generic `*_consumable("fuel", ...)` equivalent
- [ ] Re-run the affected test files; verify behavioral parity (the wrappers used to delegate to the same generic methods, so behavior should match exactly)

### Task 2.2: Delete the four deprecated wrappers
**File:** `game/strategy/data/planetary_facility.py`
**Tests:** `pytest tests/unit/strategy/`

- [ ] Delete `get_fuel_storage` at line 209 (~4 LOC including signature + body)
- [ ] Delete `get_max_fuel_storage` at line 213 (~4 LOC)
- [ ] Delete `add_fuel` at line 217 (~4 LOC)
- [ ] Delete `withdraw_fuel` at line 221 (~4 LOC)
- [ ] Delete the `# Deprecated fuel-specific wrappers (F-A-012)` header comment at line 196 once all four are gone

### Phase Verification
- [ ] `pytest tests/ --testmon` passes
- [ ] `grep -rn "add_fuel\|get_fuel_storage\|withdraw_fuel\|get_max_fuel_storage" .` returns 0 matches anywhere in the repo
- [ ] `grep -rn "F-A-012" .` returns 0 matches (or only in archival material — see notes)

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to mark project complete

_Source audit: `Reviews/results/2026-05-20_210635_legacy-audit/`. See `findings/source_audit.md` for the link._
