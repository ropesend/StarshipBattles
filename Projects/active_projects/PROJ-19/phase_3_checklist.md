# Phase 3: Replace AI Layer Duck Typing

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-19 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate AI controller and behaviors to Protocol-based checks

---

## Tasks

### Task 3.1: Update controller.py combat entity checks [Simple]
**File:** `game/ai/controller.py`
**Tests:** `pytest tests/unit/ai/ -v`

- [x] Add import: `from game.core.protocols import is_combatant`
- [x] Replace `hasattr(obj, 'team_id')` with `is_combatant(obj)` (around line 109)
- [x] Replace `hasattr(obj, 'team_id')` with `is_combatant(obj)` (around line 349)
- [x] Search for any other hasattr patterns and evaluate
- [x] Run AI tests: `pytest tests/unit/ai/test_ai_controller.py -v`
- [x] Verify: Combat targeting works correctly in game

**Notes:** Replaced 2 hasattr(obj, 'team_id') patterns with is_combatant(obj). All 189 AI tests pass.

---

### Task 3.2: Review behaviors.py getattr patterns [Simple]
**File:** `game/ai/behaviors.py`
**Tests:** `pytest tests/unit/ai/test_behaviors.py -v` (if exists)

- [x] Audit 7 getattr calls:
  - Line ~199: `getattr(master, 'is_derelict', False)` - KEEP (genuinely optional)
  - Line ~204: `getattr(ship, 'formation_rotation_mode', 'relative')` - KEEP (optional)
  - Line ~229: `getattr(ship, 'turn_throttle', 1.0)` - KEEP (optional)
  - Line ~248: `getattr(master, 'is_thrusting', False)` - KEEP (optional)
  - Line ~250: `getattr(master, 'max_speed', 0)` - KEEP (optional with default)
  - Line ~270: formation_rotation_mode check - KEEP
  - Line ~303: formation_rotation_mode check - KEEP
- [x] Document decision in decisions.md: "Keep formation getattr patterns - genuinely optional"
- [x] Run formation tests if they exist
- [x] Verify: Formation behavior works correctly in game

**Notes:** All 7 getattr patterns in behaviors.py are genuinely optional formation attributes with sensible defaults. Already documented in decisions.md.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run: `pytest tests/unit/ai/ -v` - AI tests pass (189 tests)
- [x] Run: `pytest tests/ --testmon -q` - no regressions (118 tests)
- [x] Manual test: Combat targeting and formation behavior work
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
