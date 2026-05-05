# Handoff: PROJ-284 — Phase 2 (EconomyConfig + OrganicsConsumptionEngine)

Resume **PROJ-284** at **Phase 2**. The previous session closed Phase 1 cleanly (validator PASS, 0 errors / 0 warnings; full sharded suite 14845/14850 — 5 failures are all pre-existing flakes from the PROJ-283 era, unrelated). Stopping at the phase boundary preserves a full-cache start for Phase 2, which is the substantive engine-wiring work.

## Orientation (read BEFORE touching the project plan)

The instinct is to open `plan.md` first. Resist it. The project plan assumes you understand the surrounding architecture, conventions, and related code — if you don't, you'll make short-sighted decisions that the plan's author took for granted. Prefer loading extra context.

### 1. Foundation docs (always read these first)
- `docs/README.md` — doc index + task-driven reading order
- `docs/01_ARCHITECTURE.md` — layer structure + package APIs + dependency rules
- `docs/02_PATTERNS.md` — design patterns used in this codebase. **Read Pattern 12 ("Configuration Classes") carefully** — the strategy-layer data-driven config pattern (JSON-backed + `@lru_cache` getter + graceful default fallback) is exactly the pattern Phase 2's `EconomyConfig` should follow.
- `docs/03_CONVENTIONS.md` — naming, file org, test conventions, line budgets
- `CLAUDE.md` — three non-negotiable rules (TDD, docs-in-sync, clean-sheet design) + the `get_default_* / set_default_*` module accessor pattern (Phase 2 Task 2.2 uses this)

### 2. Task-specific docs
- `docs/systems/strategy_layer.md` — especially `### Turn Engine` (§3), `### Atmosphere Modification Pipeline`, and the `### Water Modification Pipeline` sections; they show the existing engine + per-turn processing conventions. `### Planet Energy System (PROJ-237/238)` shows a similar "per-turn state mutation" pattern.
- `docs/04_SERVICES.md` — service-layer catalog; shows how `game/strategy/data/*.py` and `game/strategy/config/*.py` files are documented (see the new "Race Habitability & Point-Buy (PROJ-283)" section for the most recent example of a data-model-focused catalog entry).

### 3. Related code (read for context, even if you won't modify it)

**PROJ-284 Phase 1 outputs (define the contract Phase 2 consumes):**
- `game/strategy/data/colony_species_config.py` — `ColonySpeciesConfig(food_allocation=1.0, last_food_ratio=1.0)`. `to_dict` excludes the transient `last_food_ratio`. `from_dict` always resets it to 1.0. `__post_init__` validates `food_allocation >= 0`. Phase 2's consumption engine reads `food_allocation` from each config and writes `last_food_ratio = supplied / needed` back.
- `game/strategy/data/planet.py:217-225` — `Planet.get_species_config(race_id) -> ColonySpeciesConfig` lazy-create-and-store helper. Phase 2 should call this per-species-per-colony inside the consumption loop. `Planet.species_configs` is the dict; `Planet.populations: List[SpeciesPopulation]` is the population list (each `SpeciesPopulation` has `race_id`, `count`, `happiness`).
- `tests/unit/strategy/data/test_colony_species_config.py` + `test_planet_species_configs.py` — 20 tests total. Read to understand the round-trip contract + lazy-create semantics before modifying.

**PROJ-283 outputs (API Phase 3 consumes — not Phase 2):**
- `game/strategy/formulas/habitability.py` — `score_planet_for_race(planet, race_config) -> float in [0,1]`. Phase 3's `HappinessEngine` formula `happiness = clamp(base_happiness * last_food_ratio * habitability, 0, 3)` needs this. Not needed for Phase 2.
- `game/strategy/data/race_config.py` — `RaceConfig.base_reproduction_rate: float = 0.03`, `RaceConfig.base_happiness: float = 0.5`. Phase 3 reads both. Phase 2 doesn't touch them.

