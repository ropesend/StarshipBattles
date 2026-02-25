# Phase 5: Non-Test-Lab Color Migration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-196 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace common inline color tuples in non-Test-Lab files with the 6 new `colors.py` constants. Only target clear semantic matches.

---

## Tasks

### Task 5.1: Audit non-Test-Lab files for common color matches [Simple]
**Tests:** Read-only — no code changes

- [ ] Search for `(220, 220, 220)` in non-test-lab `game/ui/` files → candidates for `TEXT_LIGHT`
- [ ] Search for `(150, 150, 150)` → candidates for `TEXT_MUTED` (only text uses, not borders)
- [ ] Search for `(100, 100, 120)` → candidates for `BORDER_LIGHT`
- [ ] Search for `(80, 80, 90)` → candidates for `BORDER_DARK`
- [ ] Search for `(30, 30, 35)` → candidates for `PANEL_BG`
- [ ] Search for `(100, 100, 100)` → candidates for `TEXT_DIM`
- [ ] Document which replacements are safe (same semantic purpose as constant name)

**Notes:** Do NOT replace colors that serve a different semantic purpose (e.g., `(100, 100, 100)` as armor color, not text).

---

### Task 5.2: Replace common inline colors in non-Test-Lab files [Simple]
**Tests:** `pytest tests/ --testmon`

- [ ] For each file identified in 5.1: add `from game.ui.colors import <constant>` and replace inline tuple
- [ ] Run tests after each file or batch

**Notes:** Keep changeset small and targeted. Only replace exact matches where semantic purpose aligns.

---

### Task 5.3: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] All 12,718 tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ -n 12` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6
