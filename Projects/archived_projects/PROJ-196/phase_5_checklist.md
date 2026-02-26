# Phase 5: Non-Test-Lab Color Migration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-196 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace common inline color tuples in non-Test-Lab files with the 6 new `colors.py` constants. Only target clear semantic matches.

---

## Tasks

### Task 5.1: Audit non-Test-Lab files for common color matches [Simple]
**Tests:** Read-only — no code changes

- [x] Search for `(220, 220, 220)` in non-test-lab `game/ui/` files → candidates for `TEXT_LIGHT`
- [x] Search for `(150, 150, 150)` → candidates for `TEXT_MUTED` (only text uses, not borders)
- [x] Search for `(100, 100, 120)` → candidates for `BORDER_LIGHT`
- [x] Search for `(80, 80, 90)` → candidates for `BORDER_DARK`
- [x] Search for `(30, 30, 35)` → candidates for `PANEL_BG`
- [x] Search for `(100, 100, 100)` → candidates for `TEXT_DIM`
- [x] Document which replacements are safe (same semantic purpose as constant name)

**Notes:** BORDER_DARK and PANEL_BG had no matches outside test_lab/colors.py. Most (100, 100, 100) uses were armor/default colors, NOT text - skipped. setup_renderer.py:154 (150, 150, 150) was a BORDER not text - skipped.

---

### Task 5.2: Replace common inline colors in non-Test-Lab files [Simple]
**Tests:** `pytest tests/ --testmon`

- [x] For each file identified in 5.1: add `from game.ui.colors import <constant>` and replace inline tuple
- [x] Run tests after each file or batch

**Notes:** Replaced 10 inline colors across 7 files:
- TEXT_LIGHT (2): system_mode.py, setup_renderer.py
- TEXT_MUTED (6): battle_panels.py, ship_stats_renderer.py (3), strategy_widgets.py (2)
- BORDER_LIGHT (2): scrollable_json_panel.py, weapons_renderer.py

---

### Task 5.3: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] All 12,734 tests pass (1 skipped)

**Notes:** Tests passed.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ -n 12` passes
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 6
