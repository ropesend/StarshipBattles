# PROJ-35: Unify Fleet Movement Logic

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-35` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-35 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Preparation | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Create FleetNavigationService | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Fix Intercept Calculation | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Migrate FleetMovementEngine | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Add Consistency Tests | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Deprecate Old Classes | In Progress | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-01-27
**Active Phase:** Phase 6 - Deprecate Old Classes (pending manual verification)
**Last Action:** Phase 6 nearly complete - FleetMovementSimulator deprecated, documentation updated, all 4913 tests pass
**Next Action:** User to perform manual verification in running game, then mark project complete
**Blockers:** Manual verification requires user to test in running game

**Context for Next Agent:**
- Phase 6 progress:
  - Task 6.1 Complete: FleetMovementSimulator deprecated with DeprecationWarning
  - Task 6.2 Complete: Documentation updated (design.md, decisions.md)
  - Task 6.3 Partial: All 4913 tests pass, but manual verification pending
- Manual verification required (user must test in running game):
  - [ ] Create fleet with MOVE order, verify UI path matches actual movement
  - [ ] Create fleet with MOVE_TO_FLEET order, verify intercept works
  - [ ] Create fleet with warp-capable path, verify warp segments correct
- Once manual verification passes:
  - Update phase_6_checklist.md status to Complete
  - Update plan.md status table Phase 6 to Complete
  - Move project folder to `Projects/completed_projects/`

## Overview
Create a unified `FleetNavigationService` to replace duplicate movement logic in `FleetMovementSimulator` and `FleetMovementEngine`, ensuring UI path projection always matches actual turn execution. This fixes the "split brain" risk where the UI could show a fleet moving one way while the turn processor moves it differently.

## Goals
1. Single source of truth for navigation logic (destination, path calculation, next step)
2. UI projection guaranteed to match actual execution
3. Fix fake fleet object in intercept calculation (`id=-1` → proper NavigationState)
4. Clean separation: navigation logic vs resource consumption

## Scope
**In:**
- Create `FleetNavigationService` in `game/strategy/services/`
- Update `FleetMovementEngine` to delegate navigation
- Update `calculate_intercept_point` to accept `NavigationState`
- Update `project_fleet_path` to use new service
- Add consistency tests verifying projection = execution
- Deprecate `FleetMovementSimulator`

**Out:**
- Resource consumption logic (stays in `FleetMovementEngine`)
- Speed calculation logic (stays in `FleetMobilityService`)
- Order processing logic (stays in `FleetOrderProcessor`)
- Core pathfinding algorithms (stay in `pathfinding.py`)

## Architecture

```
FleetNavigationService (new - single source of truth)
├── Core (stateless, pure functions):
│   ├── get_destination(state, order, galaxy) → HexCoord?
│   ├── compute_path(state, destination, galaxy) → [HexCoord]
│   └── compute_next_step(state, galaxy) → NavigationStep
├── Projection (for UI):
│   ├── project_path(fleet, galaxy, max_turns) → [PathSegment]
│   └── project_path_as_dicts(fleet, galaxy) → [dict]
└── Execution (for TurnEngine):
    └── calculate_fleet_next_hex(fleet, galaxy) → HexCoord?
        (wrapper that applies state changes to mutable Fleet)

FleetMovementEngine (simplified - delegates navigation)
├── collect_movements(empires, galaxy, tick) → [(Fleet, HexCoord)]
├── apply_movement(fleet, next_hex, galaxy) → MovementResult
└── apply_movements(queue, galaxy) → [MovementResult]
    (retains ALL resource consumption logic)
```

## Key Files
| Component | File Path | Action |
|-----------|-----------|--------|
| Navigation Service | `game/strategy/services/fleet_navigation_service.py` | CREATE |
| Movement Engine | `game/strategy/engine/fleet_movement_engine.py` | UPDATE (delegate) |
| Pathfinding | `game/strategy/data/pathfinding.py` | UPDATE (intercept, project) |
| Movement Simulator | `game/strategy/engine/fleet_movement.py` | DEPRECATE |
| Service Tests | `tests/unit/strategy/test_fleet_navigation_service.py` | CREATE |
| Consistency Tests | `tests/strategy/test_fleet_navigation_consistency.py` | CREATE |

## Duplicated Logic to Consolidate
1. **Destination calculation** for MOVE and MOVE_TO_FLEET orders (lines 73-89 vs 69-82)
2. **Path recalculation** when destination changes (lines 152-155 vs 85-88)
3. **Path popping** logic - taking next step from path (lines 176-178 vs 109-111)
4. **Warp detection** - `hex_distance > 1` (line 269 vs 139)
5. **Order completion** logic - when to pop order (lines 181-184 vs 166-167)

## Related Documents
- [design.md](design.md) - Architecture analysis and swarm findings
- [decisions.md](decisions.md) - Full decisions log

## Verification Checklist
### Project Start
- [x] `pytest tests/` - all pass (baseline) - **4594 passed, 1 skipped**

### After Each Phase
- [x] `pytest tests/ --testmon` - affected tests pass (Phase 2: 36 passed)
- [x] `pytest tests/ --testmon` - affected tests pass (Phase 3: 91 pathfinding + navigation tests)

### Final Verification
- [ ] `pytest tests/` - full suite passes
- [ ] Manual test: Fleet with MOVE order - UI path matches actual movement
- [ ] Manual test: Fleet with MOVE_TO_FLEET order - intercept works correctly
- [ ] Manual test: Fleet with warp-capable path - warp segments render correctly
- [ ] All phase checklists complete
- [ ] Audit passed
- [ ] User verified

## Related Projects
- PROJ-12: Decomposed TurnEngine god class (extracted FleetMovementEngine)
- BUG-45: Warp capability debugging (referenced in game_session.py)
