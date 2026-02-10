# PROJ-84: Ship Layer Data Typed Structures

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-84` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-84 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Create LayerData + Update Core Ship Entities | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Update Stats, Combat, Validation | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Update Serialization | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Update UI Layer | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Update Simulation Test Scenarios | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Update Test Files | Complete | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Cleanup & Final Verification | Complete | [phase_7_checklist.md](phase_7_checklist.md) |

## Current State
**Last Updated:** 2026-02-10
**Active Phase:** All Phases Complete - Ready for Audit
**Last Action:** Verified Phases 2-7 complete (cascading updates from Phase 1), fixed simulation_test isinstance guards
**Next Action:** Trigger audit per Protocol 04
**Blockers:** None
**Context for Next Agent:** All 7 phases verified complete. 7375 tests pass. simulation_tests has 62 pass, 5 fail (pre-existing), 4 skipped. Grep audits show zero remaining layer dict access in game/. Ready for project audit.

## Overview
Replace all raw `Dict[str, Any]` layer dictionaries in the ship system with a typed `LayerData` dataclass. This eliminates string-keyed dict access (`layer_data['components']`) throughout the entire codebase, providing IDE autocomplete, type safety, and protection against typos. The `hp` field (dead code, never used after init) is removed. Ship and ShipComponentManager layer initialization is consolidated.

## Goals
- Replace `Dict[str, Any]` layer dicts with `LayerData` dataclass across all production and test code
- Drop dead `hp` field from layer data
- Consolidate duplicated layer initialization between Ship and ShipComponentManager
- Zero backward-compatibility shims — clean eradication per CLAUDE.md policy

## Scope
**In:**
- New `LayerData` dataclass with factory methods
- All production code accessing `ship.layers` values
- All test files constructing or accessing layer dicts
- Simulation test scenario ability extraction helpers
- Consolidation of Ship/ShipComponentManager layer init

**Out:**
- Changing the `ship.layers` outer dict type (remains `Dict[LayerType, LayerData]`)
- Refactoring how components are stored (list stays)
- Any changes to component or ability classes
- Save file migration (saves are disposable per CLAUDE.md)

## Key Files
| Component | File Path |
|-----------|-----------|
| LayerData (new) | `game/simulation/entities/layer_data.py` |
| Ship | `game/simulation/entities/ship.py` |
| ShipComponentManager | `game/simulation/entities/ship_component_manager.py` |
| ShipStatsCalculator | `game/simulation/entities/ship_stats.py` |
| ShipSerializer | `game/simulation/entities/ship_serialization.py` |
| DamageCalculator | `game/simulation/combat/damage_calculator.py` |
| ShipValidator | `game/simulation/validation/ship_validator.py` |
| VehicleDesignService | `game/simulation/services/vehicle_design_service.py` |
| LayerPanel | `game/ui/screens/builder/layer_panel.py` |
| BuilderMain | `game/ui/screens/builder/main.py` |
| WorkshopEventRouter | `game/ui/screens/workshop_event_router.py` |
| GameRenderer | `game/ui/renderer/game_renderer.py` |
| ShipStatsRenderer | `game/ui/panels/ship_stats_renderer.py` |
| BattleUIService | `game/ui/services/battle_ui_service.py` |
| StatsConfig | `game/ui/screens/builder/stats_config.py` |
| IControllable | `game/ai/interfaces/controllable.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [x] All phase checklists complete
- [x] `pytest tests/ -n 12` — all 7375 tests pass
- [x] `pytest simulation_tests/` — 62 pass, 5 fail (pre-existing physics calibration issues), 4 skipped
- [x] Grep for `['components']` in game/ returns zero hits (only JSON access in component.py, not LayerData)
- [x] Grep for `isinstance(layer_data, dict)` returns zero hits (outside archived/docs)
- [x] Audit passed
- [ ] User verified
