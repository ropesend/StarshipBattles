# PROJ-300: Universal IAbilitySource Framework + Storm/Facility Migration

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-300` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-300 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Aggregation framework (rates) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Register four new ability names | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. IAbilitySource protocol + Facility/Storm adapters + iterator | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Refactor system_effects_collector onto iterator | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Storm dataclass + JSON schema migration | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Migrate consumers off AreaEffectManager | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Eradicate AreaEffectManager + EnvironmentalEffects + StormEffect | Not Started | [phase_7_checklist.md](phase_7_checklist.md) |
| 8. UI integration | Not Started | [phase_8_checklist.md](phase_8_checklist.md) |
| 9. Docs sync | Not Started | [phase_9_checklist.md](phase_9_checklist.md) |

## Current State
**Last Updated:** 2026-04-26
**Active Phase:** Planning (plan approved)
**Last Action:** Project documents populated from approved master plan
**Next Action:** Begin Phase 1 — write failing tests for `aggregate_rates`
**Blockers:** None
**Context for Next Agent:** Master design is in [design.md](design.md). All architectural decisions are in [decisions.md](decisions.md). The companion projects PROJ-301..305 add new source kinds on top of this framework — do not pull their work into this project; this project's scope is **framework + storms + facilities only**.

## Overview

The codebase has two parallel "things at a location project effects" systems: facility/component sector-scope abilities (clean, scope-aware, two-phase aggregated, UI-visible via `system_effects_collector`) and storms (hardcoded `StormEffect` dataclass, custom multiplicative aggregation, never appear in the Sector panel; consumed via `AreaEffectManager` + `EnvironmentalEffects`).

This project builds the **universal `IAbilitySource` framework** — one protocol + iterator + collector pipeline that any locatable entity can plug into — and migrates the two existing source kinds (facilities, storms) onto it. `AreaEffectManager`, `EnvironmentalEffects`, and `StormEffect` are eradicated. Storms become first-class sector effects in the Sector panel.

Subsequent projects (PROJ-301..305) add new source kinds (planets-themselves, stars, warp points, system archetypes, fleets) on top of this framework.

## Goals
- Replace the hardcoded `StormEffect` / `EnvironmentalEffects` / `AreaEffectManager` triad with abilities-dict data flowing through `system_effects_collector`.
- Define `IAbilitySource` protocol + adapter package + unified iterator so future source kinds plug in via one adapter class each.
- Extend the aggregation framework to handle rate-style abilities (intra-group MAX, inter-group SUM) alongside existing multiplier-style abilities.
- Register four new ability names: `ThrustModifier`, `StrategicSpeedModifier`, `EnvironmentalDamage` (with `damage_type` parameter), `FuelDrain`.
- Storms appear in the Sector panel's "Sector Effects (N)" alongside facility-derived effects.
- Storm detail panel keeps lore (name + description) only — effects move to Sector Effects.
- Eradicate `AreaEffectManager`, `EnvironmentalEffects`, `StormEffect`, `_entries_from_environmental_effects`. Grep guard at end.

## Scope

**In:**
- `IAbilitySource` protocol in `game/core/protocols.py`.
- `game/strategy/services/ability_sources/` adapter package with `FacilityAbilitySource` + `StormAbilitySource` (only these two — others are PROJ-301..305).
- `game/strategy/services/ability_iterator.py` unified iterator.
- `system_effects_collector` refactored to delegate to the iterator.
- `aggregate_rates` in `strategic_ability_scanner.py`.
- `data/storm_types.json` (renamed + v2.0 schema).
- `Storm.abilities` dict (replacing `StormEffect`).
- Consumer rewrites: `fleet_movement_engine`, `environmental_hazard_engine`, `spec_compiler` + `conflict_resolution_engine`.
- Deletion of `area_effect_manager.py` (and its test), `StormEffect` dataclass, `_entries_from_environmental_effects`, all DI wiring.
- UI: unified `source_label` rendering, rate-style value formatter, storm detail panel keeps lore only.
- Documentation sync.

**Out (deferred to PROJ-301..305):**
- Planet intrinsic abilities (PROJ-301).
- Star intrinsic abilities (PROJ-302).
- Warp point intrinsic abilities (PROJ-303).
- Star system archetype abilities (PROJ-304).
- Fleet strategic-layer abilities (PROJ-305).
- Combat consumption of `ThrustModifier` (registered but not consumed — wire up in a follow-up).

## Key Files

| Component | File Path |
|-----------|-----------|
| `IAbilitySource` protocol | `game/core/protocols.py` |
| Adapter package | `game/strategy/services/ability_sources/` (NEW) |
| `FacilityAbilitySource` | `game/strategy/services/ability_sources/facility.py` (NEW) |
| `StormAbilitySource` | `game/strategy/services/ability_sources/storm.py` (NEW) |
| Unified iterator | `game/strategy/services/ability_iterator.py` (NEW) |
| Effect collector | `game/strategy/services/system_effects_collector.py` |
| Aggregation helpers | `game/strategy/services/strategic_ability_scanner.py` |
| Storm dataclass | `game/strategy/data/storm.py` |
| Storm type registry | `data/storm_types.json` (RENAMED from `data/storms.json`) |
| Storm generator | `game/strategy/generation/storm_generator.py` |
| Combat spec compiler | `game/strategy/combat/spec_compiler.py` |
| Conflict resolution engine | `game/strategy/engine/conflict_resolution_engine.py` |
| Fleet movement engine | `game/strategy/engine/fleet_movement_engine.py` |
| Environmental hazard engine | `game/strategy/engine/environmental_hazard_engine.py` |
| Simulation adapter | `game/strategy/adapters/simulation_adapter.py` |
| Ability stat registry | `game/simulation/combat/ability_stat_registry.py` |
| Sector panel renderer | `game/ui/panels/system_tree_panel.py` |
| Storm detail formatter | `game/ui/screens/strategy_detail_formatter.py` |
| ApplicationContext (DI) | `game/context.py` |
| **DELETE** | `game/strategy/services/area_effect_manager.py` |
| **DELETE** | `tests/unit/strategy/services/test_area_effect_manager.py` |

## Related Documents
- [design.md](design.md) — Architecture analysis, protocol shape, source-kind responsibilities, aggregation rules, what gets deleted.
- [decisions.md](decisions.md) — Full decisions log including user-confirmed design choices.
- [manifest.md](manifest.md) — File manifest for parallel execution.

## Verification

### Project Start (REQUIRED)
- [x] Read `docs/` foundation docs (01_ARCHITECTURE, 02_PATTERNS, 03_CONVENTIONS)
- [ ] Run baseline test suite: `python Tools/test_sharded/test_sharded.py` — all tests pass before Phase 1 begins

### After Each Phase
- [ ] Run `pytest tests/ --testmon` — all affected tests pass
- [ ] Update `Current State` and the Phase row in this file

### Final Verification
- [ ] Manual smoke test: storm hex shows storm effects in Sector panel; combat in storm applies shield interference; hazard tick applies env damage.
- [ ] Combat in two overlapping ion storms applies shield_capacity_mult of 0.5 × 0.5 = 0.25 (MULTIPLY behavior preserved per decisions.md).
- [ ] Strategic-speed reduction: fleet in dark nebula moves at 0.4× speed.
- [ ] Storm detail panel shows name + description only — no per-effect breakdown.
- [ ] Run full test suite: `python Tools/test_sharded/test_sharded.py` clean.
- [ ] **Grep guard:** `grep -r "EnvironmentalEffects\|AreaEffectManager\|StormEffect" game/ tests/` returns zero hits.
- [ ] Verify `docs/systems/strategy_layer.md`, `docs/systems/ability_reference.md`, `docs/02_PATTERNS.md` updated.
- [ ] All phase checklists complete.
- [ ] Audit passed.
- [ ] User verified.
