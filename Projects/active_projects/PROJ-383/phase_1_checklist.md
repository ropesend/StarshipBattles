# Phase 1: Migrate callers + delete shim

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-383 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate all 31 import sites of `game.strategy.engine.command_handlers` to the canonical `game.strategy.engine.handlers/` package, then delete the 82-LOC shim file. The shim violates CLAUDE.md Rule 3 (no compatibility shims).

---

## Tasks

### Task 1.1: Migrate `planet_command_handlers.py` imports
**File:** `game/strategy/engine/planet_command_handlers.py`
**Tests:** `pytest tests/ -k planet_command_handlers`

- [ ] Migrate 4 function-local imports of `BaseCommandHandler` at lines 55, 123, 145, 181 from `game.strategy.engine.command_handlers` to `game.strategy.engine.handlers.base` (LEG-01-015)
- [ ] Verify: re-grep file for `from game.strategy.engine.command_handlers` shows zero hits

### Task 1.2: Migrate `superweapon_command_handlers.py` imports
**File:** `game/strategy/engine/superweapon_command_handlers.py`
**Tests:** `pytest tests/ -k superweapon`

- [ ] Migrate top-level import at line 15 (`BaseCommandHandler`, `add_move_order_if_needed`) from `command_handlers` to `game.strategy.engine.handlers.base` (LEG-01-016)
- [ ] Verify: file no longer imports from the shim

### Task 1.3: Migrate `game_session.py` import
**File:** `game/strategy/engine/game_session.py`
**Tests:** `pytest tests/ -k game_session`

- [ ] Migrate top-level import at line 67 (`create_default_registry`) from `command_handlers` to `game.strategy.engine.handlers` (LEG-01-018)
- [ ] Verify: file no longer imports from the shim

### Task 1.4: Migrate 25 test-file imports
**File:** `tests/` (multiple)
**Tests:** `pytest tests/ --testmon`

- [ ] Run `grep -rn "from game.strategy.engine.command_handlers" tests/` to enumerate all test-side import sites
- [ ] Migrate each import to the canonical `game.strategy.engine.handlers.*` path
- [ ] Verify: re-grep returns zero hits in `tests/`

### Task 1.5: Delete the shim file
**File:** `game/strategy/engine/command_handlers.py`
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Delete `game/strategy/engine/command_handlers.py` (whole file, 82 LOC) (LEG-01-005)
- [ ] Verify: pytest passes; no remaining imports of `game.strategy.engine.command_handlers` anywhere in repo (`grep -rn "command_handlers" game/ tests/ combat_lab/ Tools/`)

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-07_220621_legacy-audit/`. See [findings/source_audit.md](findings/source_audit.md) for the link._
