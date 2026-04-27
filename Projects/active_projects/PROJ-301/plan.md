# PROJ-301: Planet Intrinsic Ability Sources

> **PRECONDITION:** PROJ-300 (Universal IAbilitySource Framework) must be merged before this project starts. This project depends on `IAbilitySource`, `iter_ability_sources_at_hex`, `register_source_provider`, and `aggregate_rates`.

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-301` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-301 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Planet types data registry (helper now in PROJ-300) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. `Planet.intrinsic_abilities` field + generation | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. `PlanetIntrinsicAbilitySource` adapter + iterator registration | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. UI verification + docs | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-04-26
**Active Phase:** Planning (plan approved, awaiting PROJ-300 completion)
**Last Action:** Project documents populated from approved master plan
**Next Action:** Wait for PROJ-300 to land, then begin Phase 1
**Blockers:** PROJ-300 framework
**Context for Next Agent:** Read `Projects/active_projects/PROJ-300/design.md` first to understand the IAbilitySource framework. This project adds **planets themselves** as ability sources — distinct from facilities on planets, which already work after PROJ-300. A planet's intrinsic abilities come from its `planet_type` (desert, volcanic, oceanic, gas_giant, etc.) and may be augmented with generation-time-rolled values.

## Overview

After PROJ-300 lands, the unified ability framework supports facilities (planet complexes) and storms. This project adds **planets-themselves** as a new source kind: a desert world projects sector-scope heat hazards, a gas giant projects gravity-well effects, a volcanic world emits environmental damage. These intrinsic effects are distinct from any complexes built on the planet — both contribute to the same Sector Effects panel.

Some intrinsic ability values are rolled at galaxy creation (e.g. a volcanic planet's `EnvironmentalDamage rate` ranges 0.1–0.5 — exact value rolled when the planet is generated and stored on the instance).

## Goals
- New data registry: `data/planet_types.json` declaring intrinsic ability templates per planet type, with optional `min`/`max` ranges for generation-time rolls.
- `Planet.intrinsic_abilities: Dict[str, Any]` field populated at generation.
- `PlanetIntrinsicAbilitySource` adapter implementing `IAbilitySource`.
- Adapter registered with the iterator so planet intrinsic abilities are picked up automatically by the existing collector pipeline.
- Sector panel shows planet-intrinsic effects as a distinct provider alongside facility and storm providers.
- Save/load roundtrip preserves rolled values.

## Scope

**In:**
- `data/planet_types.json` — schema + initial set of planet types (desert, volcanic, oceanic, gas_giant, terrestrial, ice, barren, lava — match existing planet type enum).
- `Planet.intrinsic_abilities` field, populated by the planet generator from the registry plus rolls.
- `PlanetIntrinsicAbilitySource` adapter in `game/strategy/services/ability_sources/planet_intrinsic.py`.
- Iterator registration so planets-themselves are discovered alongside facilities and storms.
- Tests covering aggregation across planet + facility + storm at the same hex.
- Save/load roundtrip including rolled ability values.
- Documentation update (`docs/systems/strategy_layer.md`, planet-types entry in `docs/systems/ability_reference.md`).

**Out:**
- New abilities not already supported by the framework. Planet intrinsic abilities use existing names (`EnvironmentalDamage`, `StrategicSpeedModifier`, etc.) plus any new ones added in earlier projects.
- Changes to planet types beyond declaring intrinsic abilities. (No new planet-type enum values; existing planet type taxonomy is the input.)
- UI redesign — planet intrinsic effects render through the existing `_add_effects_group` path with `source_kind='planet'`.

## Key Files

| Component | File Path |
|-----------|-----------|
| Planet type registry | `data/planet_types.json` (NEW) |
| Path constant | `game/core/paths.py` (add `PLANET_TYPES_FILE`) |
| Planet dataclass | `game/strategy/data/planet.py` (add `intrinsic_abilities` field) |
| Planet generator | `game/strategy/generation/planet_generator.py` (or wherever planets are built — confirm during Phase 2) |
| Adapter | `game/strategy/services/ability_sources/planet_intrinsic.py` (NEW) |
| Iterator registration | `game/strategy/services/ability_iterator.py` |
| Save/load | Whichever module serializes Planet (likely `game/strategy/data/planet.py` itself) |

## Related Documents
- [design.md](design.md) — Architecture, data schema, adapter shape, generation-time roll mechanism.
- [decisions.md](decisions.md) — Decisions log.
- [manifest.md](manifest.md) — File manifest.
- **PRECONDITION**: [`Projects/active_projects/PROJ-300/`](../PROJ-300/) — Universal IAbilitySource Framework.

## Verification

### Project Start (REQUIRED)
- [ ] PROJ-300 is `Awaiting Verification` or later — confirm before starting
- [ ] Run baseline test suite: `python Tools/test_sharded/test_sharded.py` — all tests pass

### Final Verification
- [ ] Manual smoke test: generate a galaxy, click on a volcanic planet — Sector Effects panel shows `Plasma Damage -0.3/turn — Active (Tarsis IV (Volcanic))` (or similar, with rolled value).
- [ ] On a hex with both a facility (e.g. with `ShieldModifier sector`) and the planet itself projecting an effect, both appear as separate providers under the right effect rows.
- [ ] Save and load — rolled intrinsic ability values are preserved.
- [ ] `pytest tests/ --testmon` clean.
- [ ] All phase checklists complete.
- [ ] User verified.
