# PROJ-87: God Class Decomposition — Strategy Data Tier

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-87` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-87 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. ShipInstance Resource Extraction | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. ShipInstance Cargo & Display Extraction | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Fleet Resource Aggregation Extraction | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Fleet Capability & Battle Extraction | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. GameSession Command Handlers | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. GameSession Initialization Extraction | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-02-10
**Active Phase:** Phase 3
**Last Action:** Phase 2 complete — ShipCargoManager + ShipDisplayFormatter extracted (874→749 lines, 31 new tests)
**Next Action:** Begin Phase 3 — Fleet resource aggregation extraction
**Blockers:** None

## Overview
Decompose three strategy-layer God classes (ShipInstance 922 LOC, Fleet 833 LOC, GameSession 834 LOC) by extracting focused delegate classes. ShipInstance and Fleet both suffer from duplicated resource management logic (~360 lines combined). GameSession's command dispatch is a growing if/elif chain.

## Goals
- Reduce ShipInstance from 922 → ~500 lines (46% reduction)
- Reduce Fleet from 833 → ~450 lines (46% reduction)
- Reduce GameSession from 834 → ~550 lines (34% reduction)
- Eliminate ~360 lines of duplicate resource management logic
- Replace GameSession's command dispatch if/elif chain with registry pattern
- Maintain facade pattern — original classes remain public API, no import chain breakage

## Scope
**In:**
- ShipInstance resource, cargo, and display method extraction
- Fleet resource aggregation, capability, and battle adapter extraction
- GameSession command handler and initialization extraction
- Galaxy.get_fleet_by_id() performance fix

**Out:**
- Simulation-layer Ship class (PROJ-88)
- UI screens (PROJ-86, PROJ-89)
- Component class (PROJ-88)
- Changing the ShipInstance↔Ship bridge pattern (to_ship/from_ship)

## Key Files
| Component | File Path |
|-----------|-----------|
| ShipInstance | `game/strategy/data/ship_instance.py` |
| Fleet | `game/strategy/data/fleet.py` |
| FleetOrder | `game/strategy/data/fleet.py` (same file) |
| GameSession | `game/strategy/engine/game_session.py` |
| Galaxy | `game/strategy/data/galaxy.py` |
| ProductionEngine | `game/strategy/engine/production_engine.py` |
| FleetMovementEngine | `game/strategy/engine/fleet_movement_engine.py` |
| FleetOrderProcessor | `game/strategy/engine/fleet_order_processor.py` |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-09 | Execute PROJ-87 first among 4 God class projects | Cleanest dependency graphs (23-100 importers), good test coverage, highest duplication density |
| 2026-02-09 | Include re-offender classes (previously decomposed ones) | Prior decompositions were incomplete or grew back; need stronger extraction |
| 2026-02-09 | Use facade/delegate pattern for all extractions | Preserves public API; import chains don't break; original classes remain the entry point |

## Initial Analysis

### ShipInstance (922 lines, 49 methods)
- **47 importers** (moderate blast radius)
- **39 test files** (good coverage)
- 13 resource methods (~166 lines) duplicate simulation-layer Ship resource logic
- 5 display methods don't belong in data layer
- 5 cargo methods are self-contained extraction candidates
- Serialization (to_dict/from_dict, to_ship/from_ship) stays — it's core identity

### Fleet (833 lines, 48 methods across Fleet + FleetOrder + OrderType)
- **100 importers** (high blast radius — facade pattern critical)
- **77 test files** (excellent coverage)
- 12 resource aggregation methods (~211 lines) follow identical loop-over-ships patterns
- 5 capability methods are self-contained
- 3 battle adapter methods bridge strategy↔simulation

### GameSession (834 lines, 24 methods)
- **23 importers** (moderate blast radius)
- **17 test files** (good coverage)
- TurnEngine delegation works well (PROJ-12)
- 8 command handlers in if/elif chain — growing with each new command type
- 130-line initialization entangles galaxy, empire, race setup

## Swarm Findings Summary

### Architecture
- ShipInstance resource methods (lines 246-412) re-implement ResourceRegistry behavior from Ship
- Fleet compounds this by aggregating ShipInstance methods (lines 236-447)
- Total: ~360 lines of duplicate resource logic across 2 classes
- GameSession properly delegates to TurnEngine; command handlers are the main issue

### Key Patterns to Reuse
- **Facade delegation**: `self.resources = ShipResourceManager(self)` — delegate, don't re-implement
- **Registry dispatch**: Replace if/elif in `handle_command()` with handler registry
- **Loop aggregation**: Fleet methods all follow `for ship in self.get_combat_capable_ships(): aggregate(ship.method())` — extract once

### Risks Identified
1. **Fleet↔ShipInstance junction in production_engine.py** — imports both; coordinate extraction. Mitigation: facade pattern ensures no import changes needed.
2. **100 Fleet importers** — any API change ripples widely. Mitigation: facade keeps existing method signatures as thin wrappers.
3. **Display methods in data layer** — moving to UI layer could create circular dependency. Mitigation: extract to separate formatter file in strategy layer, not UI.

---

## Phases

### Phase 1: ShipInstance Resource Extraction [Medium]
**Objective:** Extract ShipResourceManager to centralize 13 resource methods
**Status:** Not Started
See [phase_1_checklist.md](phase_1_checklist.md)

### Phase 2: ShipInstance Cargo & Display Extraction [Simple]
**Objective:** Extract cargo operations and display formatting
**Status:** Not Started
See [phase_2_checklist.md](phase_2_checklist.md)

### Phase 3: Fleet Resource Aggregation Extraction [Medium]
**Objective:** Extract FleetResourceAggregator to consolidate 12 aggregation methods
**Status:** Not Started
See [phase_3_checklist.md](phase_3_checklist.md)

### Phase 4: Fleet Capability & Battle Extraction [Simple]
**Objective:** Extract capability calculator and battle adapter
**Status:** Not Started
See [phase_4_checklist.md](phase_4_checklist.md)

### Phase 5: GameSession Command Handlers [Medium]
**Objective:** Extract command handlers into registry pattern
**Status:** Not Started
See [phase_5_checklist.md](phase_5_checklist.md)

### Phase 6: GameSession Initialization Extraction [Simple]
**Objective:** Extract initialization logic and add fleet lookup optimization
**Status:** Not Started
See [phase_6_checklist.md](phase_6_checklist.md)

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/` — 7353 tests pass (baseline established)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` — all affected tests pass
- [ ] Verify original class still works as facade (no broken imports)
- [ ] New extracted class has dedicated test file

### Final Verification
- [ ] Run full test suite: `pytest tests/ -n 12` (NOT --testmon)
- [ ] ShipInstance ≤ 550 lines
- [ ] Fleet ≤ 500 lines
- [ ] GameSession ≤ 600 lines
- [ ] No new import chain breakage

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [x] Phase 1 complete — ShipResourceManager extracted
- [x] Phase 2 complete — Cargo and display methods extracted
- [ ] Phase 3 complete — FleetResourceAggregator extracted
- [ ] Phase 4 complete — Fleet capability and battle adapter extracted
- [ ] Phase 5 complete — Command handlers extracted
- [ ] Phase 6 complete — GameSession initialization extracted
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
