# Phase 2: Align top-level interfaces aggregator

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-422 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
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

- [x] Update the import block to pull every ABC from `game.strategy.interfaces.engines` (the package). Single consolidated `from ... import (...)` block.
- [x] Update `__all__` to list **all 18 ABC names** plus the existing `IBattleResolver` / `BattleResult`.
- [x] Verify no other file in `game/strategy/interfaces/` was touched.

**Notes:** Drift closed: added `IOrganicsConsumptionEngine`, `IHappinessEngine`, `IQualityEngine`, `IAtmosphereEngine`, `IWaterEngine` to both the import block and `__all__`.

### Task 2.2: Verify symmetric re-export [Simple]
**Tests:** `pytest tests/unit/strategy/interfaces/test_engines_package_layout.py -q`

- [x] All 6 assertions in `test_engines_package_layout.py` are now green.
- [x] Confirm by hand: `python -c "import game.strategy.interfaces as i; ..."` lists all 18 ABCs.

**Notes:** All 6 layout tests pass. Hand-check confirms 18 ABC names (excluding `IBattleResolver`) are present in `interfaces.__all__`.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `game/strategy/interfaces/__init__.py` re-exports all 18 engine ABCs
- [x] Full layout test is green
- [x] `python Projects/scripts/validate_phase.py PROJ-422 2` passes
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
