# PROJ-191: Strategy Layer Duck Typing Elimination

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-191` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-191 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Type Hints on Signatures | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Replace getattr in Engines | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Update Test Mocks | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Replace hasattr Type Discrimination | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Miscellaneous Cleanup | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Document & Audit | Complete | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-02-25
**Active Phase:** PROJECT COMPLETE - AUDIT PASSED
**Last Action:** Audit cycle 1 PASSED
**Next Action:** None - project complete
**Blockers:** None
**Context for Next Agent:** Phase 6 complete. Key changes:
- Documented all remaining comp_def dual-format getattr patterns
- Replaced ~10 additional unnecessary getattr/hasattr patterns with direct access:
  - superweapon_validator.py: 4 patterns → direct (StarSystem.stars, warp_points always exist)
  - simulation_adapter.py: 2 patterns → direct (Ship.max_shields, current_shields)
  - design_metadata.py: 6 patterns → direct (Ship.vehicle_type, theme_id, Component attrs)
  - fleet_order_processor.py: 1 pattern → direct (Planet.id)
  - pathfinding.py: 2 patterns → direct (Fleet.id)
  - galaxy_spatial_index.py: 1 pattern → direct (Planet.diameter_hexes)
  - turn_engine.py: 2 patterns → direct (GameRegistries.components)
  - command_handlers.py: 1 pattern → direct (ValidationResult.error_code)
- Deleted 4 obsolete tests (test_design_metadata.py - testing impossible scenarios)
- Updated 2 MockPlanet classes in integration tests to add id attribute
- 20 remaining getattr/hasattr patterns - all documented as intentional
All 12693 tests pass (1 skipped). AUDIT PASSED on cycle 1.

## Overview
Replace ~93 implicit duck typing patterns (`hasattr()`/`getattr()`) in the `game/strategy/` layer with direct attribute access, explicit `isinstance` checks, and proper type annotations. Retain ~12 intentional `getattr` patterns at external data boundaries (JSON component definitions, save file deserialization).

## Goals
- Eliminate defensive `getattr(empire, 'colonies', [])` patterns where the attribute always exists
- Replace `hasattr(obj, 'planet_type')` type discrimination with `isinstance(obj, Planet)` checks
- Add type annotations to engine/service method signatures
- Update test mocks to use `spec=` parameter for early failure detection
- Document remaining intentional `getattr` patterns with explanatory comments

## Scope
**In:**
- `game/strategy/engine/` — all engine files (~53 getattr, ~15 hasattr)
- `game/strategy/data/` — fleet serialization, galaxy registry, spatial index (~15 instances)
- `game/strategy/services/` — cargo transfer, component inspector, fleet navigation (~13 instances)
- `game/strategy/validation/` — colonize validator (~5 instances)
- `game/strategy/facade/dto/` — fleet DTO order conversion (~3 instances)
- `tests/unit/strategy/` — update mocks to use spec=

**Out:**
- UI layer duck typing (`game/ui/`)
- Simulation layer (`game/simulation/`)
- AI layer (`game/ai/`)
- `from_dict()` deserialization methods (legitimate missing-field handling)
- `comp_def` dual-format patterns (dict-or-Component, ~12 instances — document only)

## Key Files
| Component | File Path |
|-----------|-----------|
| Existing Protocols | `game/core/protocols.py` |
| Empire class | `game/strategy/data/empire.py` |
| Planet/Facility | `game/strategy/data/planet.py` |
| Fleet/FleetOrder | `game/strategy/data/fleet.py` |
| ShipInstance | `game/strategy/data/ship_instance.py` |
| Economy Calculator | `game/strategy/engine/empire_economy_calculator.py` |
| Harvesting Engine | `game/strategy/engine/harvesting_engine.py` |
| Population Engine | `game/strategy/engine/population_engine.py` |
| Superweapon Processor | `game/strategy/engine/superweapon_order_processor.py` |
| Fleet Order Processor | `game/strategy/engine/fleet_order_processor.py` |
| Colonize Validator | `game/strategy/validation/colonize_validator.py` |
| Galaxy Entity Registry | `game/strategy/data/galaxy_entity_registry.py` |
| Galaxy Spatial Index | `game/strategy/data/galaxy_spatial_index.py` |
| Fleet DTO | `game/strategy/facade/dto/fleet_dto.py` |
| Cargo Transfer Service | `game/strategy/services/cargo_transfer_service.py` |
| Command Handlers | `game/strategy/engine/command_handlers.py` |
| Fleet Navigation | `game/strategy/services/fleet_navigation_service.py` |
| Area Effect Manager | `game/strategy/services/area_effect_manager.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
### After Each Phase
- [ ] `pytest tests/unit/strategy/ -n 12` — all strategy tests pass
- [ ] No new import cycles introduced

### Final Verification
- [ ] `pytest tests/ -n 12` — full suite matches baseline (12699+ passed, 6 pre-existing failures)
- [ ] `grep -rn "getattr\|hasattr" game/strategy/ --include="*.py"` — remaining instances all documented
- [ ] All phase checklists complete
- [ ] Audit passed
- [ ] User verified
