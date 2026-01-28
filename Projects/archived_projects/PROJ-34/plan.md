# PROJ-34: StrategyScene Strict Facade Refactor

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-34` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-34 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Foundation - DTOs and Facade Structure | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Commands and Handlers | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Facade Query Implementation | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. UI Module Refactoring | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Cleanup and Documentation | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Audit Fixes (Cycle 1) | Complete | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-01-27
**Active Phase:** Audit Complete - Ready for User Verification
**Last Action:** Audit cycle 2 passed. Verified Phase 6 fixes (FleetInfo immutability), facade pattern implementation, and all command handlers.
**Next Action:** User verification required (manual playtest)
**Blockers:** None

**Key Accomplishments:**
- Full CQRS-lite facade pattern implemented with truly immutable DTOs
- 7 command types with handlers in GameSession
- FleetOperations and ColonizationSystem fully refactored to use facade
- 40 new facade-related tests (31 unit + 9 integration)
- Bug fix: `planet=None` support in colonize mission (user testing found this)
- Audit fix: FleetInfo now uses Tuple instead of List for collection fields
- 4863 tests passing

## Overview
Refactor `StrategyScene` and its extracted modules to use a **Strict Facade with CQRS-lite pattern**. The UI layer will communicate with the game engine exclusively through a `StrategySessionFacade` class, eliminating direct access to session internals and state mutations.

**Origin:** Code Review finding - "Logic Leaking into UI (StrategyScene)" - High Severity

## Goals
- Enforce strict separation between UI and business logic
- All state mutations go through Commands (write path)
- All reads return immutable DTOs (read path) - never domain objects
- Create portable API boundary for future language port
- Improve testability via facade mocking

## Scope
**In Scope:**
- Create `StrategySessionFacade` class with Query + Command methods
- Create DTO classes (`FleetInfo`, `SystemInfo`, `PlanetInfo`, `EmpireInfo`)
- Add new command types (`IssueInterceptCommand`, `IssueJoinFleetCommand`, `QueueColonizeMissionCommand`, `ClearFleetOrdersCommand`)
- Refactor `StrategyScene` and all extracted modules to use facade exclusively
- Add command handlers to `GameSession`

**Out of Scope:**
- Event/observer system for state change notifications (future enhancement)
- Undo/redo command history (future enhancement)
- `FleetOrdersWindow` refactoring (can be added as bonus phase)

## Key Files
| Component | File Path | Purpose |
|-----------|-----------|---------|
| GameSession | `game/strategy/engine/game_session.py` | Core domain class - add command handlers |
| Commands | `game/strategy/engine/commands.py` | Command definitions - extend |
| StrategyScene | `game/ui/screens/strategy_scene.py` | Main UI coordinator - refactor |
| FleetOperations | `game/ui/screens/strategy_fleet_ops.py` | Fleet movement - refactor |
| ColonizationSystem | `game/ui/screens/strategy_colonization.py` | Colonization workflow - refactor |
| InputHandler | `game/ui/screens/strategy_input_handler.py` | Input routing - minor updates |
| CameraNavigator | `game/ui/screens/strategy_camera_nav.py` | Camera control - minor updates |
| Fleet | `game/strategy/data/fleet.py` | Domain model - reference for DTOs |
| ValidationResult | `game/core/validation.py` | Existing validation pattern |

## Coupling Issues to Fix
| File | Line(s) | Issue | Severity |
|------|---------|-------|----------|
| `strategy_colonization.py` | 88 | Calls `turn_engine.validate_colonize_order()` directly | High |
| `strategy_colonization.py` | 197-206 | Direct `fleet.add_order()` and `fleet.path` mutation | High |
| `strategy_fleet_ops.py` | 136-137 | Direct `fleet.add_order()` for intercept | Medium |
| `strategy_fleet_ops.py` | 176-180 | Direct `fleet.add_order()` for join | Medium |
| `strategy_scene.py` | 94-126 | 9 property delegations exposing session internals | Medium |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-27 | Use Strict Facade (not Commands-Only) | Better portability for future language port; creates clear API contract |
| 2026-01-27 | Add all new command types | Complete command coverage for all UI operations |
| 2026-01-27 | Keep turn processing as direct call | It's a lifecycle event, not a player action |
| 2026-01-27 | Use frozen dataclasses for DTOs | Immutability prevents UI from accidentally mutating state |

## Architecture Diagram
```
StrategyScene (UI)
       │
       └─── StrategySessionFacade
                    │
       ┌───────────┴───────────┐
       │                       │
   Commands                 Queries
   (mutations)            (DTOs only)
       │                       │
       ▼                       ▼
  GameSession             GameSession
  handle_command()        (read state)
       │                       │
       ▼                       ▼
  Domain Objects          DTO Factory
  (Fleet, Empire)         (FleetInfo, etc.)
```

## Verification
- [x] Baseline test suite passing (4594 passed, 1 skipped)
- [x] All phase checklists complete (6 phases)
- [x] All tests passing after refactor (4863 passed, 1 skipped)
- [x] Code review passed (grep searches confirm in-scope modules refactored)
- [x] Audit passed (cycle 2 - no significant issues)
- [ ] User verified (manual playtest pending)

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | 2026-01-27 | 1 major issue: FleetInfo has mutable List fields breaking immutability | Added Phase 6 for fixes |
| 2 | 2026-01-27 | No significant issues. Verified: FleetInfo immutability fix, facade pattern in UI, command handlers complete. Minor gaps in test coverage noted but not blocking. | PASSED |
