# PROJ-284: Colony Demographics Loop (Organics, Happiness, Population Growth Rework)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-284` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-284 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. ColonySpeciesConfig | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. EconomyConfig + OrganicsConsumptionEngine | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. HappinessEngine + PopulationEngine rework | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. FoodAllocationEditor UI | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Docs + cleanup | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-04-18
**Active Phase:** Blocked on PROJ-283 completion
**Last Action:** Project scaffolded from master plan at `C:\Users\rossr\.claude\plans\i-want-to-effervescent-hennessy.md`
**Next Action:** Wait for PROJ-283 to complete (provides `base_reproduction_rate`, `base_happiness`, new `RaceConfig.preferences`). Then begin Phase 1.
**Blockers:** PROJ-283 must complete first. Depends on `base_reproduction_rate: float` and `base_happiness: float` fields, plus the new `preferences`-based habitability formula.
**Context for Next Agent:** This is the gameplay-visible half of the rework. Once it lands, the player can: set a food-allocation slider per species per colony, see happiness rise and fall with habitability and food supply, watch populations decline from starvation. Organics is the default population-food resource but the resource is read from `data/economy.json` so a modder can swap it with a one-line edit. Happiness is fully derived each turn — the `SpeciesPopulation.happiness` field becomes a write-only cache populated by the new `HappinessEngine`.

## Overview

Introduce the full demographic loop: per-colony per-species food allocation, data-driven food consumption, derived happiness, and a reworked population-growth formula that responds to food + habitability + base rates.

Depends on PROJ-283 (foundation). Parallel-safe with PROJ-285 (production-rate hooks).

## Goals
- Store per-colony per-species slider state in a new `ColonySpeciesConfig` dataclass hung off `Planet.species_configs`.
- Drive population food consumption from `data/economy.json` so swapping from `organics` to any other resource is a one-line data edit.
- Add `OrganicsConsumptionEngine` that drains the food resource per turn, computes `last_food_ratio = supplied / needed`, applies starvation (population decline + happiness penalty) when < 1.0.
- Derive happiness each turn via new `HappinessEngine`: `happiness = clamp(base_happiness * last_food_ratio * habitability_score, 0, 3)`.
- Rework `PopulationEngine` logistic growth to use `base_reproduction_rate * last_food_ratio` and include the decline term.
- Add `FoodAllocationEditor` UI per colony per species, mirroring `atmosphere_target_editor.py`.
- Label text auto-generated from the configured food resource's display name.
- Starvation semantics (user-confirmed): proportional population decline + happiness penalty.

## Scope
**In:**
- `ColonySpeciesConfig` dataclass attached to `Planet.species_configs: Dict[race_id, ColonySpeciesConfig]`.
- `data/economy.json` + `game/strategy/config/economy_config.py` loader.
- `OrganicsConsumptionEngine` wired into `TurnEngine` between harvesting and happiness.
- `HappinessEngine` wired into `TurnEngine` between consumption and population growth.
- `PopulationEngine` rework using `base_reproduction_rate * last_food_ratio` + decline term for underfeed.
- `FoodAllocationEditor` colony UI screen.
- Tests for each engine, the config storage, the editor, and end-to-end demographic loop.
- Docs updates.

**Out:**
- New habitability factors / race setup UI -> PROJ-283.
- Habitability multiplier on harvesting/production rates -> PROJ-285.
- Save-game migration.

## Key Files
| Component | File Path |
|-----------|-----------|
| NEW ColonySpeciesConfig dataclass | `game/strategy/data/colony_species_config.py` |
| Planet entity (holds species_configs dict) | `game/strategy/data/planet.py` |
| NEW economy.json | `data/economy.json` |
| NEW EconomyConfig loader | `game/strategy/config/economy_config.py` |
| NEW OrganicsConsumptionEngine | `game/strategy/engine/organics_consumption_engine.py` |
| NEW HappinessEngine | `game/strategy/engine/happiness_engine.py` |
| PopulationEngine rework | `game/strategy/engine/population_engine.py` |
| TurnEngine phase wiring | `game/strategy/engine/turn_engine.py` |
| NEW FoodAllocationEditor UI | `game/ui/screens/food_allocation_editor.py` |
| Docs | `docs/systems/strategy_layer.md`, `docs/04_SERVICES.md` |

## Architectural overview (from master plan)

- **Per-colony-per-species config.** `ColonySpeciesConfig(food_allocation: float = 1.0, last_food_ratio: float = 1.0 [transient])` stored as `Planet.species_configs: Dict[race_id, ColonySpeciesConfig]`. `SpeciesPopulation` stays pure runtime state; config stays separate.
- **Data-driven food resource.** `data/economy.json` holds `{"population_food_resource": "organics", "food_per_pop_per_turn": 0.001}`. Loader uses the standard `get_default_* / set_default_*` module accessor pattern (CLAUDE.md).
- **Turn order (after this project ships):** harvesting -> organics-consumption -> happiness -> population-growth. Organics consumption writes `last_food_ratio` consumed by happiness, which writes `happiness` consumed by population growth.
- **Happiness formula:** `happiness = clamp(race.base_happiness * config.last_food_ratio * habitability, 0, 3)` — unbounded above so the organics slider can genuinely over-supply.
- **Reproduction formula:** `growth = (race.base_reproduction_rate * config.last_food_ratio) * pop * (1 - pop / K_eff) * happiness`, `K_eff = max_population * habitability`. Starvation adds a decline term: `-decline_rate * pop * (1 - last_food_ratio)` when `last_food_ratio < 1` (tunable, recommend 0.02).
- **Food allocation slider**: range 0 to large (recommend UI-capped at 5.0 with typed input for higher). Default 1.0. Linearly scales both consumption and effective-reproduction / happiness.

## Reused existing utilities

- `atmosphere_target_editor.py` UI pattern — mirrored by the new `food_allocation_editor`.
- `ResourceCatalog.get(id)` from `game/core/resources.py` — resolves the configured food resource's display name for UI labels.
- `PopulationEngine.score_planet_for_race` — habitability score (registry-driven after PROJ-283).
- `get_default_* / set_default_*` module accessor pattern (CLAUDE.md).

## Related Documents
- [design.md](design.md) — Architecture analysis
- [decisions.md](decisions.md) — Decisions log
- [manifest.md](manifest.md) — Full file manifest

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing via `python Tools/test_sharded/test_sharded.py`
- [ ] End-to-end manual scenario (from master plan):
  - [ ] Start a game; open colony detail; see per-species food-allocation slider (default 1.0).
  - [ ] Advance 5 turns. Happiness stabilizes near `base_happiness * 1.0 * habitability ≈ expected`.
  - [ ] Organics stockpile drains at `pop * 1.0 * food_per_pop` per turn.
  - [ ] Slide species allocation to 2.0: consumption doubles, happiness bumps.
  - [ ] Starve a colony (empty stockpile): `last_food_ratio` falls -> happiness drops -> population declines.
  - [ ] Colonize a planet with habitability < 0.2 -> happiness collapses, population declines over turns.
- [ ] Swap `data/economy.json` to `{"population_food_resource": "metals"}` — confirm the FoodAllocationEditor relabels to "Metals allocation" without code changes and metals drains per turn.
- [ ] Docs updated: `docs/systems/strategy_layer.md` documents turn-phase order, happiness formula, reproduction formula, and food-resource swap mechanism; `docs/04_SERVICES.md` has entries for the new engines + config.
- [ ] User verified end-to-end.
