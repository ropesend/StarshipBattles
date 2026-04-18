# Phase 3: HappinessEngine + PopulationEngine rework

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-284 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add `HappinessEngine` that derives happiness each turn from base_happiness * last_food_ratio * habitability. Rework `PopulationEngine` to use `base_reproduction_rate * last_food_ratio` and include a starvation-decline term.

---

## Tasks

### Task 3.1: `HappinessEngine` [Medium]
**File:** `game/strategy/engine/happiness_engine.py` (NEW)
**Tests:** `pytest tests/unit/strategy/engine/test_happiness_engine.py`

- [x] Define:
  ```python
  class HappinessEngine:
      def process_happiness(self, empires, galaxy) -> None:
          for empire in empires:
              for colony in empire.colonies:
                  for pop in colony.populations:
                      race_config = _resolve_race_config(empire, pop.race_id)
                      if race_config is None:
                          continue
                      habitability = score_planet_for_race(colony, race_config)
                      config = colony.get_species_config(pop.race_id)
                      raw = race_config.base_happiness * config.last_food_ratio * habitability
                      pop.happiness = max(0.0, min(3.0, raw))
  ```
- [x] Clamp bounds `[0, 3]` — unbounded above 1.0 so over-supply + good habitability can boost.
- [x] Reuse existing `_get_race_config` helper logic from `PopulationEngine` (factor it to a shared util if clean).

**Notes:** Implements `IHappinessEngine` (new protocol). Kept `_get_race_config` as a method on both `HappinessEngine` and `PopulationEngine` rather than extracting to a shared module — identical to a resolver helper either way, and leaving it as a method preserves the existing `PopulationEngine` tests that monkey-patch `engine._get_race_config`. Module constants `HAPPINESS_MIN = 0.0` / `HAPPINESS_MAX = 3.0` name the clamp bounds. Precondition validation (`_validate_tick_inputs`) rejects `None` colonies with `ValidationException` carrying empire context (Pattern 20).

### Task 3.2: HappinessEngine tests [Medium]
**File:** `tests/unit/strategy/engine/test_happiness_engine.py` (NEW)
**Tests:** `pytest tests/unit/strategy/engine/test_happiness_engine.py`

- [x] Ideal planet, food_ratio=1.0, base_happiness=0.5 -> happiness ≈ 0.5 * habitability ≈ 0.5 (planet ideal).
- [x] Ideal planet, food_ratio=2.0, base_happiness=0.5 -> happiness ≈ 1.0.
- [x] Hostile planet (habitability 0.1), food_ratio=1.0, base_happiness=0.5 -> happiness ≈ 0.05.
- [x] Starving (food_ratio=0), any other conditions -> happiness = 0.0.
- [x] Over-supplied ideal planet (food_ratio=5.0, base=0.6) -> happiness clamped at 3.0.
- [x] Missing `race_config` -> pop skipped, no crash.
- [x] Multi-species planet: each species' happiness computed independently from its own race config + species-config ratio.

**Notes:** 12 tests total (exceeds the 7-checkbox spec). Assertions reference the formula directly via `score_planet_for_race` rather than hardcoding numeric habitability values — keeps the tests stable if PROJ-283 tweaks the `FACTOR_REGISTRY` weights. `test_zero_population_still_gets_fresh_happiness` pins the overwrite-every-turn contract symmetrical to the organics engine's zero-pop test. The clamp test uses `ratio=20` to push past the 3.0 ceiling despite the ~0.94 Earth-like habitability factor.

### Task 3.3: Wire `HappinessEngine` into `TurnEngine` [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_turn_engine.py`

- [x] Inject `HappinessEngine` as a DI-friendly constructor parameter.
- [x] Call `happiness_engine.process_happiness(empires, galaxy)` BETWEEN `OrganicsConsumptionEngine` (Phase 2) and `PopulationEngine.process_population_growth`.
- [x] Final order: `[100-tick loop] -> OrganicsConsumptionEngine -> HappinessEngine -> PopulationEngine -> QualityEngine -> AtmosphereEngine -> WaterEngine`.
- [x] Add `IHappinessEngine` protocol to `game/strategy/interfaces/engines.py`.

**Notes:** 15th field on `TurnEngineConfig` (bumped `test_field_count` 14 → 15). Lazy `@property` on `TurnEngine` builds a default `HappinessEngine()` on first access. `test_turn_engine.py` doesn't exist in the tree — test the wiring via `test_turn_engine_config.py::test_field_count` and the sharded suite.

### Task 3.4: Rework `PopulationEngine` growth formula [Medium]
**File:** `game/strategy/engine/population_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_population_engine.py`

