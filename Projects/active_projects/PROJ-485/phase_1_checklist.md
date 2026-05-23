# Phase 1: Delete dead methods + migrate tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-485 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Delete three dead static methods on `CarrierAIController` (`_find_tactical_launch_ability`, `_pop_fighter_cvs`, `_pop_cvs`) and migrate any remaining test references to the modern surface (`_sum_launch_rate`, `_pop_cvs_within_budget`).

---

## Tasks

### Task 1.1: Delete dead methods + migrate any test callers
**File:** `game/ai/carrier_controller.py`
**Tests:** `pytest tests/unit/ai/`

- [x] Grep for `_find_tactical_launch_ability`, `_pop_fighter_cvs`, `_pop_cvs` across `tests/`, `combat_lab/`, `Tools/` to enumerate test callers (audit grep across `game/` confirmed 0 production callers, but tests are expected)
- [x] For each test caller of `_find_tactical_launch_ability`: migrate to `_sum_launch_rate` or remove the introspective coverage if it no longer maps to a modern surface
- [x] For each test caller of `_pop_fighter_cvs`: migrate to `_pop_cvs_within_budget`
- [x] For each test caller of `_pop_cvs`: migrate to `_pop_cvs_within_budget`
- [x] Delete `_find_tactical_launch_ability` at `game/ai/carrier_controller.py:358-390` (~30 LOC, 0 production callers)
- [x] Delete `_pop_fighter_cvs` at `game/ai/carrier_controller.py:255-263` (~8 LOC, 0 production callers)
- [x] Delete `_pop_cvs` at `game/ai/carrier_controller.py:265-300` (~45 LOC, only caller was `_pop_fighter_cvs` which is now gone)

### Phase Verification
- [x] `pytest tests/ --testmon` passes
- [x] `grep -rn "_find_tactical_launch_ability" .` returns 0 matches
- [x] `grep -rn "_pop_fighter_cvs" .` returns 0 matches
- [x] `grep -rn "_pop_cvs\b" .` returns 0 matches (whole-word; `_pop_cvs_within_budget` should remain untouched)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to mark project complete

_Source audit: `Reviews/results/2026-05-20_210635_legacy-audit/`. See `findings/source_audit.md` for the link._
