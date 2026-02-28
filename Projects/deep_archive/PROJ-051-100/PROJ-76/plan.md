# PROJ-76: Empire-Wide Build Queue Window

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-76` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-76 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Data Layer | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Window Foundation | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Column System | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Filtering | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Navigation | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Multi-Select | Complete | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Integration | Complete | [phase_7_checklist.md](phase_7_checklist.md) |

## Current State
**Last Updated:** 2026-02-08
**Active Phase:** Audit Complete
**Last Action:** Audit cycle 1 passed with no significant issues. 4 investigation agents verified data layer, window implementation, test coverage, and integration.
**Next Action:** User verification required
**Blockers:** None
**Context for Next Agent:** Project is audit-complete. User needs to verify and close.

## Overview
Create a new empire-wide build queue management window that shows all space yards (planet shipyards and fleet yards) across the entire empire in a unified, filterable list. This complements the existing per-hex BuildQueueScreen by providing a high-level overview and batch operations.

## Goals
- Add a new "All Queues" button to the strategy screen top bar
- Show all space yards in a list with configurable columns
- Support filtering by location type, queue status, build capabilities, and text search
- Enable navigation to single hex build queue via row click
- Support multi-select for batch adding items to multiple queues

## Scope
**In Scope:**
- New top bar button "All Queues" (separate from existing "Build Queues")
- New window with virtual scrolling list of all space yards
- Columns: Portrait, Location Name, System, Sector, Queue Contents, Capabilities, Build Rate
- Column visibility toggle in sidebar
- Filtering: Location type (planet/fleet), queue status, capabilities, text search
- Row click navigates to hex build screen
- Multi-select with Ctrl+click for batch operations

**Out of Scope:**
- Modifying the existing BuildQueueListWindow (keep as-is)
- Complex batch operations (only add-to-queue for now)
- Column reordering (visibility toggle only in v1)
- Preset save/load (can add later)

## Key Files
| Component | File Path |
|-----------|-----------|
| BuildQueueSource | `game/strategy/data/build_queue_source.py` |
| PlanetListWindow | `game/ui/screens/planet_list_window.py` |
| BuildQueueScreen | `game/ui/screens/build_queue_screen.py` |
| StrategyUI | `game/ui/screens/strategy_ui.py` |
| StrategyScreen | `game/ui/screens/strategy_screen.py` |
| New Window | `game/ui/screens/empire_build_queue_window.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [x] All phase checklists complete
- [x] All tests passing (7111 passed, 2 pre-existing failures)
- [x] Audit passed (Cycle 1 - no significant issues)
- [ ] User verified

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | 2026-02-08 | 6 minor observations (style/coverage), no functional issues | PASSED |
