# PROJ-210: Strategy God Class Decomposition

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-210` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-210 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Serialization & Embedded Classes | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Facade Bloat & Pass-Through Elimination | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Planet Decomposition | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. FleetOrderProcessor Decomposition | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Dead Code & Cleanup | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-02-28
**Active Phase:** Phase 2
**Last Action:** Phase 1 complete - extracted FleetOrderSerializer, PlanetaryFacility, SpeciesPopulation
**Next Action:** Begin Phase 2 — Facade Bloat & Pass-Through Elimination
**Blockers:** None
**Test Baseline:** 12,929 tests passing (1 skipped, 4 bug_13 pre-existing failures)

## Overview
Systematic decomposition of strategy domain god classes based on findings from review `2026-02-27_211327_general_strategy-god-classes`. 80 total findings from 5 review agents, validated by 3 independent validators (12.5% rejection rate).

**Core Problem:** Fleet (552 lines), Planet (499 lines), and FleetOrderProcessor (648 lines) accumulate too many responsibilities. PROJ-87 extracted delegates but introduced ~120 lines of zero-value pass-through facade methods that maintained the god class API surface.

## Goals
1. Extract FleetOrder serialization into dedicated OrderSerializer (eliminate 7-branch isinstance chains)
2. Extract PlanetaryFacility and SpeciesPopulation to own modules
3. Eliminate ~120 lines of pass-through facade methods on Fleet (expose delegates via properties)
4. Decompose FleetOrderProcessor (648 lines) into focused command handlers
5. Extract shared ConstructionQueue abstraction (used by Fleet, Planet, PlanetaryFacility)
6. Remove ~150 lines of dead/unused code
7. Fix hidden circular dependency via late imports (Fleet → FleetSpeedCalculator)

## Scope
**In:**
- `game/strategy/data/fleet.py` — Pass-through elimination, serialization extraction
- `game/strategy/data/planet.py` — Extract embedded classes, separate concerns
- `game/strategy/data/ship_instance.py` — Minor cleanup (well-decomposed already)
- `game/strategy/data/fleet_resource_aggregator.py` — Decouple from Fleet internals
- `game/strategy/data/fleet_capability_calculator.py` — Consolidate duplicate utilities
- `game/strategy/data/fleet_battle_adapter.py` — Decouple from Fleet internals
- `game/strategy/engine/fleet_order_processor.py` — Decompose into command handlers
- `game/strategy/data/build_queue_source.py` — Shared ConstructionQueue abstraction
- All callers of pass-through methods (full codebase search required)

**Out:**
- UI layer changes (beyond updating import paths)
- New feature development
- Performance optimization (separate concern)
- FleetNavigationService (600+ lines but different problem — algorithmic complexity, not god class)

## Key Files
| Component | File Path | Lines | Action |
|-----------|-----------|-------|--------|
| Fleet (god class) | `game/strategy/data/fleet.py` | 552 | Remove pass-throughs, extract serialization |
| Planet (god class) | `game/strategy/data/planet.py` | 499 | Extract embedded classes, separate concerns |
| FleetOrderProcessor | `game/strategy/engine/fleet_order_processor.py` | 648 | Decompose into command handlers |
| Fleet delegates | `game/strategy/data/fleet_*.py` | 643 | Decouple from Fleet internals |
| Ship delegates | `game/strategy/data/ship_*.py` | 379 | Minor cleanup only |
| Build system | `game/strategy/data/build_queue_source.py` | 255 | Shared abstraction |

## Source Review
- Review folder: `Reviews/results/2026-02-27_211327_general_strategy-god-classes/`
- 5 agent reports: CQ (18), AR (18), ROF (14), CX (15), DC (15)
- 3 validator reports: V1 (33 reviewed), V2 (33 reviewed), V3 (14 reviewed)
- Confirmed findings: 53/80 (66%), Downgraded: 17 (21%), Rejected: 10 (12.5%)

## Key Findings Cross-Reference
| Finding IDs | Theme | Phase |
|-------------|-------|-------|
| ROF-001, CQ-03, AR-002, CX-01 | Serialization complexity | Phase 1 |
| ROF-002, CQ-05, AR-006 | Planet embedded classes | Phase 1 |
| CQ-01, CQ-02, ROF-006, DC-004 | Pass-through facade bloat | Phase 2 |
| AR-001 | Delegate tight coupling | Phase 2 |
| ROF-003 | Shared ConstructionQueue | Phase 3 |
| ROF-008, CQ-05 | Planet grid/economy separation | Phase 3 |
| AR-003, CX-03 | FleetOrderProcessor god class | Phase 4 |
| DC-001 through DC-015 | Dead code cleanup | Phase 5 |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- Related: PROJ-87 (Strategy Data Tier) — original decomposition attempt

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (baseline: 7,353)
- [ ] No new circular dependencies introduced
- [ ] Pass-through method count reduced to 0
- [ ] Fleet.py < 300 lines
- [ ] Planet.py < 300 lines (after extraction)
- [ ] Audit passed
- [ ] User verified
