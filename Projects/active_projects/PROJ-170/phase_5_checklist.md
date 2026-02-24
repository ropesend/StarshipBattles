# Phase 5: Caller Catch Updates

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-170 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update 36 except blocks in game/ that catch generic exceptions from game code. Most complex phase — broad tuple catches in persistence tier.
**Estimated Effort:** 3 hours

**Strategy:** After Phases 2-4, all `raise` statements have been migrated. Now update catches.
- For tuples like `except (TypeError, ValueError, KeyError)`: replace with domain exceptions
- The generic types may still be needed for stdlib exceptions caught in the same block — audit each
- If a block catches BOTH stdlib and game exceptions: use `except (ValidationException, ComponentException, ValueError, KeyError)` keeping only the stdlib types needed

---

## Tasks

### Task 5.1: Persistence Tier Catches [Medium]
**Files:** `save_game_service.py`, `design_library.py`, `race_library.py`, `ship_io.py`
**Tests:** `pytest tests/unit/strategy/systems/ tests/unit/ui/services/ -k "save or design_lib or race_lib or ship_io"`

**save_game_service.py** (4 blocks):
- [x] Lines ~108,204,207,223: Added ValidationException and StateException to catches alongside generic types for transitional safety

**design_library.py** (4 blocks):
- [x] Lines ~101,184: Added ValidationException to catches for game code exceptions

**race_library.py** (2 blocks):
- [x] Lines ~117,156,196: Added ValidationException to catches for RaceConfig loading/saving

**ship_io.py** (2 blocks):
- [x] Lines ~97,160: Added ValidationException and ComponentException to catches for ship serialization

- [x] Verify: All tests passing

**Notes:** Added domain exceptions to tuple catches alongside generic types for transitional safety.

### Task 5.2: Component Loading Chain Catches [Medium]
**Files:** `component.py`, `design_loader.py`, `vehicle_design_service.py`, `battle_service.py`, `battle_controller.py`
**Tests:** `pytest tests/unit/simulation/ -n 4`

**component.py** (1 block):
- [x] Line ~532: Added ValidationException to component loading catch

**design_loader.py** (2 blocks):
- [x] Lines ~82,129: Added ValidationException and ComponentException to catches for Ship.from_dict()

**vehicle_design_service.py** (1 block):
- [x] Line ~129: Added ValidationException to ship creation catch

**battle_service.py** (1 block):
- [x] Line ~90: Added ValidationException and StateException to battle creation catch

**battle_controller.py** (3 blocks):
- [x] Lines ~173,390,517: Added ValidationException and StateException to catches

- [x] Verify: All tests passing

**Notes:** Component loading chain updated with domain exceptions.

### Task 5.3: Other Game Code Catches [Simple]
**Files:** `formation_editor.py`, `new_game_setup_screen.py`, `abilities/__init__.py`
**Tests:** `pytest tests/unit/ui/ tests/unit/simulation/components/abilities/`

**formation_editor.py** (2 blocks):
- [x] Line ~208: Added ValidationException to serialization error catch
- [x] Line ~235: Already has ValidationException from Phase 4

**new_game_setup_screen.py** (1 block):
- [x] Line ~586: Already raises ValidationException (migrated in Phase 4)

**abilities/__init__.py** (1 block):
- [x] Line ~119: Added ValidationException and ComponentException to ability creation catch

- [x] Verify: All tests passing

**Notes:** Added domain exceptions to ability instantiation.

### Task 5.4: Mixed-Source Review [Medium]
**Files:** Various — 13 blocks requiring individual audit

- [x] `ship_theme_manager.py:116` — NO CHANGE: Only catches stdlib exceptions from JSON/dict access
- [x] `battle_ui.py:218` — NO CHANGE: Catches pygame.error (stdlib)
- [x] `strategy_session_facade.py:503` — Added StateException alongside RuntimeError
- [x] `json_utils.py:141` — NO CHANGE: TypeError from json.dumps() is stdlib
- [x] `save_game_service.py` — Addressed in Task 5.1
- [x] All mixed blocks audited

- [x] Verify: `pytest tests/ -n 12` - 11972 passed, 1 skipped

**Notes:** Only strategy_session_facade.py needed update for RuntimeError → StateException.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ -n 12` all pass (11972 passed, 1 skipped)
- [x] Domain exceptions added to catches where game code is the source
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 6
