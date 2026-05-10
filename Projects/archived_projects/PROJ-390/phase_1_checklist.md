# Phase 1: Migrate ~12 callers + retire module-level shim

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-390 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate all production callers of the module-level `log_event` / `set_event_handler` / `get_event_handler` functions at `event_logging.py:57-88` to an injected `EventBus`, then delete the module-level functions and the `_event_handler` global. The shim is a documented violation of session-scoped isolation.

---

## Tasks

### Task 1.1: Enumerate non-test callers
**File:** `game/`, `tests/`, `combat_lab/`, `Tools/`
**Tests:** —

- [x] Run `grep -rn -E "from game.core.event_logging import (log_event|set_event_handler|get_event_handler)" game/ combat_lab/ Tools/` to enumerate every production import (LEG-02-016 / LEG-03-021)
- [x] Run the same grep against `tests/` — these will need migration too
- [x] Record the full caller list as `event_logging_callers.md` in `Scratchpad/` so each caller can be checked off

### Task 1.2: Wire `EventBus` into ApplicationContext if not already there
**File:** `game/context.py` (or wherever EventBus is exposed today)
**Tests:** `pytest tests/ -k context`

- [x] If `EventBus` is not already an `ApplicationContext` service, add it (Pattern 1)
- [x] Confirm `ctx.event_bus` accessor exists for callers

### Task 1.3: Migrate each production caller
**File:** Each caller from Task 1.1
**Tests:** Caller-local pytest target

- [x] For each caller: replace `log_event(...)` with `ctx.event_bus.log(...)` (or whichever method matches the canonical `EventBus` API), threading `ctx` through if not already available
- [x] Verify each migrated caller: file no longer imports from `game.core.event_logging`'s module-level API

### Task 1.4: Migrate test callers
**File:** `tests/`
**Tests:** `pytest tests/ --testmon`

- [x] Replace test-side imports of the module-level functions with fixture-injected `EventBus` instances
- [x] Verify: `grep -rn "from game.core.event_logging import log_event" tests/` returns zero hits

### Task 1.5: Delete the module-level shim
**File:** `game/core/event_logging.py`
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Delete the module-level `log_event()`, `set_event_handler()`, `get_event_handler()` at lines 57-88 plus the `_event_handler` global (LEG-02-016 / LEG-03-021)
- [x] Update `docs/02_PATTERNS.md` §10 to remove the "compatibility shim" tag and reflect the canonical `EventBus`-injection pattern as the only way
- [x] Verify: pytest passes; full grep for the deleted symbols returns zero hits

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-07_220621_legacy-audit/`. See [findings/source_audit.md](findings/source_audit.md) for the link._
