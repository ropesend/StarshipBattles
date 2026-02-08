# PROJ-74: Resupply System

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-74` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-74 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Fuel Synthesizer Component | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. PlanetaryFacility Resource Tracking | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. ResupplyEngine Core | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Fleet Resupply Logic | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. TurnEngine Integration | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. End-to-End Testing | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-02-08
**Active Phase:** Phase 2 Complete - Ready for Phase 3
**Last Action:** Added resource_levels field, serialization, and helper methods to PlanetaryFacility
**Next Action:** Begin Phase 3 - ResupplyEngine Core
**Blockers:** None
**Context for Next Agent:** PlanetaryFacility now has resource_levels: Dict[str, float] field with get_fuel_storage(), get_max_fuel_storage(registries), add_fuel(amount, registries), withdraw_fuel(amount) methods. Serialization updated in Planet.to_dict()/from_dict(). 25 new tests in test_facility_resource_tracking.py. All 6829 tests pass. Next phase creates the ResupplyEngine class.

## Overview
Implement a fuel resupply system where:
1. **Fuel Synthesizer** component produces fuel on planetary complexes
2. Fuel accumulates in complex's fuel tanks (storage)
3. Ships at same sector as planet automatically load fuel (continuous per-tick)
4. Owner's fleets get priority over other fleets
5. Fuel is distributed to equalize range across fleet ships

## Goals
- Add Fuel Synthesizer component (complex-only)
- Track fuel storage on planetary facilities
- Implement per-tick resupply during turn processing
- Smart fuel distribution to equalize fleet range

## Scope
**In Scope:**
- Fuel Synthesizer component with configurable output (200-500/turn)
- PlanetaryFacility resource tracking (fuel storage)
- ResupplyEngine for turn processing
- Fleet-level fuel distribution algorithm (range equalization)
- Save/load persistence for facility fuel levels

**Out of Scope:**
- Other resource types (energy, ammo) - future extension
- Allied fleet resupply - owner only for now
- UI for resupply status - future enhancement

## Key Files
| Component | File Path |
|-----------|-----------|
| PlanetaryFacility | `game/strategy/data/planet.py:24-31` |
| ResourceGeneration | `game/simulation/components/abilities/resources.py:191-228` |
| ResourceStorage | `game/simulation/components/abilities/resources.py:151-188` |
| TurnEngine | `game/strategy/engine/turn_engine.py` |
| ResourceManagementEngine | `game/strategy/engine/resource_management_engine.py` |
| ShipInstance | `game/strategy/data/ship_instance.py` |
| Galaxy spatial | `game/strategy/data/galaxy.py:192` |
| Components JSON | `data/components.json` |
| Fuel Tank | `data/components.json:238-261` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
