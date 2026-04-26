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
| 1. `planet_habitability_multiplier` helper | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Wire into HarvestingEngine | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Wire into ProductionEngine | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Docs + cleanup | Complete | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-04-18
**Active Phase:** ALL 4 PHASES COMPLETE — ready to close. Awaiting user sign-off on `plan.md § Verification` manual scenarios.
**Last Action:** Phase 4 complete. Added `## Habitability Multiplier (PROJ-285)` section to `docs/systems/production_system.md` (formula, edge-case table, per-turn cache contract, booster stacking, backward-compat clause). Added `## 9. Colony Economy Multiplier (PROJ-285)` to `docs/systems/strategy_layer.md` summarizing the PROJ-283 → PROJ-284 → PROJ-285 unified habitability story. Added `### Colony Economy Multiplier (PROJ-285)` to `docs/04_SERVICES.md` cataloging all 5 touched files. CLAUDE.md no-op per task 4.4. Full sharded suite: 14966 / 14965 passed / 1 failed — persistent theme_id flake. Validator PASS on all 4 phases.

**Shipped across all phases:**
- Phase 1: `planet_habitability_multiplier(planet, race_registry)` at `game/strategy/formulas/colony_output.py` — population-weighted mean with save-drift defence (missing races excluded, not zeroed). Per-turn cache on `Planet.get_cached_habitability_multiplier(race_registry, turn)` — `init=False, compare=False, repr=False` fields, not serialized. 18 unit tests.
- Phase 2: `HarvestingEngine.__init__(registries, race_registry=None)` kwarg + `_get_habitability_mult(colony)` helper. Hook in `_harvest_resource` multiplies AFTER quality + booster, BEFORE tick_fraction. `set_current_turn(turn)` API + `TurnEngine.process_turn` wired to call it at turn start. 12 new tests (7 unit + 5 integration) + zero churn on 27 legacy MagicMock-based tests.
- Phase 3: `ProductionEngine.__init__(registries, race_registry=None)` kwarg + matching `_get_habitability_mult` helper. Hook in `_process_queue_tick_dynamic` scales the `production_rate` dict before the tick-capacity while-loop — downstream math honors the multiplier automatically. Fleet queues always get 1.0. 10 new tests (8 unit + 2 integration extension).
- Phase 4: Three docs updated (production_system.md, strategy_layer.md, 04_SERVICES.md) + CLAUDE.md no-op. Full sharded suite green apart from the persistent theme_id flake.

**Next Action:** USER SIGN-OFF. Launch the game, colonize an ideal planet + a hostile planet, advance turns, verify the `plan.md § Verification` manual scenarios (95% rate on ideal, 20% on hostile, weighted average on multi-species, no penalty on uncolonized extractor sites). When satisfied, move project folder to `Projects/archived_projects/PROJ-285/`.

**Blockers:** None.

**Context for Next Agent (if reopened):**
- `planet_habitability_multiplier` is the single source of truth for colony habitability scaling in economic formulas. Adding a new economic side effect (e.g. resupply fuel generation — explicitly deferred in scope) should reuse the helper + per-turn cache via `colony.get_cached_habitability_multiplier(race_registry, turn)`.
- Both engines default `race_registry=None` → multiplier=1.0. Any engine re-wiring that passes a race_registry will activate the habitability scaling; legacy callers (850+ lines of MagicMock planets in `test_harvesting_engine.py` + `tests/unit/strategy/production_engine/`) remain untouched and green.
- Per-turn cache lives ONLY on Planet (not the engines). Multiple engines hitting the same colony in the same turn share ONE computation — verified by `test_harvest_and_production_share_planet_cache` in `tests/unit/strategy/production_engine/test_habitability.py`.
- Missing-race defensive behavior: species with `race_id` absent from the registry are EXCLUDED from both numerator and denominator. A save with a known-race + unknown-race colony scores as 100% known-race for the multiplier. This was a deliberate design choice (documented in `colony_output.py` module docstring) — the simpler alternative of scoring missing-race as 0 would silently collapse empire economies under save drift.
- Docs cross-reference chain: `04_SERVICES.md` → `production_system.md § Habitability Multiplier` (full formula + edge cases) + `strategy_layer.md §9` (summary + unified PROJ-283/284/285 story).
- Persistent sharded-runner flake: `test_copy_designs_without_themes_preserves_original` (theme_id pollution). Followed every phase of PROJ-283, PROJ-284, PROJ-285. Passes in isolation. NOT a regression — predates the PROJ-28X work.

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
