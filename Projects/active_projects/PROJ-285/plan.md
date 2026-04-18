# PROJ-285: Habitability-to-Production Economy Hook

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-285` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-285 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. `planet_habitability_multiplier` helper | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Wire into HarvestingEngine | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Wire into ProductionEngine | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Docs + cleanup | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-04-18
**Active Phase:** Blocked on PROJ-283 completion
**Last Action:** Project scaffolded from master plan at `C:\Users\rossr\.claude\plans\i-want-to-effervescent-hennessy.md`
**Next Action:** Wait for PROJ-283 (depends on registry-driven habitability formula). Then begin Phase 1.
**Blockers:** PROJ-283 must complete first (depends on `calculate_habitability(planet, race_config)` using the registry). Can run in parallel with PROJ-284 after PROJ-283 lands.
**Context for Next Agent:** Tiny project — one helper, two call-site edits, one docs update. The test work is larger than the code work because it must recalibrate existing harvest/production tests that implicitly assumed habitability=1.0. New helper goes in `game/strategy/formulas/colony_output.py`. Population-weighted average because multiple species on a planet means different species see different habitability scores.

## Overview

Plug habitability into the economy: a colony's harvest and production rates scale with how livable the planet is for its resident species. New helper `planet_habitability_multiplier(planet, race_registry) -> float` returns the population-weighted mean habitability across species on the planet, injected at the base-rate resolution step in `HarvestingEngine._harvest_resource` and `ProductionEngine._process_queue_tick_dynamic`.

Depends on PROJ-283 (registry-driven habitability formula). Parallel-safe with PROJ-284.

## Goals
- New helper `planet_habitability_multiplier(planet, race_registry) -> float` using population-weighted mean habitability.
- Multiply into the base rate during harvest (after existing booster aggregation, before `tick_fraction`).
- Multiply into the base rate during production (after booster aggregation, per-tick expenditure calculation).
- Update existing harvest and production tests to either use an "ideal planet/race" fixture (preserving existing numeric expectations) or explicitly assert the new multiplier's effect.
- Document the behavior and the "population-weighted" choice.

## Scope
**In:**
- `planet_habitability_multiplier` helper in `game/strategy/formulas/colony_output.py`.
- `HarvestingEngine._harvest_resource` hook: one multiply.
- `ProductionEngine._process_queue_tick_dynamic` hook: one multiply.
- Unit tests for the helper (including the population-weighted math and multi-species cases).
- Updated unit tests for harvesting + production (ideal-planet fixtures keep old numbers; or explicit habitability-checking tests).
- Integration test: hostile-planet colony produces substantially less than ideal-planet colony.
- Docs update.

**Out:**
- Resupply fuel generation (deferred — user didn't explicitly request).
- Happiness-as-production-factor (deferred — happiness affects growth in PROJ-284 only).
- Race setup, colony-per-species config, organics consumption -> PROJ-283 / PROJ-284.

## Key Files
| Component | File Path |
|-----------|-----------|
| NEW `planet_habitability_multiplier` helper | `game/strategy/formulas/colony_output.py` |
| Harvest hook | `game/strategy/engine/harvesting_engine.py` |
| Production hook | `game/strategy/engine/production_engine.py` |
| Docs | `docs/systems/strategy_layer.md`, `docs/systems/production_system.md`, `docs/04_SERVICES.md` |

## Architectural overview (from master plan)

- **Population-weighted average** (user-confirmed): for a planet with multiple species, `multiplier = Σ (pop.count * habitability(planet, race)) / Σ pop.count`. Larger species' habitability counts proportionally more.
- Edge case: planet with no populations (uncolonized extractor sites, temporary fleet-owned outposts if any) -> multiplier=1.0 (no habitability penalty; nothing to be unhappy).
- The habitability score is registry-driven (PROJ-283 output); this project does not recompute.
- Multiplier stacks multiplicatively with existing `BuildRateBooster` / `ResourceHarvestBooster` — those already use `aggregate_multipliers()` internally; habitability applies as one more term.

## Reused existing utilities

- `score_planet_for_race(planet, race_config)` from PROJ-283's registry-driven `habitability.py`.
- `aggregate_multipliers()` pattern from `strategic_ability_scanner.py` — unchanged. Habitability multiplier stacks alongside.
- `RaceLibrary.get_race(race_id)` — resolve race_config from race_id on population entries.

## Related Documents
- [design.md](design.md) — Architecture analysis
- [decisions.md](decisions.md) — Decisions log
- [manifest.md](manifest.md) — Full file manifest

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing via `python Tools/test_sharded/test_sharded.py`
- [ ] Manual scenario:
  - [ ] Colony on ideal planet (habitability 0.95) produces metals at ~95% of raw rate.
  - [ ] Colony on hostile planet (habitability 0.2) produces metals at ~20% of raw rate.
  - [ ] Multi-species colony (70% happy species, 30% sad species) produces at weighted average.
  - [ ] Uncolonized world (no pops, automated extractor) — no habitability penalty applied.
- [ ] Docs updated: `production_system.md` + `strategy_layer.md` cover the multiplier; formula documented.
- [ ] User verified end-to-end.