- [x] Replace existing growth logic with:
  ```python
  config = colony.get_species_config(pop.race_id)
  last_food_ratio = config.last_food_ratio
  effective_r = race_config.base_reproduction_rate * last_food_ratio
  habitability = score_planet_for_race(colony, race_config)
  K_eff = max(1.0, max_population * habitability)

  logistic_term = effective_r * pop.count * (1 - pop.count / K_eff) * pop.happiness

  # Starvation decline: separate from logistic; adds on top
  decline_term = 0.0
  if last_food_ratio < 1.0:
      decline_term = -DECLINE_RATE * pop.count * (1 - last_food_ratio)

  growth = logistic_term + decline_term
  pop.count = max(0, pop.count + int(growth))
  ```
- [x] `DECLINE_RATE = 0.02` as a module constant.
- [x] Use `pop.happiness` freshly written by `HappinessEngine` in Phase 3 (no recompute).
- [x] No more `_aptitude_to_growth_rate` (deleted in PROJ-283 Phase 4).

**Notes:** Removed the defensive `min(1.0, pop.happiness)` clamp from the old formula — `HappinessEngine` now produces values up to 3.0, and the population growth formula must honor over-supply boosts. Kept a `max(0.0, ...)` floor so a pathological pre-turn happiness can't flip the logistic sign. `K_eff` floor changed from `int(max(0, hab)) + 1` to `max(1.0, max_pop * hab)` (float) to avoid premature truncation on harsh-but-not-dead planets.

### Task 3.5: Update `PopulationEngine` tests [Medium]
**File:** `tests/unit/strategy/engine/test_population_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_population_engine.py`

- [x] Seed `config.last_food_ratio` AND `pop.happiness` explicitly before running population growth (simulating what the new turn order does).
- [x] Green state (food_ratio=1, habitability=0.9, happiness=0.5, pop=1000, max_pop=2000) -> sensible positive growth.
- [x] Amber state (food_ratio=0.5): effective_r halved; logistic output halved; decline term = `-0.02 * 1000 * 0.5 = -10`.
- [x] Red state (food_ratio=0): effective_r=0 (no logistic growth); decline term = `-0.02 * pop` -> steady population decline.
- [x] Zero-pop: skipped.
- [x] Over-carrying-capacity: `P > K` -> negative logistic growth applies normally.

**Notes:** Added a new `TestFoodRatioAndDecline` class with 6 tests covering the new formula. Left all existing test classes (`TestLogisticGrowthBasic`, `TestHappinessAndHabitability`, `TestPopulationDynamics`, `TestAptitudeEffects`, `TestTurnEngineIntegration`, `TestEdgeCases`) unchanged — they all still pass because `last_food_ratio` defaults to 1.0, which collapses the new formula onto the old one. Extra test: `test_happiness_clamp_above_one_still_honored` pins the "remove defensive happiness clamp" behavior change from Task 3.4.

### Task 3.6: End-to-end demographic loop integration test [Medium]
**File:** `tests/integration/strategy/test_demographics_loop.py` (NEW)
**Tests:** `pytest tests/integration/strategy/test_demographics_loop.py`

- [x] Build a minimal `TurnEngine` with the 3 new-wired engines + stub harvesting.
- [x] Scenario A: fed colony on ideal planet, 5 turns — population grows logistically, happiness stable at `base_happiness * 1.0 * hab ≈ expected`, organics stockpile drains.
- [x] Scenario B: starving colony (no organics stockpile), 5 turns — happiness drops to 0, population declines via decline term.
- [x] Scenario C: colony with food_allocation=2.0 — consumption doubles, happiness elevates, stockpile drains faster.

**Notes:** Scoped to the 3-engine pipeline (`OrganicsConsumptionEngine → HappinessEngine → PopulationEngine`) without booting a full `TurnEngine` — the per-turn post-tick pipeline is what PROJ-284 actually changes, and testing just those three keeps the integration test fast and free of harvesting / production / movement fixtures. Added a bonus `TestPipelineOrdering` class that pins the order-matters property: if happiness ran BEFORE consumption, starvation wouldn't show up until turn 2. Added `test_starvation_ratio_written_every_turn_even_when_zero_last_turn` to exercise a refill → starve → refill cycle.

### Task 3.7: Full suite green [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Full sharded suite green.

**Notes:** 14910 total, 14905 passed, 5 failed — all 5 failures are pre-existing sharded-runner flakes called out in the Phase 2 handoff (`tests/fixtures/test_make_minimal_spec.py` × 4 + `test_quickstart_builder::test_copy_designs_without_themes_preserves_original`). Verified in isolation: the 4 `test_make_minimal_spec.py` tests pass; only the theme_id pollution flake persists, and it ALSO fails in isolation when run alongside the quickstart suite, matching the handoff's "persistently identified across every PROJ-283 phase + PROJ-284 Phase 1" note. Net new Phase 3 tests: 23 (12 happiness + 6 population-new-formula + 5 demographics integration).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
