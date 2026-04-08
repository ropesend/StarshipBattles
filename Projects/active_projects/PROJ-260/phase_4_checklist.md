# Phase 4: Thin Ship Facade + Documentation + Verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-260 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Verify Ship.py is under 500 lines. If not, apply additional extractions identified in Phase 1. Update documentation. Run full test suite. Verify no regressions.

**Prerequisites:** Phases 2 and 3 complete. Both new delegates extracted and tested.

---

## Tasks

### Task 4.1: Measure and Verify Line Count [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** N/A

- [ ] Run `wc -l game/simulation/entities/ship.py` -- record result
- [ ] If under 500 lines: proceed to Task 4.3 (skip 4.2)
- [ ] If over 500 lines: proceed to Task 4.2 for additional extraction

**Notes:** Record the exact line count.

---

### Task 4.2: Additional Extractions (if needed) [Complex]
**File:** `game/simulation/entities/ship.py` and new delegate files
**Tests:** Relevant test files

This task only applies if Ship.py is still over 500 lines after Phases 2 and 3.

- [ ] Review Phase 1 extraction plan for additional candidates
- [ ] Candidates (from Phase 1 analysis):
  - Move `change_class()` to ShipLayerManager if not already done
  - Move `recalculate_stats()` orchestration if identified as movable
  - Move dirty flag logic (`mark_stats_dirty`, `recalculate_stats_if_dirty`) to a delegate
  - Consolidate facade methods (some may be removable if callers can use delegate directly)
  - Remove any blank lines, dead comments, or vestigial code
- [ ] For each additional extraction: write test first, then implement
- [ ] Run affected tests after each change
- [ ] Re-measure: `wc -l game/simulation/entities/ship.py`
- [ ] Repeat until under 500 lines

**Notes:** If the <500 target is unreachable without breaking the facade pattern, document why and propose a revised target in decisions.md.

---

### Task 4.3: Update Ship Class Docstring [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** N/A

- [ ] Update Ship class docstring to list ALL delegates (now 11):
  - ShipComponentManager
  - ShipCombatManager
  - ShipCombatEngine
  - ShipStatsCalculator
  - ShipSerializer
  - ShipStatQuerier
  - ShipValidatorHelper
  - ShipFormation
  - ShipPhysicsMixin
  - ShipLayerManager (NEW)
  - ShipResourceManager (NEW)
- [ ] Verify docstring accurately describes Ship's role as a facade

---

### Task 4.4: Update Documentation [Medium]
**Tests:** N/A

- [ ] Read `docs/01_ARCHITECTURE.md` -- check if Ship decomposition is described
- [ ] Read `docs/02_PATTERNS.md` -- check pattern #5 (Facade/Delegate) for Ship
- [ ] Update docs if they reference Ship's internal methods that moved to delegates
- [ ] Ensure the Facade/Delegate pattern documentation mentions the new delegates
- [ ] If any new patterns or conventions were established, document them

**Notes:** Only update docs that are affected by this change. Do not rewrite docs that are still accurate.

---

### Task 4.5: Full Test Suite [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run full sharded test suite: `python Tools/test_sharded/test_sharded.py`
- [ ] Verify 14783+ tests passing (zero regressions from baseline)
- [ ] If any failures: investigate, fix, and re-run
- [ ] Record final test count

**Notes:** This is the final gate. No regressions allowed.

---

### Task 4.6: Final Metrics [Simple]
**Tests:** N/A

- [ ] Record final Ship.py line count: `wc -l game/simulation/entities/ship.py`
- [ ] Record Ship.py method count (public + private)
- [ ] Record new file sizes:
  - `wc -l game/simulation/entities/ship_layer_manager.py`
  - `wc -l game/simulation/entities/ship_resource_manager.py`
  - `wc -l tests/unit/simulation/entities/test_ship_layer_manager.py`
  - `wc -l tests/unit/simulation/entities/test_ship_resource_manager.py`
- [ ] Verify Ship is now a thin facade with NO implementation logic remaining
- [ ] Update plan.md with final metrics

**Notes:** Target: Ship.py < 500 lines. All implementation logic in delegates.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Ship.py < 500 lines (or revised target documented and approved)
- [ ] Ship class docstring updated with all 11 delegates
- [ ] docs/ updated where affected
- [ ] Full test suite passing (14783+ tests, zero regressions)
- [ ] Final metrics recorded
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete"
- [ ] Update plan.md Verification section (all checkboxes)
