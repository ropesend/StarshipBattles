# Phase 1: Migrate callers + delete shim

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-383 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate all 31 import sites of `game.strategy.engine.command_handlers` to the canonical `game.strategy.engine.handlers/` package, then delete the 82-LOC shim file. The shim violates CLAUDE.md Rule 3 (no compatibility shims).

---

## Tasks

### Task 1.1: Migrate `planet_command_handlers.py` imports
**File:** `game/strategy/engine/planet_command_handlers.py`
**Tests:** `pytest tests/ -k planet_command_handlers`

- [x] Migrate 4 function-local imports of `BaseCommandHandler` at lines 55, 127, 149, 185 (post-merge line numbers) from `game.strategy.engine.command_handlers` to `game.strategy.engine.handlers.base` (LEG-01-015)
- [x] Verify: re-grep file for `from game.strategy.engine.command_handlers` shows zero hits

### Task 1.2: Migrate `superweapon_command_handlers.py` imports
**File:** `game/strategy/engine/superweapon_command_handlers.py`
**Tests:** `pytest tests/ -k superweapon`

- [x] Already done by PROJ-382 Phase 3 (commit `73eb2a635`). Top-level import at line 15 already reads `from game.strategy.engine.handlers.base import BaseCommandHandler, add_move_order_if_needed`. (LEG-01-016)
- [x] Verify: file no longer imports from the shim

### Task 1.3: Migrate `game_session.py` import
**File:** `game/strategy/engine/game_session.py`
**Tests:** `pytest tests/ -k game_session`

- [x] Migrate top-level import at line 67 (`create_default_registry`) from `command_handlers` to `game.strategy.engine.handlers` (LEG-01-018)
- [x] Verify: file no longer imports from the shim

### Task 1.4: Migrate 25 test-file imports
**File:** `tests/` (multiple)
**Tests:** `pytest tests/ --testmon`

- [x] Run `grep -rn "from game.strategy.engine.command_handlers" tests/` to enumerate all test-side import sites (10 files, 25 imports)
- [x] Migrate each import to the canonical `game.strategy.engine.handlers.*` path
- [x] Verify: re-grep returns zero hits in `tests/`

### Task 1.5: Delete the shim file
**File:** `game/strategy/engine/command_handlers.py`
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Delete `game/strategy/engine/command_handlers.py` (whole file, 82 LOC) (LEG-01-005)
- [x] Verify: pytest passes; no remaining imports of `game.strategy.engine.command_handlers` anywhere in repo

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-07_220621_legacy-audit/`. See [findings/source_audit.md](findings/source_audit.md) for the link._
