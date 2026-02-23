# PROJ-162: Extract CargoTransferService from UI Dialogs

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-162` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-162 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Create CargoTransferService | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Refactor Dialogs to Use Service | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Fix Input Handler & Filter Tests | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Cleanup & Verification | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-23
**Active Phase:** Phase 2 — Refactor Dialogs to Use Service
**Last Action:** Phase 1 complete — CargoTransferService created with 5 static methods
**Next Action:** Begin Phase 2 — refactor CargoQuickDialog and TransferDialog to use CargoTransferService
**Blockers:** None
**Context for Next Agent:** CargoTransferService in game/strategy/services/cargo_transfer_service.py. 22 unit tests pass. Pre-existing 12 UI test failures remain (to be fixed in Phase 2-3). Tests: 11849 passed, 12 failed (pre-existing).

## Overview
Extract shared business logic (colony resolution, population extraction, transfer command assembly) from `CargoQuickDialog` and `TransferDialog` into a `CargoTransferService` in the strategy services layer. Fix all 12 failing UI screen tests. Clean up 18 leftover DIAG log statements.

## Goals
- Fix all 12 failing tests in `tests/unit/ui/screens/`
- Extract business logic from UI dialogs into testable service
- Eliminate code duplication between CargoQuickDialog and TransferDialog
- Remove DIAG log noise from production code
- Zero regressions in the 69 passing at-risk tests

## Scope
**In:** CargoTransferService extraction, all 12 test fixes, DIAG log cleanup, input handler mock fixes, fleet report filter mock fix
**Out:** TransferDialog `_session` access fix, debug label cleanup, fleet object vs DTO inconsistency

## Key Files
| Component | File Path |
|-----------|-----------|
| New service | `game/strategy/services/cargo_transfer_service.py` |
| CargoQuickDialog | `game/ui/screens/cargo_quick_dialog.py` |
| TransferDialog | `game/ui/screens/transfer_dialog.py` |
| Input handler | `game/ui/screens/strategy_input_handler.py` |
| Fleet report filters | `game/ui/screens/fleet_report_filters.py` |
| Failing test: cargo issuance | `tests/unit/ui/screens/test_cargo_quick_dialog_issuance.py` |
| Failing test: transfer dialog | `tests/unit/ui/screens/test_transfer_dialog.py` |
| Failing test: input core | `tests/unit/ui/screens/test_strategy_input_handler_core.py` |
| Failing test: input transfer | `tests/unit/ui/screens/test_strategy_input_handler_transfer.py` |
| Failing test: fleet filters | `tests/unit/ui/screens/test_fleet_report_filters.py` |
| Reference pattern | `game/strategy/services/fleet_cargo_projector.py` |
| Services init | `game/strategy/services/__init__.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (`pytest tests/ -n 12` — 0 failures)
- [ ] Audit passed
- [ ] User verified
