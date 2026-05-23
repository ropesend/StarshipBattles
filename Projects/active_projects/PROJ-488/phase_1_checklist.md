# Phase 1: Migrate 25 callers + delete alias

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-488 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate ~25 `MASS_EARTH` callers to the canonical `EARTH_MASS` symbol, then delete the alias.

---

## Tasks

### Task 1.1: Enumerate all `MASS_EARTH` callers
**File:** various
**Tests:** `pytest tests/ --testmon`

- [ ] Run `grep -rn "MASS_EARTH" .` and record the full caller list (verifier counted ~25; confirm exact count)
- [ ] Group callers by directory: `game/`, `tests/`, `Tools/`, diagnostics

### Task 1.2: Migrate all callers to `EARTH_MASS`
**File:** all caller files
**Tests:** `pytest tests/ --testmon`

- [ ] For each caller, replace `MASS_EARTH` with `EARTH_MASS`
- [ ] If the caller imports `MASS_EARTH` from `game.strategy.data.planet_physics`, switch the import to `from game.core.constants import EARTH_MASS` (or whatever the canonical path is — verify against the existing direct importers of `EARTH_MASS`)
- [ ] Run the affected test files to confirm no regressions

### Task 1.3: Delete the alias
**File:** `game/strategy/data/planet_physics.py`
**Tests:** `pytest tests/unit/strategy/data/`

- [ ] Delete `MASS_EARTH = EARTH_MASS  # Backward-compatible alias` at line 25 (and the surrounding blank line at 24 if it becomes orphan)
- [ ] If line 25 was the last reason for the import of `EARTH_MASS` into `planet_physics.py`, also remove the now-unused import; otherwise keep it

### Phase Verification
- [ ] `pytest tests/ --testmon` passes
- [ ] `grep -rn "MASS_EARTH" .` returns 0 matches across the entire repo
- [ ] The `EARTH_MASS` value at every former call site is numerically identical (the alias was a literal rebinding; this should be a no-op behaviorally)

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to mark project complete

_Source audit: `Reviews/results/2026-05-20_210635_legacy-audit/`. See `findings/source_audit.md` for the link._
