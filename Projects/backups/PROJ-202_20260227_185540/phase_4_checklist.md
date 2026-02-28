# Phase 4: Verify & Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-202 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Final verification that refactoring is complete, correct, and documented.

---

## Tasks

### Task 4.1: Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Record results: ____ passed, ____ failed
- [ ] Verify: 0 failures
- [ ] Verify: Test count hasn't decreased

**Notes:** Baseline is 6246 tests.

---

### Task 4.2: Complexity Verification [Simple]
**Tests:** `radon cc game/ui/screens/strategy_renderer.py -s -a`

- [ ] Run radon: `radon cc game/ui/screens/strategy_renderer.py -s -a`
- [ ] Verify `_draw_systems` CC is now < 20 (goal achieved)
- [ ] Record final CC: ____ (was 29)
- [ ] Verify: No new methods above CC 20 introduced

---

### Task 4.3: Code Review Checklist [Simple]
**File:** `game/ui/screens/strategy_renderer.py`

- [ ] No commented-out code left behind
- [ ] No TODO comments introduced
- [ ] All new methods have docstrings
- [ ] Type hints present on method signatures
- [ ] No duplicate code between extracted methods
- [ ] ZOOM_DETAIL_THRESHOLD used consistently (no stray 0.5 literals)

---

### Task 4.4: Update Project Documentation [Simple]
**File:** `Projects/active_projects/PROJ-202/`

- [ ] Update `decisions.md` with any decisions made during implementation
- [ ] Verify all findings files are accurate
- [ ] Record final complexity metrics in plan.md

---

### Task 4.5: Final Commit [Simple]

- [ ] Stage all changes: `git add -A`
- [ ] Create final commit:
```
[PROJ-202] Complete: Reduce _draw_systems CC from 29 to [X]

Extracted helper methods:
- _classify_star_color(): Pure function for color-to-asset mapping
- _draw_colony_marker_if_zoomed_out(): Colony marker rendering
- _draw_system_stars(): Star rendering loop

Added test coverage:
- Star color classification (6 tests)
- Colony marker visibility (4 tests)
- Selection highlight (3 tests)
- Fallback rendering (2 tests)
- Star labels (3 tests)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```
- [ ] Verify commit succeeded

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All tests pass
- [ ] CC goal achieved (< 20)
- [ ] Final commit created
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md Verification section checkboxes
- [ ] Mark project as complete in plan.md
