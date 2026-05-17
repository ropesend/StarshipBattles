# Phase 2: Align top-level interfaces aggregator

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-422 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_1
**Review Mode:** lightweight
**Files (planned):** game/strategy/interfaces/__init__.py
**Objective:** Make `game/strategy/interfaces/__init__.py` re-export every ABC the engines package exposes; close the existing 5-name drift.

---

## Tasks

### Task 2.1: Rewrite `interfaces/__init__.py` to re-export all 18 ABCs [Simple]
**File:** `game/strategy/interfaces/__init__.py`
**Tests:** `pytest tests/unit/strategy/interfaces/test_engines_package_layout.py -q` — `test_top_level_interfaces_reexports_all_engines` must now go green

The current file re-exports 13 of 18 ABCs (lines 12-26). Missing: `IOrganicsConsumptionEngine`, `IHappinessEngine`, `IQualityEngine`, `IAtmosphereEngine`, `IWaterEngine`. Close that drift here.

- [ ] Update the import block to pull every ABC from `game.strategy.interfaces.engines` (the package). Single import line per leaf, or one consolidated `from ... import (...)` block — match the existing file's style.
- [ ] Update `__all__` to list **all 18 ABC names** (plus whatever non-engine symbols the file already exposes, e.g. battle resolver types — leave those untouched).
- [ ] Verify no other file in `game/strategy/interfaces/` was touched.

**Notes:** [Filled during implementation]

### Task 2.2: Verify symmetric re-export [Simple]
**Tests:** `pytest tests/unit/strategy/interfaces/test_engines_package_layout.py -q`

- [ ] All 6 assertions in `test_engines_package_layout.py` are now green.
- [ ] Confirm by hand: `python -c "import game.strategy.interfaces as i; print(sorted(n for n in i.__all__ if n.startswith('I')))"` lists all 18 ABCs.

**Notes:** [Filled during implementation. Per TD plan §"Per-Phase Success Criteria": Phase 2 is done only when every name in `engines.__all__` is also importable from `game.strategy.interfaces`.]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `game/strategy/interfaces/__init__.py` re-exports all 18 engine ABCs
- [ ] Full layout test is green
- [ ] `python Projects/scripts/validate_phase.py PROJ-422 2` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
