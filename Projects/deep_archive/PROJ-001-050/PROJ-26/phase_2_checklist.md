# Phase 2: Major Issues

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-26 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address major severity findings that significantly impact quality
**Priority:** High

---

## Tasks

### Task 2.1: NC-03 - ShipBuilderService shim [Simple] ✓
**File:** `game/simulation/services/ship_builder_service.py` (already deleted before project)
**Tests:** N/A - already verified removed

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Already fixed before this project started. Verified: no `ship_builder_service.py` exists and no imports reference it in `game/`.

### Task 2.2: NC-02 - Builder vs Workshop terminology [Deferred]
**File:** `ui/builder/` and `game/ui/screens/builder/` directories + `builder_*.py` files
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:**
- **Investigation findings:** This is a larger migration than originally estimated (~80+ imports across ~40+ files)
- **Architecture observation:** "Builder" names reusable UI panels, "Workshop" names the screen that assembles them. This may be intentional layering.
- **Recommendation:** Defer to a dedicated project with proper planning

### Task 2.3: NC-05 - Battle vs Combat distinction [Simple] ✓
**File:** `docs/NAMING_CONVENTIONS.md` (created)
**Tests:** N/A (documentation task)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix (N/A - documentation)
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:**
- Created `docs/NAMING_CONVENTIONS.md` documenting:
  - Battle vs Combat distinction (simulation layer vs component behavior)
  - Builder vs Workshop architecture (reusable panels vs screen assembly)
  - Handler naming convention (prefix with context)
  - Scene vs Screen usage
  - Ability module package structure
- Documents existing intentional patterns rather than changing code

### Task 2.4: NC-02 - Workshop imports from Builder directory [Deferred]
**File:** Same scope as Task 2.2
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** This is part of the Builder→Workshop migration (Task 2.2). Deferred together.

### Task 2.5: NEW-03 - Duplicate InputHandler class [Simple] ✓
**File:** `game/core/input_handler.py` and `game/ui/screens/strategy_input_handler.py`
**Tests:** `pytest tests/repro_issues/test_bug_15_screenshot_strategy.py --testmon`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix (existing tests covered the rename)
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:**
- Renamed `InputHandler` → `StrategyInputHandler` in `strategy_input_handler.py`
- Updated import in `strategy_scene.py` to use `StrategyInputHandler`
- Updated test file to use new class name
- Left `game/core/input_handler.py::InputHandler` as is (game-level handler, no conflict)
- All 5 affected tests pass

### Task 2.6: NEW-05 - Duplicate Ability classes [Simple] ✓
**File:** `game/simulation/components/abilities.py` (deleted) and `game/simulation/components/abilities/` (kept)
**Tests:** `pytest tests/unit/entities/test_abilities.py tests/unit/entities/test_ability_interface.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix (existing tests cover ability imports)
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:**
- Python was already using `abilities/__init__.py` (the package), not `abilities.py` (the monolithic file)
- The monolithic `abilities.py` (565 lines) was dead code - never imported
- Deleted `game/simulation/components/abilities.py`
- Verified all imports still work from `game.simulation.components.abilities` package
- All 31 ability tests pass


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked (deferred tasks marked appropriately)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
