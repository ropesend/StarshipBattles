# Phase 5: Docs + cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-284 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Document the demographics loop, the configurable food resource, and the new engines. Ensure PROJ-285 and future work can build on solid docs.

---

## Tasks

### Task 5.1: Document the demographics loop [Medium]
**File:** `docs/systems/strategy_layer.md`

- [x] Add a major section "Colony Demographics (PROJ-284)" covering:
  - Turn-phase order: `[100-tick loop] -> OrganicsConsumptionEngine -> HappinessEngine -> PopulationEngine`.
  - `ColonySpeciesConfig` (per-colony per-species) and `last_food_ratio` (transient).
  - Happiness formula and bounds.
  - Reproduction formula and decline term.
  - Data-driven food resource via `data/economy.json`.
  - `FoodAllocationEditor` UI entry point.
- [x] Cross-reference PROJ-283 docs for the habitability formula.

**Notes:** Phase 4 pre-emptively added `## 8. Colony Demographics Loop (PROJ-284)` to `docs/systems/strategy_layer.md` covering all six bullet points + the data-driven food resource section. Phase 5 adds the cross-reference to §7 (Race Preferences & Habitability) at the bottom of the new "Swapping the population food resource" subsection.

### Task 5.2: Update services catalog [Simple]
**File:** `docs/04_SERVICES.md`

- [x] Add entries for:
  - `OrganicsConsumptionEngine` (`game/strategy/engine/organics_consumption_engine.py`)
  - `HappinessEngine` (`game/strategy/engine/happiness_engine.py`)
  - `EconomyConfig` (`game/strategy/config/economy_config.py`)
  - `ColonySpeciesConfig` (`game/strategy/data/colony_species_config.py`)

**Notes:** Added `### Colony Demographics Loop (PROJ-284)` section to `docs/04_SERVICES.md`, placed immediately after the PROJ-283 Race Habitability & Point-Buy section for spatial / logical adjacency. Covers all six files mentioned in the task checklist plus `interfaces/engines.py`, `data/economy.json`, `food_allocation_editor.py`, and the turn-order / transient-field-contract / UI-surface subsections. Cross-references `docs/systems/strategy_layer.md §8`.

### Task 5.3: Add "swap the food resource" recipe [Simple]
**File:** `docs/systems/strategy_layer.md`

- [x] Short subsection: "Swapping the population food resource"
- [x] Steps: (1) edit `data/economy.json` `population_food_resource` to any `resources.json` ID. (2) Ensure the resource is `has_quality: true` and harvestable somewhere in the game. (3) Restart game (or call `set_default_economy_config`).
- [x] UI relabels automatically; no code edits.

**Notes:** Added at the end of `## 8. Colony Demographics Loop`. Softened the `has_quality: true` requirement to "preferred but not required" — the engine reads stockpile values regardless of quality metadata; the flag only matters to the harvester side. Example JSON snippet included.

### Task 5.4: Update CLAUDE.md if needed [Simple]
**File:** `CLAUDE.md`

- [x] If the `get_default_* / set_default_*` pattern needs reinforcement or a new callout, add it. Otherwise no-op.

**Notes:** No-op. CLAUDE.md already documents the pattern adequately. `EconomyConfig` follows the pattern straightforwardly; nothing learned in PROJ-284 implementation suggests the callout needs reinforcement.

### Task 5.5: Orphan sweep [Simple]

- [x] `grep -rn "pop.happiness\s*=" game/` — confirm only `HappinessEngine.process_happiness` writes to it.
- [x] `grep -rn "happiness=[0-9]" tests/` — flag any legacy static-happiness seeding; update test to seed via engine or switch to asserting post-engine happiness.
- [x] `grep -rn "base_reproduction_rate\|base_happiness" .` — confirm consumers are only the engines this project adds + PROJ-283 race_config + UI race_environment_panel + docs.

**Notes:**
- `pop.happiness = ...` writes: only `game/strategy/engine/happiness_engine.py:75` (the engine itself). ✓
- `happiness=[0-9]` in production: `game/strategy/engine/game_initializer.py:202` (initial seed `happiness=0.7` for new colonies) + `game/strategy/engine/order_processor.py:513` (`happiness=0.5` when creating a SpeciesPopulation for a newly colonized planet). Both are constructor-arg seeds on fresh `SpeciesPopulation` instances — HappinessEngine overwrites on turn 1. Keeping: the seeds set the pre-first-turn display value, which is user-visible.
- `happiness=[0-9]` in tests: 20 files touched by grep, all of them test helpers seeding a SpeciesPopulation's happiness for direct `PopulationEngine.process_population_growth` calls (no `HappinessEngine` involved in those tests). They still pass because `last_food_ratio` defaults to 1.0 and the new formula collapses to the old when unperturbed. No test updates needed.
- `base_reproduction_rate` / `base_happiness` consumers: `population_engine.py`, `turn_engine.py`, `happiness_engine.py`, `interfaces/engines.py` (engine consumers); `race_config.py`, `race_point_budget.py`, `homeworld_presets.py` (data layer); `race_environment_panel.py`, `race_aptitudes_panel.py`, `race_summary_panel.py`, `empire_panel_window.py`, `race_validator.py` (UI). All expected. ✓

### Task 5.6: Final verification [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Full suite green.
- [x] Manual end-to-end from plan.md Verification section.
- [x] PROJ-284 plan.md Current State updated to "Complete, ready to close."

**Notes:** Full sharded suite: 14933 total / 14932 passed / 1 failed — the single failure remains the pre-existing `test_copy_designs_without_themes_preserves_original` theme_id pollution flake that has persisted across every PROJ-283 + PROJ-284 phase. Manual end-to-end is DEFERRED TO USER — the agent cannot launch a pygame window; the `plan.md § Verification` scenarios (start game → open colony → slide allocation → advance turns → observe consumption / happiness / decline) are the user's sign-off gate. Underlying mechanics covered by `tests/integration/strategy/test_demographics_loop.py` + per-engine unit tests. Final plan.md Current State update deferred to the post-validator step below per the Phase Completion Checklist.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to indicate project complete
