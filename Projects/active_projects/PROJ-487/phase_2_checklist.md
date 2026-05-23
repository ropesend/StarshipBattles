# Phase 2: Migrate test callers + delete deprecated wrappers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-487 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate the ~56 test call sites of the fuel wrappers to the generic consumable API, then delete the four wrappers (~16 LOC).

---

## Tasks

### Task 2.1: Migrate the test suite callers
**File:** `tests/unit/strategy/data/test_facility_resource_tracking.py` + related test files
**Tests:** `pytest tests/unit/strategy/`

- [x] Grep `tests/` for `\.add_fuel\b`, `\.get_fuel_storage\b`, `\.withdraw_fuel\b`, `\.get_max_fuel_storage\b`
- [x] For each call site, replace with the generic `*_consumable("fuel", ...)` equivalent
- [x] Re-run the affected test files; verify behavioral parity (the wrappers used to delegate to the same generic methods, so behavior should match exactly)

**Notes:** Migrated 4 test files:
- `tests/unit/strategy/data/test_facility_resource_tracking.py` — migrated ~34 call sites (class methods, assertions). Removed obsolete `test_fuel_wrappers_delegate_to_generic_consumable_api` test since the wrappers themselves are being deleted.
- `tests/integration/strategy/test_resupply_system.py` — migrated 4 `facility.get_fuel_storage()` assertions to `get_consumable_storage("fuel")`.
- `tests/integration/save_load/test_resupply_persistence.py` — migrated 1 `restored.facilities[0].get_fuel_storage()` assertion.
- `tests/unit/strategy/engine/test_resupply_engine.py` — migrated 3 mock-call assertions from `facility.withdraw_fuel.assert_called_once_with(N)` to `facility.withdraw_consumable.assert_called_once_with("fuel", N)`.

Targeted suite (resupply + facility): 74 passed.

### Task 2.2: Delete the four deprecated wrappers
**File:** `game/strategy/data/planetary_facility.py`
**Tests:** `pytest tests/unit/strategy/`

- [x] Delete `get_fuel_storage` at line 209 (~4 LOC including signature + body)
- [x] Delete `get_max_fuel_storage` at line 213 (~4 LOC)
- [x] Delete `add_fuel` at line 217 (~4 LOC)
- [x] Delete `withdraw_fuel` at line 221 (~4 LOC)
- [x] Delete the `# Deprecated fuel-specific wrappers (F-A-012)` header comment at line 196 once all four are gone

**Notes:** Deleted all four wrappers and the deprecated-wrappers banner. Also dropped the now-stale `(F-A-012)` annotation from the Generic consumable API banner and the explanatory paragraph that referenced the (now-removed) wrappers.

### Phase Verification
- [x] `pytest tests/ --testmon` passes
- [x] `grep -rn "add_fuel\|get_fuel_storage\|withdraw_fuel\|get_max_fuel_storage" .` returns 0 matches anywhere in the repo
- [x] `grep -rn "F-A-012" .` returns 0 matches (or only in archival material — see notes)

**Phase verification notes:**
- Targeted run (`tests/unit/strategy/ + tests/integration/strategy/ + tests/integration/save_load/`): 7304 passed.
- Full repo run (`pytest tests/ --ignore=tests/system`): 24635 passed, 1 skipped.
- `pytest tests/ --testmon` could not run due to a pre-existing testmon-on-Windows infrastructure error (`ValueError: path is on mount '\\.\nul'`); the full non-testmon run above stands in.
- Grep in `game/` for the four wrapper names: 0 matches.
- Grep in `tests/` for the four wrapper names: 0 matches.
- Remaining matches in the repo are all archival/historical: `Reviews/results/*/raw/coverage_matrix.json`, archived audit findings, `Projects/deep_archive/`, plus this project's own checklists and design docs (intentional historical record).
- `F-A-012` remaining matches: only in this project's design/decisions docs and archival material; the active codebase is clean.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to mark project complete

_Source audit: `Reviews/results/2026-05-20_210635_legacy-audit/`. See `findings/source_audit.md` for the link._
