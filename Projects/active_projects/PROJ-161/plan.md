# PROJ-161: Per-Tick Harvesting and Maintenance

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-161` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-161 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. HarvestingEngine Per-Tick Conversion | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. MaintenanceEngine Per-Tick Conversion | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. TurnEngine Wiring & Legacy Removal | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Test Updates | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Cleanup & Legacy Removal | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-02-23
**Active Phase:** Phase 2
**Last Action:** Phase 1 complete - added process_harvesting_tick() with tick_fraction parameter
**Next Action:** Begin Phase 2 - MaintenanceEngine Per-Tick Conversion
**Blockers:** None

## Overview
Harvesting and maintenance currently run once at turn-start before the 100-tick subturn loop. Every other economy engine (resource consumption, fuel generation, fleet resupply, construction) already spreads work across 100 ticks. This project converts both harvesting and maintenance to per-tick operations, eliminates the redundant `_apply_partial_harvest` legacy code, and updates all affected tests.

## Goals
- Spread harvesting across 100 ticks (1/100th per tick), matching fuel generation pattern
- Spread maintenance across 100 ticks (1/100th per tick), with immediate scuttle on failure
- Eliminate `_apply_partial_harvest` from ProductionEngine (redundant with per-tick harvesting)
- Remove `harvesting_engine` parameter threading through ProductionEngine
- Update all affected tests
- Update interfaces and documentation

## Scope
**In:**
- HarvestingEngine: new `process_harvesting_tick(tick, empires)` method
- MaintenanceEngine: new `process_maintenance_tick(tick, empires)` method
- TurnEngine: move harvesting/maintenance into `_process_tick()`
- ProductionEngine: remove `_apply_partial_harvest` and `harvesting_engine` parameter
- IHarvestingEngine / IMaintenanceEngine interface updates
- All affected unit, integration, and E2E tests
- Storage recalculation every tick

**Out:**
- UI display changes (rates stay as "/turn" -- internal spreading invisible to players)
- EmpireEconomyCalculator changes (read-only projections, uses per-turn totals)
- PopulationEngine (stays once-per-turn by design)

## Key Files
| Component | File Path |
|-----------|-----------|
| Harvesting Engine | `game/strategy/engine/harvesting_engine.py` |
| Maintenance Engine | `game/strategy/engine/maintenance_engine.py` |
| Turn Engine | `game/strategy/engine/turn_engine.py` |
| Production Engine | `game/strategy/engine/production_engine.py` |
| Engine Interfaces | `game/strategy/interfaces/engines.py` |
| Integration Tests - Harvesting | `tests/integration/strategy/turn_engine/test_harvesting.py` |
| Integration Tests - Maintenance | `tests/integration/strategy/turn_engine/test_maintenance.py` |
| E2E Tests | `tests/integration/strategy/test_economy_e2e.py` |
| Unit Tests - Harvesting | `tests/unit/strategy/engine/test_harvesting_engine.py` |
| Unit Tests - Maintenance | `tests/unit/strategy/engine/test_maintenance_engine.py` |
| Unit Tests - Production | `tests/unit/strategy/production_engine/test_tick_consumption.py` |
| Turn Engine conftest | `tests/integration/strategy/turn_engine/conftest.py` |
| UI Scuttle Notification | `game/ui/screens/strategy_screen.py` |
| Economy Calculator | `game/strategy/engine/empire_economy_calculator.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] Full test suite passing: `pytest tests/ -n 12`
- [ ] E2E: 100 ticks harvesting == old 1-call harvesting (numerical equivalence)
- [ ] E2E: 100 ticks maintenance == old 1-call maintenance (numerical equivalence)
- [ ] E2E: Storage cap enforced correctly with per-tick accumulation
- [ ] E2E: Scuttle notification appears in UI when maintenance fails
- [ ] `_apply_partial_harvest` fully removed, no dead code remaining
- [ ] `harvesting_engine` parameter fully removed from ProductionEngine
- [ ] Audit passed
- [ ] User verified
