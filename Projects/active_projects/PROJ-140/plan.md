# PROJ-140: Colony Ship Colonization Validation

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-140` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-140 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Fix Execution-Time Validation (Bugs 1+2) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Fix "Any Planet" Validation (Bug 5) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Fix UI Designation Filtering (Bug 3) | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Fix Mission Command Handler (Bug 4) | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Full Regression + Cleanup | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-02-13
**Active Phase:** Phase 4 Complete — Phase 5 Next
**Last Action:** Phase 4 complete: Fixed ColonizeMissionCommandHandler pod validation (Bug 4)
**Next Action:** Begin Phase 5 - Full Regression + Cleanup
**Blockers:** None
**Context for Next Agent:** Phase 4 complete with 11957 tests passing (+5 from Phase 3). Fixed: ColonizeMissionCommandHandler.execute() now validates pod match before queuing orders - checks find_ship_with_colony_pod and get_committed_colony_pods. Also updated 4 integration tests to include colony ships with matching pods.

## Overview

Colony ships of the wrong type can colonize planets, and when they do, the ships are not destroyed. The colonization system has validation at the UI layer (PROJ-55) but critical gaps at the execution and command layers allow mismatched colony pods to succeed silently. This project closes those gaps at every layer: UI filtering, command validation, and execution-time enforcement.

## Goals
- Colony pod type must match planet type for colonization to succeed — at every layer
- Colony ship must always be consumed when colonization succeeds
- UI must not allow targeting planets without matching colony pods
- Colonization orders must not be queued without matching pod validation
- "Any Planet" colonization must select a planet matching an available pod

## Scope
**In:**
- Fix `process_colonize()` to pass `component_registry` to validator (Bug 1)
- Restructure `process_colonize()` to pre-check ship before mutation (Bug 2)
- Add pod filtering to `handle_colonize_designation()` (Bug 3)
- Add pod validation to `ColonizeMissionCommandHandler` (Bug 4)
- Fix "Any Planet" validation to check pod availability (Bug 5)

**Out:**
- COLONIZE order serialization bug (Planet targets stored as `fleet_ref` in FleetOrder.to_dict)
- Save/load round-tripping of COLONIZE orders
- UI feedback improvements (better error messages, planet type indicators)

## Key Files
| Component | File Path |
|-----------|-----------|
| Execution | `game/strategy/engine/fleet_order_processor.py` |
| Validation | `game/strategy/validation/colonize_validator.py` |
| UI Handler | `game/ui/screens/strategy_colonization.py` |
| Command Handler | `game/strategy/engine/command_handlers.py` |
| Turn Engine | `game/strategy/engine/turn_engine.py` |
| Facade | `game/strategy/facade/strategy_session_facade.py` |
| Test Fixtures | `tests/integration/colonization/test_planet_specific_colonization.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis, swarm findings, and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (`pytest tests/ -n 12`)
- [ ] Every code path that creates a colony validates pod match
- [ ] Every successful colonization removes the colony ship
- [ ] UI prevents targeting planets without matching pods
- [ ] Audit passed
- [ ] User verified
