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
| 5. Miscellaneous Cleanup | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Document & Audit | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-02-24
**Active Phase:** Phase 4 Complete
**Last Action:** Replaced ~25 hasattr patterns with isinstance/protocol checks
**Next Action:** Phase 5 — Miscellaneous Cleanup
**Blockers:** None
**Context for Next Agent:** Phase 4 complete. Key changes:
- galaxy_entity_registry.py: Replaced hasattr(planet, 'diameter_hexes') with direct access, hasattr(obj, 'occupied_hexes') with is_zone_occupant(obj)
- galaxy_spatial_index.py: Direct star.location access, is_zone_occupant(star)
- colonize_validator.py: isinstance(zone_obj, Planet), is_planet(target) for order.target checks
- fleet_order_processor.py: isinstance(candidate, Planet), target_fleet is not None checks
- superweapon_order_processor.py: Removed 7 hasattr guards for owner_id/colonies/unregister_fleet
- fleet.py: isinstance(target, Planet) and isinstance(target, Fleet) for serialization
- fleet_dto.py: isinstance checks for order target conversion
- Updated 8+ test files to add get_zones_at_global_hex() to MockGalaxy and resources={} to mock planets
All 12701 tests pass (1 skipped).

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
