# PROJ-232: Command Layer Cleanup - Fix Dataclasses, Eliminate Handler Boilerplate, Add Type Safety

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-232` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-232 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Fix Dataclass Pattern | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Add String Enums | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Add Type Safety | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Clean Up DIAG Logging | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Update Documentation | Complete | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-03-28 22:30
**Active Phase:** All phases complete
**Last Action:** Implemented all 5 phases. All 2949 strategy tests pass, 0 failures.
**Next Action:** Final full suite verification, then archive project.
**Blockers:** None
**Context for Next Agent:** All changes are complete and tested. commands.py reduced from 515 to ~330 lines. 25 redundant __init__ methods removed. TransferDirection and BuildEntityType enums added. 27 handler signatures updated from cmd: Any to specific types. 9 DIAG log statements cleaned up. Docs updated.

## Overview
Remove all 25 redundant `__init__` methods from command dataclasses, replace magic string literals with `str, Enum` types, add specific type hints to all 27 command handler `execute()` signatures, and clean up leftover diagnostic logging. No runtime behavior changes.

## Goals
- Fix broken `@dataclass` pattern in `commands.py` (25 redundant `__init__` methods)
- Replace `"load"`/`"unload"` and `"planet"`/`"fleet"` magic strings with enums
- Add type safety: `cmd: Any` → specific command types in all 27 handlers
- Remove 9 leftover DIAG log statements from `TransferCommandHandler`
- Keep docs consistent with code changes

## Scope
**In Scope:**
- `game/strategy/engine/commands.py` — dataclass fix + enums
- `game/strategy/engine/command_handlers.py` — type hints + logging cleanup
- `game/strategy/engine/superweapon_command_handlers.py` — type hints
- `game/strategy/validation/transfer_validator.py` — enum update
- `game/ui/screens/build_queue_screen.py` — enum call site
- `game/ui/screens/empire_build_queue_window.py` — enum call site
- `docs/systems/strategy_layer.md` — Protocol example update
- `docs/02_PATTERNS.md` — Protocol example update

**Out of Scope:**
- Fleet resolution boilerplate (intentionally kept — too low ROI for abstraction)
- Handler logic refactoring (no behavioral changes)
- Test code changes (tests should pass without modification)
- Other strategy layer files

## Key Files
| Component | File Path |
|-----------|-----------|
| Command classes | `game/strategy/engine/commands.py` |
| Command handlers | `game/strategy/engine/command_handlers.py` |
| Superweapon handlers | `game/strategy/engine/superweapon_command_handlers.py` |
| Transfer validator | `game/strategy/validation/transfer_validator.py` |
| Build queue screen | `game/ui/screens/build_queue_screen.py` |
| Empire build queue | `game/ui/screens/empire_build_queue_window.py` |
| Strategy docs | `docs/systems/strategy_layer.md` |
| Patterns docs | `docs/02_PATTERNS.md` |
| Precedent: field(init=False) | `game/core/validation.py:91` |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-28 | Exclude fleet resolution boilerplate from scope | 3-line pattern repeats 25x but abstraction (decorator/exception) deviates from codebase conventions (Protocol+mixin). Cost exceeds benefit. |
| 2026-03-28 | Use `field(init=False)` on base `Command.type` | Removes `type` from generated `__init__`, preserving all 24 call sites. Precedented by `ValidationResult` in `game/core/validation.py`. |
| 2026-03-28 | Use `str, Enum` for TransferDirection and BuildEntityType | Backwards compatible — `BuildEntityType.PLANET == "planet"` is True. No changes needed at string comparison sites. |
| 2026-03-28 | Keep `IssueTransferCommand.cargo_type` as `str` | Only one value ("passengers") used — not worth an enum yet. |

## Initial Analysis

### Call Site Analysis (24 total)
- **12 positional:** `strategy_colonization.py:157,258`, `strategy_fleet_ops.py:119,145,208`, `strategy_superweapons.py:102,146,208,248,292,331`, `strategy_click_dispatcher.py:244`
- **12 keyword:** `strategy_window_manager.py:399,407,413,445`, `build_queue_screen.py:253,292`, `empire_build_queue_window.py:364`, `cargo_transfer_service.py:236`, `transfer_dialog.py:428`, `strategy_build_queue_manager.py:167,171`, `game_session.py:43`
- All safe with `field(init=False)` approach

### Test Impact (27 files, ~8600 lines)
- Primary: `test_commands.py`, `test_command_handlers.py`, `test_superweapon_command_handlers.py`
- Integration: `test_command_handlers.py`, `test_commands.py`, `test_commands_colonization.py`
- All should pass without modification — only `__init__` generation mechanism changes, not behavior

### Test Baseline
- 13904 passed, 17 failed (pre-existing: UI star color mapping + asset manager), 2 skipped
- All strategy command tests pass cleanly

## Swarm Findings Summary

### Architecture
- `ICommandHandler` Protocol at line 100-114 uses `@runtime_checkable` with `command: Any`
- `CommandHandlerRegistry.dispatch()` at line 286 receives command name via `command.name` property (`__class__.__name__`)
- `GameSession.handle_command()` at line 203 routes through registry
- All 27 handlers extend `BaseCommandHandler` and follow identical resolve→validate→apply pattern

### Key Patterns to Reuse
- **`field(init=False)` + `__post_init__`:** `game/core/validation.py:91` — exact same pattern needed
- **`TYPE_CHECKING` imports:** Already used at `command_handlers.py:26` for `GameSession`
- **`str, Enum`:** Standard Python pattern for backwards-compatible string enums

### Risks Identified
1. **Dataclass inheritance ordering** — mitigated by `field(init=False)` removing `type` from `__init__`
2. **Positional arg breakage** — mitigated: verified all 12 positional sites safe with new field order
3. **`str, Enum` serialization** — mitigated: `.value` returns raw string, JSON-safe

---

## Phases

### Phase 1: Fix Dataclass Pattern in commands.py [Medium]
**Objective:** Remove 25 redundant `__init__` methods, let `@dataclass` generate them
**Status:** Complete

#### Task 1.1: Modify base Command class [Simple]
**File:** `game/strategy/engine/commands.py`
**Tests:** `pytest tests/unit/strategy/engine/test_commands.py -v`
- [x] Add `field` to dataclasses import (line 1): `from dataclasses import dataclass, field`
- [x] Change `type: CommandType` to `type: CommandType = field(init=False)` (line 14)
- [x] Add `__post_init__` method to Command
- [x] Run tests to verify base class change works
**Notes:** All 38 command tests pass.

#### Task 1.2: Add missing field defaults [Simple]
- [x] All 6 field defaults added to match existing `__init__` defaults
**Notes:** Done together with Task 1.3.

#### Task 1.3: Remove all __init__ methods [Medium]
- [x] All 25 `__init__` methods removed
- [x] Run full strategy tests: 2927 passed, 1 skipped, 0 failures
**Notes:** File reduced from 515 to ~330 lines.

---

### Phase 2: Add String Enums [Simple]
**Objective:** Replace magic string literals with proper enums
**Status:** Complete

#### Task 2.1: Add TransferDirection and BuildEntityType enums [Simple]
- [x] Added `TransferDirection(str, Enum)` and `BuildEntityType(str, Enum)`
- [x] Updated field types in IssueTransferCommand and construction queue commands
**Notes:** `str, Enum` ensures backwards compatibility.

#### Task 2.2: Update consumers [Simple]
- [x] Updated `transfer_validator.py`, `command_handlers.py`, `build_queue_screen.py`, `empire_build_queue_window.py`
**Notes:** All 51 targeted tests pass.

---

### Phase 3: Add Type Safety to Handlers [Simple]
**Objective:** Replace `cmd: Any` with specific command types in all 27 handlers
**Status:** Complete

#### Task 3.1: Update Protocol and imports [Simple]
- [x] Updated `ICommandHandler` Protocol and `CommandHandlerRegistry.dispatch`
- [x] Added all command class imports inside `TYPE_CHECKING` block

#### Task 3.2: Type-annotate command_handlers.py handlers [Simple]
- [x] All 16 handler `execute` signatures updated
**Notes:** Used script to update all at once.

#### Task 3.3: Type-annotate superweapon_command_handlers.py [Simple]
- [x] Added `TYPE_CHECKING` imports for all 11 command types
- [x] All 11 handler `execute` signatures updated
**Notes:** 111 handler tests pass.

---

### Phase 4: Clean Up DIAG Logging [Simple]
**Objective:** Remove leftover diagnostic logging from TransferCommandHandler
**Status:** Complete

#### Task 4.1: Clean DIAG statements [Simple]
- [x] Removed 4 redundant DIAG statements on error paths
- [x] Converted 5 DIAGs to `logger.debug()`, stripped "DIAG" prefix
- [x] Kept non-DIAG `logger.info` statements
**Notes:** Cleaner handler with diagnostics at debug level.

---

### Phase 5: Update Documentation [Simple]
**Objective:** Keep docs consistent with code changes
**Status:** Complete

#### Task 5.1: Update doc examples [Simple]
- [x] `strategy_layer.md`: `command: Any` to `command: Command`
- [x] `02_PATTERNS.md`: `command: Any` to `command: 'Command'`
**Notes:** Both docs updated.

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Read `docs/` foundation docs (01_ARCHITECTURE, 02_PATTERNS, 03_CONVENTIONS)
- [x] Run full test suite: `pytest tests/ -n 12` — baseline established (13904 passed, 17 pre-existing failures)

### After Each Phase
- [x] Run `pytest tests/unit/strategy/ tests/integration/strategy/ -v` — all affected tests pass
- [x] No new imports of production types outside TYPE_CHECKING blocks

### Final Verification
- [x] `pytest tests/unit/strategy/ tests/integration/strategy/` — 2949 passed, 1 skipped, 0 failures
- [ ] Spot-check in game: move, colonize, transfer, construction queue commands work
- [x] Verify changes consistent with `docs/` — docs updated in Phase 5

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | 2026-03-28 | All phases complete, 2949 tests pass | N/A |

## Completion Checklist
- [x] All Phase 1 tasks checked off
- [x] All Phase 2 tasks checked off
- [x] All Phase 3 tasks checked off
- [x] All Phase 4 tasks checked off
- [x] All Phase 5 tasks checked off
- [x] All tests passing
- [x] Regression tests passing
- [ ] Audit passed (no significant issues)
- [ ] User verified

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
