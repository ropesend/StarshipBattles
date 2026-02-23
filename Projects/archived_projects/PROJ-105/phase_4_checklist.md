# Phase 4: Capture Baselines & End-to-End Verify

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-105 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Capture baseline images and verify the full workflow works end-to-end

---

## Tasks

### Task 4.1: Capture Initial Baselines [Simple]
**Tests:** `pytest tests/visual_regression/ --update-baselines -n 1 -v`

- [ ] Run: `pytest tests/visual_regression/ --update-baselines -n 1 -v`
- [ ] Verify: 5 tests show "SKIPPED" with "Baseline updated" messages
- [ ] Verify: `tests/visual_regression/baselines/` contains 5 subdirectories:
  - `ship_stats_collapsed/baseline.png`
  - `ship_stats_expanded/baseline.png`
  - `seeker_monitor/baseline.png`
  - `battle_control_ongoing/baseline.png`
  - `battle_control_victory/baseline.png`
- [ ] Visually inspect each baseline PNG (open in image viewer) — should show recognizable panel content
- [ ] Verify file sizes are reasonable (5-50KB each)

**Notes:**

---

### Task 4.2: Verify Compare Mode (Identical) [Simple]
**Tests:** `pytest tests/visual_regression/ -v`

- [ ] Run: `pytest tests/visual_regression/ -v`
- [ ] Verify: all 5 tests PASS (identical render → match)
- [ ] Verify: no diff images generated in `tests/visual_regression/diffs/`

**Notes:**

---

### Task 4.3: Verify Regression Detection [Medium]
**Tests:** Manual — make a trivial change, verify detection, revert

- [ ] Make a temporary change to `game/ui/panels/battle_panels.py`:
  - Change background color at line 97 from `(20, 25, 35, UIConfig.PANEL_ALPHA)` to `(50, 25, 35, UIConfig.PANEL_ALPHA)`
- [ ] Run: `pytest tests/visual_regression/ -v`
- [ ] Verify: `ship_stats_collapsed` and `ship_stats_expanded` tests FAIL
- [ ] Verify: failure message includes changed_pixels count and change_percentage
- [ ] Verify: diff image generated at `tests/visual_regression/diffs/ship_stats_collapsed/diff.png`
- [ ] Open diff image — should show side-by-side with red highlights on changed background pixels
- [ ] Revert the change to `battle_panels.py` (restore original `(20, 25, 35, UIConfig.PANEL_ALPHA)`)
- [ ] Run: `pytest tests/visual_regression/ -v`
- [ ] Verify: all 5 tests PASS again

**Notes:**

---

### Task 4.4: Full Test Suite Verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run: `pytest tests/ -n 12`
- [ ] Verify: all tests pass including visual regression tests
- [ ] Verify: test count increased by 5+ from baseline (8167 → 8172+)
- [ ] Verify: no new warnings related to visual regression

**Notes:**

---

### Task 4.5: Git Cleanup [Simple]
**Files:** `.gitignore`

- [ ] Verify `tests/visual_regression/diffs/` is in `.gitignore`
- [ ] Stage and review baseline PNGs: `git add tests/visual_regression/baselines/`
- [ ] Verify baselines are tracked (not gitignored)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Baselines captured and committed
- [ ] Compare mode passes for all 5 panels
- [ ] Regression detection works (trivial change → failure + diff image)
- [ ] Revert → tests pass again
- [ ] Full test suite passes (`pytest tests/ -n 12`)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Complete"
