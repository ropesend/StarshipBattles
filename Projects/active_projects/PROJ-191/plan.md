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
| 4. Replace hasattr Type Discrimination | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Miscellaneous Cleanup | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Document & Audit | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-02-24
**Active Phase:** Phase 3 Complete
**Last Action:** Updated test mocks to use spec= parameter for type safety
**Next Action:** Phase 4 — Replace hasattr Type Discrimination
**Blockers:** None
**Context for Next Agent:** Phase 3 complete. Updated test mocks in:
- test_empire_economy_calculator.py: 15 Mock() calls → Mock(spec=Empire/Planet/Fleet/etc.)
- test_harvesting_engine.py: _make_empire() and _make_planet() helpers use spec=
- test_maintenance_engine.py: _make_colony() uses Mock(spec=Planet)
- test_production_refactor.py: mock_empire and mock_colony fixtures use spec=
- test_fleet_movement_engine.py: create_mock_fleet() uses Mock(spec=Fleet), empire uses Mock(spec=Empire)
- test_population_engine.py: TurnEngine integration test empire uses Mock(spec=Empire)
All 12702 tests pass (1 skipped).

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
