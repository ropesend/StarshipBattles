# Phase 1: Critical Foundation missing return

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-483 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Resolve the single CRITICAL Foundation finding — `_StatContributorRegistry.iter_for` is a generator method crossing module/layer boundaries (called from `simulation/entities/ship_stats.py:307`) but lacks a return annotation.

---

## Tasks

### Task 1.1: Annotate `_StatContributorRegistry.iter_for` [Simple]
**File:** `game/simulation/entities/stat_contributors/registry.py`
**Tests:** `pytest tests/ -k stat_contributor` then `mypy game/simulation/entities/stat_contributors/registry.py`

- [x] Add `-> Iterator[StatContributorEntry]` to `iter_for` (line 298 — verifier saw `yield entry` at line 318). Import `Iterator` from `typing` if not already imported
- [x] Ensure `StatContributorEntry` is importable in the signature scope (may already be defined in the same module)
- [x] Verify: `pytest tests/ -k stat_contributor` passes; `mypy` shows no new errors

### Task 1.2: Phase verification [Simple]
- [x] Verify: `pytest tests/ -k stat_contributor` (95 passed); mypy on file is clean (no errors on `registry.py`)
- [x] Verify: `mypy` clean on touched file

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-20_210540_type-audit/`. See `findings/source_audit.md` for the link._
