# PROJ-77: Event Log System

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-77` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-77 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Event Infrastructure | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. GameSession Integration | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Engine Event Emission | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Event Log UI | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Testing & Polish | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-02-08
**Active Phase:** Phase 3 - Engine Event Emission
**Last Action:** Phase 2 complete - EventLog in GameSession, save/load persistence, facade queries
**Next Action:** Begin Phase 3 - Add log_event() calls to ProductionEngine, FleetOrderProcessor, ConflictResolutionEngine
**Blockers:** None
**Context:** GameSession creates EventLog + registers handler via set_event_handler. Facade has get_turn_events/get_all_events/get_events_by_category. 24 new tests (55 total).

## Overview
Implement a comprehensive event logging system for the strategy layer that captures and displays game events (ship/complex building, colony founding, combat) in a modal window at turn start, with a button to reopen the log.

## Goals
- Capture all significant game events during turn processing
- Display events in a modal popup at the start of each turn
- Persist events with game saves (full history)
- Provide filter tabs (All, Combat, Production, Colonies)
- Add top-bar button to reopen the event log after closing

## Scope
**In Scope:**
- Event data model (Event, EventLog classes)
- Event emission from ProductionEngine, FleetOrderProcessor, ConflictResolutionEngine
- Event persistence in GameSession save/load
- Modal window UI with filter tabs
- Top bar "Log" button

**Out of Scope:**
- Detailed battle replay (just summary)
- Event notifications/popups during turn processing
- Sound effects for events
- Event export/share functionality

## Key Files
| Component | File Path |
|-----------|-----------|
| Event Types | `game/strategy/events/event_types.py` (NEW) |
| Event Model | `game/strategy/events/event_log.py` (NEW) |
| GameSession | `game/strategy/engine/game_session.py` |
| Facade | `game/strategy/facade/strategy_session_facade.py` |
| Event Window | `game/ui/screens/event_log_window.py` (NEW) |
| Strategy UI | `game/ui/screens/strategy_ui.py` |
| Strategy Screen | `game/ui/screens/strategy_screen.py` |
| Production Engine | `game/strategy/engine/production_engine.py` |
| Fleet Order Processor | `game/strategy/engine/fleet_order_processor.py` |
| Conflict Engine | `game/strategy/engine/conflict_resolution_engine.py` |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  UI LAYER                                                    │
│  StrategyScreen._process_full_turn()                        │
│    → after turn completes, show EventLogWindow              │
│  StrategyUI.btn_events (top bar button to reopen)           │
└──────────────────────────────────────┬──────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────┐
│  FACADE LAYER                                                │
│  StrategySessionFacade.get_turn_events(turn) → List[dict]   │
└──────────────────────────────────────┬──────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────┐
│  SESSION LAYER                                               │
│  GameSession._event_log: EventLog                           │
│  - Collects events via logger callback                       │
│  - Persists in to_dict() / from_dict()                      │
└──────────────────────────────────────┬──────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────┐
│  ENGINE LAYER (Event Emission via log_event())              │
│  ProductionEngine → "ship_built", "complex_built"           │
│  FleetOrderProcessor → "colony_founded"                      │
│  ConflictResolutionEngine → "combat_resolved"               │
└─────────────────────────────────────────────────────────────┘
```

## User Decisions
| Decision | Choice | Rationale |
|----------|--------|-----------|
| Display Mode | Modal popup | Non-intrusive, appears at turn start |
| Persistence | Save all events | Full history for review |
| Combat Detail | Summary only | Keep log concise |
| Filtering | Yes - tabs | User wants to filter by type |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (`pytest tests/ -n 12`)
- [ ] Audit passed
- [ ] User verified