**Phase 2 modification targets (read BEFORE editing):**
- `game/strategy/engine/turn_engine.py` — **THIS is the critical file**. Phase 2 Task 2.6 inserts `OrganicsConsumptionEngine.process_consumption(empires)` AFTER the 100-tick loop, BEFORE the existing `PopulationEngine.process_population_growth` call. Read `process_turn()` end-to-end to find the right slot. The engine should be a constructor-injected dependency (matches existing DI pattern — see `TurnEngineConfig` in `docs/02_PATTERNS.md` Pattern 22).
- `game/strategy/engine/population_engine.py` — read it to understand the existing "process after the 100-tick loop" pattern. PROJ-283 Phase 4 already rewired this to read `race_config.base_reproduction_rate` directly. Phase 3 reworks the formula further; Phase 2 does NOT modify this file.
- `game/strategy/interfaces/engines.py` — Task 2.6 sub-point says "Add `IOrganicsConsumptionEngine` protocol for DI consistency." Read the file first; if protocols for other engines are there, follow the convention. If not, either skip or add a bare minimum.

**Configuration pattern references (read to get the pattern right):**
- `game/strategy/data/classification_config.py` — `ClassificationConfig` with `_load_from_json`, `_use_defaults`, `@lru_cache` getter, graceful fallback. **Your `EconomyConfig` should mirror this pattern.** But note: PROJ-284's plan uses `get_default_economy_config` / `set_default_economy_config` (module accessor) rather than `@lru_cache` — choose: either match the existing data-driven config pattern (`@lru_cache`) or match the CLAUDE.md module-accessor pattern. The plan leans module-accessor; `ClassificationConfig` leans `@lru_cache`. Probably fine either way — pick one, justify in decisions.md.
- `data/astrophysics.json` — example of a strategy-layer data-driven JSON file. `data/economy.json` (Task 2.1) will be much simpler (just 2 keys).

### 4. Related tests (read so you know what "working" looks like)
- `tests/unit/strategy/data/test_colony_species_config.py` — Phase 1 test file. Shape your Phase 2 tests similarly (class-per-concern, descriptive names).
- `tests/unit/strategy/data/test_planet_species_configs.py` — uses a `_minimal_planet(**overrides)` helper to construct `Planet` with the smallest set of valid fields. The Phase 2 `OrganicsConsumptionEngine` tests will need to build mock empires → colonies → populations; either reuse `create_test_empire` / `create_test_planet` from `tests/fixtures/strategy_entities.py`, or write minimal inline stubs. Prefer the fixtures if they're lightweight.
- `tests/unit/strategy/engine/test_population_engine.py` — read the `make_human_race_config` helper (PROJ-283 Phase 4 migrated it to use `base_reproduction_rate`). Your Phase 2 tests will need similar builders for empires/colonies/populations.
- `tests/unit/strategy/data/classification_config` tests (if any) — look for the `@lru_cache.cache_clear()` pattern in setup/teardown; Phase 2's `EconomyConfig` tests will need similar isolation if you use `@lru_cache`.

## Only now: read the project files
Read in this order — the plan depends on all of the above:
1. `Projects/active_projects/PROJ-284/design.md` — architectural rationale
2. `Projects/active_projects/PROJ-284/decisions.md` — full decision log including 4 entries confirming PROJ-283's handoff API (API is stable: `base_reproduction_rate`, `base_happiness`, `score_planet_for_race`, registry-driven `preferences`)
3. `Projects/active_projects/PROJ-284/plan.md` § **Current State** — authoritative handoff (updated end of Phase 1)
4. `Projects/active_projects/PROJ-284/phase_2_checklist.md` — Phase 2 task list (7 tasks)
5. `Projects/active_projects/PROJ-284/manifest.md` — file manifest with Phase 1 ✓ markers

## First action
Open `phase_2_checklist.md`. The literal next unchecked item is:

> **Task 2.1: Author `data/economy.json` [Simple]**
> - [ ] Author:
>   ```json
>   {
>     "population_food_resource": "organics",
>     "food_per_pop_per_turn": 0.001
>   }
>   ```
> - [ ] Document the schema at the top of `docs/systems/strategy_layer.md` in Phase 5.

