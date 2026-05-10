# PROJ-237: Planetary Shield, Energy System & Planet Orders Framework

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-237` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-237 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Ability Classes & Component Definitions | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Data Model Changes | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Planet Energy Engine | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Planet Orders Framework | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Integration & Shield Blocking | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. UI, Quickstart & Final Integration | Complete | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-03-29
**Active Phase:** Complete
**Last Action:** All 6 phases implemented and verified
**Next Action:** Create PROJ-238 for order system unification, UI, and hotkeys
**Blockers:** None
**Test Baseline:** 13951 passed → **14016 passed** (+65 new tests), 19 failed (pre-existing, unchanged)

## Overview
Add three interconnected subsystems to the strategy layer: (1) a per-planet energy system with generators and batteries, (2) a planetary shield that consumes energy and blocks planet destroyers, and (3) a planet orders framework (parallel to fleet orders) that enables tick-based planet actions. The shield is the first planet order type; future orders include launching fighters and converting resources.

## Goals
- Introduce a planet-level energy resource (generation, storage, consumption)
- Create a planetary shield component that blocks superweapon planet destruction
- Build a reusable planet orders framework for future planet-level actions
- Display shield status and energy level in the planet report UI
- Add a starting complex with shield + generator + battery on each homeworld

## Scope
**In:**
- Three new ability classes (PlanetaryShield, PlanetaryEnergyGenerator, PlanetaryEnergyStorage)
- Three new component definitions in `components.json`
- Per-planet energy fields on `Planet` dataclass
- `PlanetEnergyEngine` (per-tick generation/consumption/clamping)
- `PlanetOrderType` enum + `PlanetOrder` dataclass (parallel to fleet orders)
- `PlanetActionEngine` (per-tick order execution with `execution_progress`)
- `PlanetActionTimeResolver` (resolve action_time from ability JSON data)
- Command handlers for issuing planet orders from UI
- Shield blocking in `superweapon_order_processor.py`
- Shield/energy display in planet report panel (text in `format_planet_info()`)
- New `qs_shield_complex.json` starting complex
- `IPlanet` protocol update for new fields
- `PlanetInfo` DTO update
- Event types for shield/energy events
- Comprehensive unit and integration tests

**Out:**
- Combat-layer shield integration (placeholder only; future work)
- Visual energy bar widget (text display only for now)
- Orbital bombardment mechanics
- Planet order UI panel (orders issued programmatically/via existing patterns for now)
- Energy cost for non-shield components (future expansion)

## Key Files
| Component | File Path |
|-----------|-----------|
| **New ability classes** | `game/simulation/components/abilities/planetary.py` (NEW) |
| **Ability registry** | `game/simulation/components/abilities/__init__.py` |
| **Component data** | `data/components.json` |
| **Planet dataclass** | `game/strategy/data/planet.py` |
| **Facility dataclass** | `game/strategy/data/planetary_facility.py` |
| **Planet order types** | `game/strategy/data/planet_order_types.py` (NEW) |
| **Energy engine** | `game/strategy/engine/planet_energy_engine.py` (NEW) |
| **Planet action engine** | `game/strategy/engine/planet_action_engine.py` (NEW) |
| **Action time resolver** | `game/strategy/services/planet_action_time_resolver.py` (NEW) |
| **Engine interfaces** | `game/strategy/interfaces/engines.py` |
| **Turn engine** | `game/strategy/engine/turn_engine.py` |
| **Superweapon processor** | `game/strategy/engine/superweapon_order_processor.py` |
| **Planet commands** | `game/strategy/engine/planet_command_handlers.py` (NEW) |
| **Command dataclasses** | `game/strategy/engine/commands.py` |
| **Command registry** | `game/strategy/engine/command_handlers.py` |
| **Planet order validator** | `game/strategy/validation/planet_order_validator.py` (NEW) |
| **Event types** | `game/strategy/events/event_types.py` |
| **IPlanet protocol** | `game/core/protocols.py` |
| **Planet DTO** | `game/strategy/facade/dto/planet_dto.py` |
| **Planet info formatter** | `game/ui/screens/strategy_detail_fmt.py` |
| **Quickstart builder** | `game/strategy/quickstart_builder.py` |
| **Starting complex** | `tests/fixtures/quickstart/designs/qs_shield_complex.json` (NEW) |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-29 | Per-planet energy pool (not per-facility) | Simpler, more intuitive. All facilities share one planet-wide pool. |
| 2026-03-29 | Strategy-only shield for now; combat placeholders | Planets don't participate in combat yet. Full combat integration is future work. |
| 2026-03-29 | Auto-deactivate shield when energy hits zero | Simple and predictable. Player must reactivate manually. |
| 2026-03-29 | Timed shield activation/deactivation (ticks from JSON) | Adds strategic depth. Can span multiple turns (>100 ticks). Framework for future planet orders. |
| 2026-03-29 | Separate PlanetOrderType enum (not extending OrderType) | Planet orders are fundamentally different entities from fleet orders. Clean separation. |
| 2026-03-29 | Planet orders queue lives on Planet (mirrors Fleet.orders) | Planet is the commanded entity, like Fleet. |
| 2026-03-29 | `component_states` dict on PlanetaryFacility for shield active state | Flexible state tracking without modifying component registry or design data (read-only definitions). |
| 2026-03-29 | Energy generation phase after fuel gen (Phase 0c1), planet actions after fleet actions (Phase 1.6) | Energy must be generated before consumed. Planet actions are strategic like fleet actions. |

## Initial Analysis
See [design.md](design.md) for full architecture analysis and swarm findings.

## Swarm Findings Summary
### Architecture
- Module placement is correct: abilities in `game/simulation/components/abilities/`, engines in `game/strategy/engine/`
- No layer violations: all interactions stay within Strategy ↔ Simulation boundary
- Energy engine follows HarvestingEngine (stateless scan) pattern; planet action engine follows ActionExecutionEngine (stateful progress) pattern
- TurnEngine integration: two new phases via existing lazy-property + `_time_phase()` pattern

### Key Patterns to Reuse
- **Component scanning**: `iter_components()` + `get_component_abilities()` + registry lookup (see `harvesting_engine.py:35-80`)
- **Action execution**: `execution_progress` tracking + `ActionTimeResolver` delegation (see `action_execution_engine.py:105-183`)
- **Command handlers**: `BaseCommandHandler._resolve_planet()` + validator delegation (see `superweapon_command_handlers.py`)
- **Serialization**: `.get()` with defaults for backward compatibility (see `planet.py:338-350`)
- **Engine DI**: Lazy properties with runtime import in TurnEngine (see `turn_engine.py:229-329`)

### Risks Identified
1. **Mid-turn facility destruction** (HIGH) — Generator/battery/shield scuttled by maintenance mid-turn. Mitigate: recalculate capacity each tick (like HarvestingEngine's `recalculate_storage()`), auto-deactivate shield if shield facility destroyed.
2. **Multiple shields on one planet** (MEDIUM) — No existing "one-per-planet" constraint pattern. Mitigate: treat as additive (multiple generators/batteries stack), but only one shield can be active. Validate at order-issue time.
3. **Energy underflow** (MEDIUM) — Shield drains more than available. Mitigate: auto-deactivate when `energy < drain_rate_per_tick`, clamp to `[0, capacity]` each tick.
4. **Planet order conflicts** (MEDIUM) — ACTIVATE queued while DEACTIVATE in progress. Mitigate: guard execution with state checks; skip redundant orders.
5. **IPlanet protocol** (LOW) — New fields must be added to protocol and DTO. Straightforward but must not be missed.

---

## Phases

### Phase 1: Ability Classes & Component Definitions [Medium]
**Objective:** Create the three new ability classes and register them, then add component definitions to `components.json`.
**Status:** Not Started

See [phase_1_checklist.md](phase_1_checklist.md)

### Phase 2: Data Model Changes [Medium]
**Objective:** Add energy/shield/order fields to Planet, component_states to PlanetaryFacility, create PlanetOrder types, update protocols and DTOs.
**Status:** Not Started

See [phase_2_checklist.md](phase_2_checklist.md)

### Phase 3: Planet Energy Engine [Medium]
**Objective:** Create PlanetEnergyEngine that generates energy from generators, stores up to battery capacity, consumes energy for active shields, and auto-deactivates shields when energy runs out.
**Status:** Not Started

See [phase_3_checklist.md](phase_3_checklist.md)

### Phase 4: Planet Orders Framework [Complex]
**Objective:** Create PlanetActionEngine, PlanetActionTimeResolver, command handlers, and validators for tick-based planet order execution.
**Status:** Not Started

See [phase_4_checklist.md](phase_4_checklist.md)

### Phase 5: Integration & Shield Blocking [Medium]
**Objective:** Wire engines into TurnEngine, add shield blocking to superweapon processor, add event types.
**Status:** Not Started

See [phase_5_checklist.md](phase_5_checklist.md)

### Phase 6: UI, Quickstart & Final Integration [Medium]
**Objective:** Add shield/energy display to planet info UI, create starting complex, update quickstart builder, run full test suite.
**Status:** Not Started

See [phase_6_checklist.md](phase_6_checklist.md)

---

## Verification

### Project Start (REQUIRED)
- [ ] Read `docs/` foundation docs (01_ARCHITECTURE, 02_PATTERNS, 03_CONVENTIONS)
- [ ] Run full test suite: `python -m pytest tests/ -n 12` — all tests pass (establishes baseline)

### After Each Phase
- [ ] Run `python -m pytest tests/ --testmon` — all affected tests pass
- [ ] Verify no import errors: `python -c "from game.strategy.engine.turn_engine import TurnEngine"`

### Final Verification
- [ ] Start new quickstart game — shield complex spawned on homeworld
- [ ] Energy generates over turns, shield can be activated
- [ ] Planet destroyer blocked by active shield
- [ ] Shield auto-deactivates when energy runs out
- [ ] Run full test suite: `python -m pytest tests/ -n 12` — all tests pass
- [ ] Verify changes are consistent with `docs/` — update docs if architecture/patterns changed

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All Phase 4 tasks checked off
- [ ] All Phase 5 tasks checked off
- [ ] All Phase 6 tasks checked off
- [ ] All tests passing
- [ ] Regression tests passing
- [ ] Audit passed (no significant issues)
- [ ] User verified
