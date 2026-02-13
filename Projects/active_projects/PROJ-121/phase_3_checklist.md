# Phase 3: UI-Framework

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-121 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Address findings in the UI-Framework module (10 findings, 0 critical)
**Priority:** Normal

---

## Tasks

### Task 3.1: LEG-UI2-001 - Dead Code - draw_hud and draw_bar Functi [Simple]
**File:** `game/ui/renderer/game_renderer`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 3.2: LEG-UI2-002 - Unused Method - create_ai_for_ship in Ba [Simple]
**File:** `game/ui/orchestration/battle_o`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 3.3: LEG-UI2-003 - Unused Method - capture_step in Screensh [Simple]
**File:** `game/ui/services/screenshot_ma`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 3.4: LEG-UI2-004 - Duplicate Exception Handlers in ShipIO [Simple]
**File:** `game/ui/services/ship_io.py:71`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 3.5: LEG-UI2-005 - Comment References "legacy behavior" in [Medium]
**File:** `game/ui/services/ship_factory.`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 3.6: LEG-UI2-006 - Basic Color Constants (BLUE, RED, GREEN) [Simple]
**File:** `game/ui/colors.py:9-11`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 3.7: LEG-UI2-007 - ShipIOAdapter vs ShipIO Direct Access [Medium]
**File:** `game/ui/services/ship_io_adapt`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 3.8: LEG-UI2-008 - Excessive getattr() with Defaults in bat [Medium]
**File:** `game/ui/services/battle_ui_ser`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 3.9: LEG-UI2-009 - Singleton Pattern Still in Use for Asset [N]
**File:** `game/ui/assets/ship_theme_mana`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 3.10: LEG-UI2-010 - Anticipatory Code in _CONTEXT_OVERLAP [Simple]
**File:** `game/ui/services/input_mapper.`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]


---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
