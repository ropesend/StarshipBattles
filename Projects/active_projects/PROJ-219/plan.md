# PROJ-219: Fleet Registration Consolidation

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-219` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-219 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Core Empire Changes | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Wire Up Galaxy References | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Remove Redundant Calls | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Integration Tests | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Cleanup | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-03-01
**Active Phase:** Phase 2 - Wire Up Galaxy References
**Last Action:** Phase 1 complete: _galaxy, set_galaxy(), add_fleet(), remove_fleet() updated with auto-register/unregister
**Next Action:** Begin Phase 2: Wire up galaxy references in GameInitializer and GameSession
**Blockers:** None
**Test Baseline:** 13152 passed, 1 skipped
**Context for Next Agent:** Empire now has _galaxy field + set_galaxy() + auto-register/unregister in add_fleet/remove_fleet. 7 new tests in test_empire_fleet_registration.py. Phase 2 wires galaxy refs in GameInitializer.initialize() and GameSession.from_dict().

## Overview

Fleet registration with the galaxy registry is currently scattered across multiple files with no enforcement mechanism. When a fleet is created, two separate calls are required: `empire.add_fleet(fleet)` for ownership and `galaxy.register_fleet(fleet)` for O(1) lookup. This two-step ritual is error-prone - PROJ-216 found 3 locations where registration was missing.

Additionally, swarm analysis discovered **7 locations with missing unregistration** (plus 1 with explicit unregister that becomes redundant), causing "ghost fleets" to remain in the registry after destruction.

This project consolidates all registration/unregistration into `Empire.add_fleet()` and `Empire.remove_fleet()`.

## Goals

1. **Single-point registration**: `empire.add_fleet(fleet)` automatically calls `galaxy.register_fleet(fleet)`
2. **Single-point unregistration**: `empire.remove_fleet(fleet)` automatically calls `galaxy.unregister_fleet(fleet)`
3. **Fix ghost fleet bugs**: All 8 locations calling `remove_fleet()` now work correctly (7 missing unregistration + 1 redundant explicit call)
4. **Cleanup**: Remove redundant registration calls and PROJ-216 diagnostic logging

## Scope

**In:**
- Add `_galaxy` back-reference to Empire class
- Add `set_galaxy()` method for late binding
- Modify `add_fleet()` and `remove_fleet()` to auto-register/unregister
- Wire up galaxy references in GameInitializer and GameSession
- Remove redundant `galaxy.register_fleet()` calls in production_engine, command_handlers
- Remove explicit `galaxy.unregister_fleet()` in superweapon_processor (now automatic)
- Add unit and integration tests for fleet lifecycle
- Remove PROJ-216 diagnostic logging

**Out:**
- Changing Fleet class to hold galaxy reference
- Modifying deserialization to auto-register (keep explicit for clarity)
- Adding `restore_fleet()` method to GalaxyEntityRegistry (not needed)

## Key Files

| Component | File Path | Changes |
|-----------|-----------|---------|
| Empire | `game/strategy/data/empire.py` | Add `_galaxy`, `set_galaxy()`, modify `add_fleet()`/`remove_fleet()` |
| GameInitializer | `game/strategy/engine/game_initializer.py:45-55` | Call `set_galaxy()` after empire creation |
| GameSession | `game/strategy/engine/game_session.py:339-357` | Call `set_galaxy()` after deserialization |
| ProductionEngine | `game/strategy/engine/production_engine.py:641-643` | Remove redundant `galaxy.register_fleet()` |
| CommandHandlers | `game/strategy/engine/command_handlers.py:692` | Remove redundant `galaxy.register_fleet()` |
| SuperweaponProcessor | `game/strategy/engine/superweapon_order_processor.py:239` | Remove explicit `unregister_fleet()` |

## Bug Fixes (Automatic via remove_fleet change)

| Location | File:Line | Issue |
|----------|-----------|-------|
| Combat destruction | `conflict_resolution_engine.py:186` | Ghost fleet after combat |
| JOIN_FLEET merge | `fleet_order_processor.py:113` | Merged fleet in registry |
| COLONIZE empty | `fleet_order_processor.py:216` | Empty fleet in registry |
| Instant merge | `fleet_order_processor.py:663` | Merged fleet in registry |
| Superweapon finalize | `superweapon_order_processor.py:103` | Consumed fleet in registry |
| Self-destruct | `superweapon_order_processor.py:613` | Consumed fleet in registry |
| Maintenance scuttle | `maintenance_engine.py:286` | Empty fleet in registry |
| Stellarate (explicit) | `superweapon_order_processor.py:241` | Already has unregister; becomes redundant |

## Related Documents

- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification

### After Each Phase
```bash
pytest tests/ --testmon
```

### Final Verification
```bash
pytest tests/ -n 12
```

### Manual Test Checklist
- [ ] Start new game, build ship at colony → fleet appears in galaxy registry
- [ ] Split fleet → both fleets queryable via `get_fleet_by_id()`
- [ ] Merge fleet → merged fleet removed from registry
- [ ] Combat → destroyed fleet removed from registry
- [ ] Save/load → all fleets work correctly
- [ ] Colonize with solo colony ship → empty fleet removed

## Completion Checklist

- [ ] Phase 1: Core Empire Changes complete
- [ ] Phase 2: Wire Up Galaxy References complete
- [ ] Phase 3: Remove Redundant Calls complete
- [ ] Phase 4: Integration Tests complete
- [ ] Phase 5: Cleanup complete
- [ ] All tests passing (baseline + new)
- [ ] Audit passed
- [ ] User verified
