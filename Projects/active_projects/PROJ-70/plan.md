# PROJ-70: Fleet Details Panel Enhancement

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-70` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-70 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Write Tests (TDD) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Enhance format_fleet_info() | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Wire Up strategy_ui.py | Complete | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-02-07
**Active Phase:** All phases complete - ready for audit
**Last Action:** Phase 3 complete - Replaced inline fleet code in strategy_ui.py with format_fleet_info() call, removed OrderType import
**Next Action:** Trigger audit (Protocol 04)
**Blockers:** None
**Context for Next Agent:** All 3 phases complete. strategy_ui.py now calls format_fleet_info() instead of inline fleet formatting (22 lines → 1 line). OrderType import removed. 6587 tests pass (1 pre-existing failure in test_protocols.py).

## Overview
Enhance the Fleet Details panel in the strategy screen sidebar to show: travel range (hex/turn + fuel endurance), condensed ship list grouped by design sorted by mass, aggregated cargo list, and current orders. Also consolidates duplicated fleet formatting code.

## Goals
- Show total hex travel range (speed + fuel endurance) in fleet detail panel
- Show scrollable condensed ship list grouped by design (e.g., "Devastator x 3"), sorted by mass descending
- Show aggregated cargo list with quantities
- Show current orders in execution order
- Consolidate duplicated fleet formatting code into single `format_fleet_info()` function

## Scope
**In:**
- Enhance `format_fleet_info()` in `strategy_detail_fmt.py` with 4 sections
- Add helper functions for ship grouping, cargo aggregation, order formatting
- Replace inline fleet code in `strategy_ui.py` with call to `format_fleet_info()`
- Unit tests for all new formatting functions

**Out:**
- No FleetReportPanel class (overkill for HTML text display)
- No layout changes to the detail panel (UITextBox already scrollable)
- No changes to Fleet or ShipInstance data models
- No fixes to cargo asymmetry bugs (separate issue)

## Key Files
| Component | File Path |
|-----------|-----------|
| Fleet formatter | `game/ui/screens/strategy_detail_fmt.py` |
| Strategy UI | `game/ui/screens/strategy_ui.py` |
| Fleet model | `game/strategy/data/fleet.py` |
| Ship model | `game/strategy/data/ship_instance.py` |
| Tests | `tests/unit/ui/screens/test_fleet_detail_fmt.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (`pytest tests/ -n 12`)
- [ ] Manual test: Select fleet on strategy screen, verify all 4 sections display
- [ ] User verified
