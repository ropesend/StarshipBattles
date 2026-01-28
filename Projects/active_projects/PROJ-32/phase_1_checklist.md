# Phase 1: Critical Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-32 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address critical severity findings that pose immediate risk
**Priority:** Immediate

---

## Tasks

#### Task 1.1: RES-01 - Control panel state mutation on reset [Simple]
**File:** `game/research/ui/research_controls.py`, `game/research/ui/research_scene.py`
**Tests:** `pytest tests/unit/research/test_research_controls.py::TestResetMethod`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:**
- Issue: `ResearchTreeScene._on_reset()` directly mutated `control_panel.tracker` and `control_panel.tech_tree` attributes, bypassing constructor initialization
- Fix: Added `ResearchControlPanel.reset(tracker, tech_tree)` method that properly encapsulates state updates
- Updated `_on_reset()` to call `control_panel.reset()` instead of direct attribute mutation
- Added 7 unit tests for the new `reset()` method
- All 209 research tests pass, all 4512 unit tests pass


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
