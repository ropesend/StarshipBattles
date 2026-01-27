# PROJ-24: ShipControllableAdapter Interface Migration

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-24` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-24 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Add Interface Methods | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Migrate AIController | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Migrate Behaviors | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Migrate core/* | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Remove Delegation | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-01-27
**Active Phase:** Planning Complete - Ready for Implementation
**Last Action:** Comprehensive plan created with 5 phases
**Next Action:** Begin Phase 1 - Add missing interface methods to IControllable
**Blockers:** None

## Overview
Refactor AIController and behavior classes to use IControllable interface methods exclusively instead of direct ship attribute access (~165 direct accesses across 4 files). This will allow removal of the `__getattr__`/`__setattr__` delegation in ShipControllableAdapter.

**Origin:** LPA-01 finding from PROJ-22 review

## Goals
- Complete the IControllable interface migration started in PROJ-12
- Remove backward-compatibility delegation from ShipControllableAdapter
- Eliminate all direct ship attribute access in AI code
- Enable clean interface-based AI testing

## Scope
**In:**
- `game/ai/interfaces/controllable.py` - Add ~11 missing interface methods
- `game/ai/controller.py` - Migrate ~48 direct accesses to interface methods
- `game/ai/behaviors.py` - Migrate ~35 direct accesses to interface methods
- `game/ai/core/system.py` - Migrate ~58 direct accesses to interface methods
- `game/ai/core/behaviors.py` - Migrate ~22 direct accesses to interface methods
- Test updates in `tests/unit/ai/`

**Out:**
- Consolidating the two AI implementations (separate PROJ-25)
- `game/ai/target_evaluator.py` - Uses Ship objects directly for evaluation

## Critical Finding: Dual AI Implementations

**There are TWO parallel AIController implementations in active use:**

| Implementation | Location | Used By |
|---------------|----------|---------|
| **Simulation Layer** | `game/ai/controller.py` + `game/ai/behaviors.py` | `battle_engine.py`, `battle_orchestrator.py`, tests |
| **UI Layer** | `game/ai/core/system.py` + `game/ai/core/behaviors.py` | `battle.py`, `setup.py`, `panels.py`, builder |

Both must be migrated before delegation can be removed.

## Key Files
| Component | File Path | Changes |
|-----------|-----------|---------|
| Interface + Adapter | `game/ai/interfaces/controllable.py` | Add ~11 new interface methods |
| AIController (simulation) | `game/ai/controller.py` | Migrate ~48 direct accesses |
| Behaviors (simulation) | `game/ai/behaviors.py` | Migrate ~35 direct accesses |
| AIController (UI) | `game/ai/core/system.py` | Migrate ~58 direct accesses |
| Behaviors (UI) | `game/ai/core/behaviors.py` | Migrate ~22 direct accesses |
| Interface tests | `tests/unit/ai/test_controllable_interface.py` | Add tests for new methods |

## New Interface Methods Required

| Method | Implementation |
|--------|----------------|
| `get_turn_speed()` | `return self._ship.turn_speed` |
| `get_acceleration_rate()` | `return self._ship.acceleration_rate` |
| `get_is_thrusting()` | `return self._ship.is_thrusting` |
| `set_rotation(angle)` | `self._ship.angle = angle` |
| `set_in_formation(value)` | `self._ship.in_formation = value` |
| `set_formation_master(master)` | `self._ship.formation_master = master` |
| `get_secondary_targets()` | `return self._ship.secondary_targets or []` |
| `set_secondary_targets(targets)` | `self._ship.secondary_targets = targets` |
| `get_components_by_ability(name, op)` | `return self._ship.get_components_by_ability(...)` |
| `adjust_position(delta)` | `self._ship.position += delta` |
| `get_layers()` | `return self._ship.layers` |

## Related Documents
- [design.md](design.md) - Architecture analysis and swarm findings
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (4563+ tests)
- [ ] No direct attribute access via grep verification
- [ ] Audit passed
- [ ] User verified

## Estimated Effort
- Phase 1: ~1 hour (interface additions)
- Phase 2: ~2 hours (controller.py migration)
- Phase 3: ~2 hours (behaviors.py migration)
- Phase 4: ~3 hours (core/*.py migration)
- Phase 5: ~30 minutes (cleanup)
- Testing: ~1.5 hours
- **Total: ~10-11 hours**

## Future Work (PROJ-25)
After PROJ-24 completes, a separate project should consolidate the dual AI implementations:
- Determine which implementation is canonical
- Migrate all consumers to use single implementation
- Delete duplicate code in `game/ai/core/`