TDD ordering recommendation:
1. Write `test_economy_config.py` first (Task 2.3) — a test that tries to load `data/economy.json` and asserts the defaults. It'll fail because neither the JSON nor the loader exist yet.
2. Author `data/economy.json` (Task 2.1).
3. Write the loader (Task 2.2). Test should pass.
4. Write `test_organics_consumption_engine.py` (Task 2.5) — 7 test scenarios from the checklist.
5. Write `organics_consumption_engine.py` (Task 2.4). Scenarios should pass.
6. Wire into `TurnEngine` (Task 2.6). Don't wire HappinessEngine yet — Phase 3.
7. Run full sharded suite.

## Watchouts (from Phase 1 + cross-project)

1. **`last_food_ratio` is TRANSIENT**: `ColonySpeciesConfig.to_dict` excludes it; `from_dict` always resets to 1.0. Phase 2's engine MUST overwrite it every turn — don't rely on the cached value from a previous turn existing after save/load. Recommended: if `needed == 0` (zero-pop edge case), explicitly write `last_food_ratio = 1.0` so downstream readers (HappinessEngine, PopulationEngine) don't see stale values.

2. **Food resource lookup**: `economy_config.population_food_resource` is a STRING id (e.g., `"organics"`). UI labels must resolve via `ResourceCatalog.get(id).display_name` — NEVER hardcode "Organics" outside `economy.json`. This is the whole point of the data-driven design: a modder edits the JSON and the label auto-updates.

3. **`get_default_* / set_default_*` vs `@lru_cache` getter**: CLAUDE.md says use `get_default_* / set_default_*`; Pattern 12 (Configuration Classes) shows the strategy-layer data-driven configs use `@lru_cache`. The PROJ-284 plan text leans toward the former. Pick one, document the choice in `decisions.md`. If you pick `@lru_cache`, remember tests must call `.cache_clear()` in setup/teardown.

4. **DI pattern for `TurnEngine`**: the existing engine-DI pattern uses `TurnEngineConfig` (Pattern 22 in docs/02_PATTERNS.md). Your new `OrganicsConsumptionEngine` should be either an optional `TurnEngineConfig` field or a kwarg to `TurnEngine.__init__`. Read the existing structure before choosing. Prefer `TurnEngineConfig` for consistency.

5. **Phase order**: `[100-tick loop] → OrganicsConsumptionEngine → PopulationEngine`. Phase 3 slots `HappinessEngine` between consumption and population. Don't wire `HappinessEngine` in Phase 2.

6. **Old saves**: `Planet.from_dict` already handles missing `species_configs` (defaults to empty dict); `EconomyConfig` loader needs to handle missing `data/economy.json` (return defaults). Don't write migration code — per CLAUDE.md System Migration Policy, save files are disposable.

7. **Pre-existing sharded-runner flakes**: `tests/fixtures/test_make_minimal_spec.py` (4 tests) and `tests/unit/quickstart/test_quickstart_builder.py::TestQuickstartBuilderDesignCopying::test_copy_designs_without_themes_preserves_original` flake occasionally in sharded runs due to test pollution; pass in isolation. These are NOT PROJ-284 regressions. Persistently identified across every PROJ-283 phase + PROJ-284 Phase 1.

8. **Context budget**: Phase 2 is 7 tasks ≈ 40-60k token work. Current-session scale: Phase 1 consumed roughly 30-40k (including full sharded suite run). Phase 3 is similarly sized. You likely won't finish both Phase 2 AND Phase 3 in one cache — stop cleanly at Phase 2 boundary if `check_context.py` shows you approaching 80%.

## Protocol
Follow `Projects/protocols/03a_continue_working.md`. The new guidance (2026-04-18): "Phase completion is a checkpoint, not an exit condition. If the next phase looks too big to fit under 80%, split it." Phase 2 is cohesive and splitting mid-phase creates awkward validator state — if you can fit it, do so; otherwise stop at a phase boundary. Run `python Projects/scripts/validate_phase.py PROJ-284 2` before stopping.
