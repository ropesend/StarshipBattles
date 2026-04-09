# PROJ-260: Ship Further Decomposition - LayerManager and ResourceManager Extraction

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-260` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-260 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Deep Analysis of Ship Class | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract ShipLayerManager | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Extract ShipResourceManager | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Thin Facade + Docs + Verification | Complete | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-04-08
**Active Phase:** Phase 1 Complete, ready for Phase 2
**Last Action:** Phase 1 analysis complete. Extraction plan: ShipLayerManager (145 lines: _initialize_layers, _equip_default_hull, change_class) + ShipResourceManager (66 lines: get_resource_stat, resource attrs). Projected Ship: ~511 lines. Findings in findings/phase_1_extraction_plan.md.
**Next Action:** Phase 2 — Extract ShipLayerManager (TDD)
**Blockers:** PROJ-258 (DI Migration) must be complete before execution begins

## Overview
Ship.py is 713 lines with 53 public methods and 77 properties. Nine delegates have already been
extracted (ShipComponentManager, ShipCombatManager, ShipCombatEngine, ShipStatsCalculator,
ShipStatQuerier, ShipValidatorHelper, ShipFormation, ShipPhysicsMixin, ShipSerializer), but the
class still owns layer initialization logic and resource management state that belong in dedicated
delegates. This project extracts two new delegates -- ShipLayerManager and ShipResourceManager --
to bring Ship below 500 lines while maintaining its role as a pure facade.

## Goals
- Extract layer initialization and layer-query logic into ShipLayerManager
- Extract resource state, initialization tracking, and resource stat accessors into ShipResourceManager
- Reduce Ship.py line count from ~713 to under 500
- Maintain Ship as the public API facade (no breaking changes to any caller)
- Follow the established facade/delegate pattern used by all 9 existing delegates
- Full TDD: tests written before implementation for both new delegates

## Scope
**In:**
- `_initialize_layers()` method and layer radius recalculation logic (lines 364-422)
- `_equip_default_hull()` method (lines 189-206)
- `change_class()` method -- layer-related portion (lines 424-492)
- Resource-related instance variables: `resources`, `_resources_initialized`, `_prev_max_resources`, `_prev_max_shields`
- Resource stat accessor: `get_resource_stat()` (lines 595-611)
- Resource consumption attributes (lines 147-153): `fuel_consumption`, `ammo_consumption`, `energy_consumption`, `potential_fuel_consumption`, `potential_ammo_consumption`, `potential_energy_consumption`
- `_initialize_resources()` in ShipStatsCalculator that reads/writes Ship resource state (lines 580-617)
- Facade methods on Ship that delegate to new managers

**Out:**
- Changes to existing delegates (ShipComponentManager, ShipCombatManager, etc.)
- Changes to ResourceRegistry or ResourceState classes
- Changes to ShipStatsCalculator's 5-phase calculation pipeline (it will call the new manager instead of Ship directly)
- New features or behavior changes -- this is purely structural

## Key Files
| Component | File Path |
|-----------|-----------|
| **Ship (target)** | `game/simulation/entities/ship.py` |
| **ShipStatsCalculator** | `game/simulation/entities/ship_stats.py` |
| **ResourceRegistry** | `game/simulation/systems/resource_manager.py` |
| **LayerData** | `game/simulation/entities/layer_data.py` |
| **ShipComponentManager** | `game/simulation/entities/ship_component_manager.py` |
| **ShipCombatManager** | `game/simulation/entities/ship_combat_manager.py` |
| **ShipCombatEngine** | `game/simulation/entities/ship_combat_engine.py` |
| **ShipStatQuerier** | `game/simulation/entities/ship_stat_querier.py` |
| **ShipValidatorHelper** | `game/simulation/entities/ship_validator_helper.py` |
| **ShipFormation** | `game/simulation/entities/ship_formation.py` |
| **ShipPhysicsMixin** | `game/simulation/entities/ship_physics.py` |
| **ShipSerializer** | `game/simulation/entities/ship_serialization.py` |
| **ShipDesignStats** | `game/simulation/entities/ship_design_stats.py` |
| **ShipLoader** | `game/simulation/entities/ship_loader.py` |
| **Existing Ship Tests** | `tests/unit/entities/test_ship.py` |
| **Component Manager Tests** | `tests/unit/simulation/entities/test_ship_component_manager.py` |
| **Combat Manager Tests** | `tests/unit/simulation/entities/test_ship_combat_manager.py` |
| **Stats Calculator Tests** | `tests/unit/simulation/systems/test_ship_stats_calculator_phases.py` |
| **Resource Stat Tests** | `tests/unit/simulation/entities/test_ship_resource_stat.py` |
| **NEW: ShipLayerManager** | `game/simulation/entities/ship_layer_manager.py` |
| **NEW: ShipLayerManager Tests** | `tests/unit/simulation/entities/test_ship_layer_manager.py` |
| **NEW: ShipResourceManager** | `game/simulation/entities/ship_resource_manager.py` |
| **NEW: ShipResourceManager Tests** | `tests/unit/simulation/entities/test_ship_resource_manager.py` |

## Dependency: PROJ-258
This project depends on PROJ-258 (DI Migration) being complete. PROJ-258 may change how
registries are accessed, which affects `_initialize_layers()` and `_equip_default_hull()`.
Starting this project before PROJ-258 is done risks rework.

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [manifest.md](manifest.md) - File manifest for conflict detection

## Verification
- [ ] All phase checklists complete
- [ ] All 14783+ tests passing (zero regressions)
- [ ] Ship.py line count < 500
- [ ] Ship retains all public API methods (facade only)
- [ ] No caller changes required outside Ship and ShipStatsCalculator
- [ ] docs/ updated if architecture patterns changed
- [ ] Audit passed
- [ ] User verified
