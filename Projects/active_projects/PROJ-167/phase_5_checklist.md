# Phase 5: Verification & Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-167 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Full test suite verification, remaining hardcoded color audit, final cleanup

---

## Tasks

### Task 5.1: Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify: 11,994+ tests pass, 0 failures
- [ ] Document any test count changes (new tests added, etc.)

**Notes:**

---

### Task 5.2: Hardcoded Color Audit [Simple]
**Tests:** N/A (audit only)

- [ ] Run: `grep -rn "color_hint.*'#" game/simulation/components/abilities/` — should only hit `ui_colors.py`
- [ ] Run: `grep -rn "'#[0-9A-Fa-f]\{6\}'" game/simulation/components/abilities/` — should only hit `ui_colors.py`
- [ ] Run: `grep -rn "'#[0-9A-Fa-f]\{6\}'" game/ui/screens/builder/detail_panel.py` — should only hit imported constants (no raw hex)
- [ ] Check that no ability file still has inline hex strings
- [ ] Document any remaining hardcoded colors that were intentionally left inline (with justification)

**Notes:**

---

### Task 5.3: Import Verification [Simple]
**Tests:** N/A (verification only)

- [ ] Verify no circular imports: `python -c "from game.simulation.components.abilities.ui_colors import *; print('OK')"`
- [ ] Verify no simulation→ui imports were added: `grep -rn "from game.ui" game/simulation/` — should find nothing
- [ ] Verify ui→simulation imports are clean: `grep -rn "from game.simulation.components.abilities.ui_colors" game/ui/` — should only be detail_panel.py

**Notes:**

---

### Task 5.4: Final Documentation [Simple]
**File:** `game/simulation/components/abilities/ui_colors.py`, `game/ui/colors.py`

- [ ] Verify both files have clear module docstrings
- [ ] Verify constant naming is consistent (HINT_* for ability, semantic names for UI)
- [ ] Update plan.md Current State to "Complete"
- [ ] Update plan.md phase table — all phases "Complete"

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Full test suite passes: 11,994+ tests
- [ ] No hardcoded hex colors remain in ability files
- [ ] No layer boundary violations
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md Completion Checklist — all items checked
