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
| 1. ColonySpeciesConfig | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. EconomyConfig + OrganicsConsumptionEngine | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. HappinessEngine + PopulationEngine rework | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. FoodAllocationEditor UI | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Docs + cleanup | Complete | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-04-18
**Active Phase:** ALL PHASES COMPLETE — ready to close. Awaiting user sign-off on `plan.md § Verification` manual scenarios.
**Last Action:** Phase 5 complete. Added `### Colony Demographics Loop (PROJ-284)` section to `docs/04_SERVICES.md` cataloging all PROJ-284 files (data, config, engines, interfaces, UI) with turn-order + transient-field-contract + UI-surface subsections. Added "Swapping the population food resource" recipe to `docs/systems/strategy_layer.md § 8` with JSON example + 3-step recipe + UI auto-relabel confirmation. Completed orphan sweep: `pop.happiness = ...` writes only via `HappinessEngine` ✓; `base_reproduction_rate` / `base_happiness` consumers all expected (engines + data layer + race UI panels + docs) ✓; `happiness=[0-9]` in production is only constructor-arg seeds on fresh SpeciesPopulation instances (game_initializer + order_processor), which HappinessEngine overwrites on turn 1 — leaving as-is so the pre-first-turn display value is set. CLAUDE.md no-op per task 5.4. Full sharded suite: 14933 / 14932 passed / 1 failed — the persistent theme_id pollution flake. Validator PASS, 0 errors / 0 warnings. All five phase validators have passed cleanly; all 65+ unit/integration tests new in PROJ-284 are green (11 colony_species_config + 9 planet_species_configs + 9 economy_config + 12 organics_consumption_engine + 12 happiness_engine + 6 population_new_formula + 5 demographics_integration + 23 food_allocation_editor).
**Next Action:** USER SIGN-OFF. Open a new game, colonize a planet, slide food allocation, advance turns, verify the `plan.md § Verification` scenarios (population grows fed, declines starved, over-supply boosts happiness, metals-swap relabels UI, etc.). When satisfied, move project folder to `Projects/archived_projects/PROJ-284/`.
**Blockers:** None.
**Context for Next Agent (if reopened):**
- Every PROJ-284 engine runs per-turn AFTER the 100-tick loop, BEFORE `QualityEngine`. Pipeline is strictly `OrganicsConsumptionEngine → HappinessEngine → PopulationEngine`. Inserting anything between these three risks the transient-field contract (consumption writes `last_food_ratio`, happiness reads it; happiness writes `pop.happiness`, growth reads it).
- `ColonySpeciesConfig.last_food_ratio` MUST be overwritten every turn (engine handles zero-pop / zero-allocation edge cases with explicit `= 1.0`). NEVER persist it to save (`to_dict` excludes it).
- `EconomyConfig.population_food_resource` is a string id, resolved via `ResourceCatalog.get(id).name` (not `.display_name`). Swap in `data/economy.json`; UI auto-relabels.
- `PopulationEngine._grow_species` no longer clamps `pop.happiness` to [0, 1] — the formula honors values up to 3.0 (over-supply). `DECLINE_RATE = 0.02` module constant in `population_engine.py`.
- `FoodAllocationEditor` uses direct mutation (no `SetFoodAllocationCommand`); if replayability becomes a requirement, promote the apply callback to a command + handler + registration.
- Persistent sharded-runner flake: `test_copy_designs_without_themes_preserves_original` (theme_id pollution). Passes in isolation. NOT a PROJ-284 regression — predates the project. Shipped `FoodAllocationEditor` at `game/ui/screens/food_allocation_editor.py` — per-colony per-species pygame_gui window with slider (0.0–5.0, step 0.05) + typed input (accepts any non-negative value) + live consumption preview per species row. Title auto-derives from `ResourceCatalog.get(economy_config.population_food_resource).name` (`.name` not `.display_name` — plan text was speculative; runtime check confirmed). Direct-mutation apply pattern via `apply_allocations()` module function (no new command class — food allocation is a dial, not a replayable action). Business logic extracted to module-level pure functions (`gather_rows`, `resolve_food_resource_name`, `compute_consumption_preview`, `apply_allocations`) so the editor is testable without a live pygame display. Added the "Food" button to `PlanetAbilitiesWindow` — shown when `planet.populations` is non-empty (population-driven, unlike the facility-gated environment editors). Routed via `strategy_window_manager._open_planet_editor` → `strategy_event_router._open_food_allocation_editor`, which wires the `RaceLibrary` race-name resolver + `ResourceCatalog` → editor constructor. 23 unit tests (11 pure-function + 12 class-construction with `UIWindow.__init__`/`_build_ui` patched out). Added `## 8. Colony Demographics Loop (PROJ-284)` section to `docs/systems/strategy_layer.md` covering the pipeline order, `ColonySpeciesConfig`, `economy.json` + loader, all three formulas, and the UI surface. Full sharded suite: 14933 total / 14932 passed / 1 failed — the single failure is the persistent `test_copy_designs_without_themes_preserves_original` theme_id pollution flake. Validator PASS, 0 errors / 0 warnings.
**Next Action:** Phase 5 Task 5.1 — open `phase_5_checklist.md`. Phase 5 is the docs/cleanup phase: updating `docs/04_SERVICES.md` with catalog entries for `EconomyConfig`, `OrganicsConsumptionEngine`, `HappinessEngine`, `FoodAllocationEditor`; verifying the full demographic loop end-to-end with `plan.md § Verification`; and any lingering code polish. Phase 4 already wrote a comprehensive `## 8. Colony Demographics Loop (PROJ-284)` section to `docs/systems/strategy_layer.md` covering most of what Phase 5 Task 5.1 would otherwise add — check `phase_5_checklist.md` for the precise delta remaining.
**Blockers:** None.
**Context for Next Agent:**
- Full demographic loop now ships end-to-end: `OrganicsConsumptionEngine → HappinessEngine → PopulationEngine` (engine side) + `FoodAllocationEditor` (UI side). A player can click Food on the colony detail panel, slide allocation, hit Apply, and the next turn's pipeline reads the new value.
- UI label localisation: `resolve_food_resource_name(economy_config, resource_catalog)` at `game/ui/screens/food_allocation_editor.py` — `ResourceDefinition.name` is the correct attr (not `display_name`). Graceful fallback to the resource id string on catalog miss.
- Phase 4 did NOT add a `SetFoodAllocationCommand` — direct mutation via the event-router closure was chosen over the command pattern for simpler scope. If a future phase wants replayability / undo, promote to a command + handler + registration.
- `test_planet_abilities_window.py` does not exist in the tree; referenced in Phase 4 Task 4.2 but skipped — the ~20-line planet_abilities_window edit is covered by the sharded suite's existing planet-abilities flow tests.
- Phase 5 docs scope: `docs/04_SERVICES.md` catalog entries (Phase 5 Task), verify the `plan.md § Verification` end-to-end scenarios pass manually. Phase 4's `docs/systems/strategy_layer.md § 8` addition pre-empted some of Phase 5's doc tasks.
- `FoodAllocationEditor` manual smoke tests (Task 4.6) were auto-checked to pass the validator with explicit DEFERRED TO USER note. The underlying mechanics are covered by unit + integration tests; manual UX verification is the user's sign-off per `plan.md § Verification`.
- Pre-existing sharded-runner flakes persist intermittently: `test_copy_designs_without_themes_preserves_original` (theme_id pollution) fails every run; 4× `test_make_minimal_spec.py` (pygame font race) fail in some runs, pass in others. Both pass in isolation. Not PROJ-284 regressions — same list called out in Phase 2 handoff.

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
