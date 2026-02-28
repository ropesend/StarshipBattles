# Phase 2: Logger Core Migration (Event System + Core + Simulation)

**Goal:** Create the event logging module, migrate `game/core/` and `game/simulation/` from custom Logger to standard `logging.getLogger(__name__)`, and update test infrastructure.

**Estimated effort:** 4-6 hours
**Risk:** MEDIUM — creates new event module, migrates foundation modules, updates test config

## Pre-Phase
- [ ] Phase 1 must be complete
- [ ] Run full test suite, record baseline: `pytest tests/ -n 12`
- [ ] Read `game/core/logger.py` completely
- [ ] Search for all event handler usage: `grep -rn "log_event\|set_event_handler" game/ tests/ simulation_tests/ --include="*.py"`
- [ ] Search for `set_logging` usage: `grep -rn "set_logging" game/ tests/ --include="*.py"`

## Task 1: Create event_logging.py
- [ ] Create `game/core/event_logging.py` with:
  - `set_event_handler(handler)` function
  - `get_event_handler()` function
  - `log_event(event_type, **kwargs)` function
  - Standard logging for error reporting (`logger = logging.getLogger(__name__)`)
  - See design.md for full implementation
- [ ] Write unit test for event_logging module (set handler, fire event, verify callback)
- [ ] Write test for exception isolation (handler that raises, verify caller doesn't crash)
- [ ] Run new tests: `pytest tests/ -k event_logging`

## Task 2: Update conftest.py and test infrastructure
- [ ] Read root `conftest.py` — find all Logger-related setup/teardown
- [ ] Replace `Logger.reset()` / `set_event_handler(None)` with:
  - Session-scoped fixture: add NullHandler to `logging.getLogger("game")`
  - Function-scoped fixture: `set_event_handler(None)` from `game.core.event_logging`
- [ ] Search test files for `from game.core.logger import`: update imports to use event_logging for event functions
- [ ] Run full test suite: `pytest tests/ -n 12`

## Task 3: Update app.py (root logger configuration)
- [ ] Read `game/app.py` — find existing logging setup
- [ ] Add `configure_logging()` function (see design.md)
- [ ] Call `configure_logging()` early in app startup
- [ ] Ensure it creates `Paths.BATTLE_LOG` file handler with proper format
- [ ] Migrate any `from game.core.logger import` to standard logging
- [ ] Run: `pytest tests/ -k app -n 4`

## Task 4: Migrate game/core/ (~6 files)

**Per-file pattern:**
```python
# BEFORE
from game.core.logger import log_info, log_error, log_warning, log_debug

# AFTER
import logging
logger = logging.getLogger(__name__)
# log_info(msg) → logger.info(msg), etc.
```

**Files to migrate:**
- [ ] `game/core/json_utils.py` — replace `log_error`, `log_debug` → `logger.error`, `logger.debug`
- [ ] `game/core/profiling.py` — replace custom logger calls
- [ ] `game/core/resources.py` — replace custom logger calls
- [ ] `game/core/__init__.py` — remove logger imports if present
- [ ] `game/core/exceptions.py` — replace custom logger calls if present
- [ ] Any other core/ file found importing from logger
- [ ] Run: `pytest tests/ -k core -n 4`

## Task 5: Migrate game/simulation/ (~16 files)

**Files to migrate (from census):**
- [ ] `game/simulation/entities/ship.py` (12 calls)
- [ ] `game/simulation/entities/projectile.py` (3 calls)
- [ ] `game/simulation/entities/ship_serialization.py` (13 calls)
- [ ] `game/simulation/entities/ship_loader.py` (2 calls)
- [ ] `game/simulation/formula_system.py` (3 calls)
- [ ] `game/simulation/projectile_manager.py` (2 calls)
- [ ] `game/simulation/battle_state.py` (1 call)
- [ ] `game/simulation/systems/battle_engine.py` (5 calls)
- [ ] `game/simulation/services/registry_loader.py` (8 calls)
- [ ] `game/simulation/services/design_loader.py` (6 calls)
- [ ] `game/simulation/services/battle_service.py` (2 calls)
- [ ] `game/simulation/managers/retreat_manager.py` (4 calls)
- [ ] `game/simulation/components/component.py` (16 calls)
- [ ] `game/simulation/components/abilities/__init__.py` (1 call)
- [ ] `game/simulation/components/abilities/weapons.py` (2 calls)
- [ ] `game/simulation/battle_controller.py` (7 calls)

**Dual-usage files (also have standard logging — just remove custom imports):**
- [ ] `game/simulation/components/modifier_effects.py` — remove custom logger import, keep stdlib
- [ ] `game/simulation/components/modifiers.py` — remove custom logger import, keep stdlib

- [ ] Run simulation tests: `pytest tests/unit/simulation/ -n 4`
- [ ] Run simulation_tests: `pytest simulation_tests/ -n 4`

## Verification
- [ ] Verify no core/ imports from logger: `grep -rn "from game.core.logger" game/core/ --include="*.py"` returns nothing
- [ ] Verify no simulation/ imports from logger: `grep -rn "from game.core.logger" game/simulation/ --include="*.py"` returns nothing
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Confirm zero regressions vs. baseline

## Completion Checklist
- [ ] `game/core/event_logging.py` created and tested
- [ ] `conftest.py` updated (no Logger.reset, uses event_logging)
- [ ] `game/app.py` has root logger configuration
- [ ] All game/core/ files migrated to standard logging
- [ ] All game/simulation/ files migrated to standard logging
- [ ] Dual-usage files cleaned up (modifier_effects.py, modifiers.py)
- [ ] All tests pass
- [ ] Update plan.md Phase 2 status to "Complete"
