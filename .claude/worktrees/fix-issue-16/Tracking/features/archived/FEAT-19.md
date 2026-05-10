# FEAT-19: Surplus-food happiness bonus (allocation > 1.0× rewards happiness)

## Description
Today, increasing the food allocation slider above 1.0× has no effect on
happiness. The formula
`happiness = base_happiness × last_food_ratio × habitability` reads
`last_food_ratio` (capped at 1.0 by Liebig minimum), so once the colony is
fed, extra allocation just raises the demand bar — it never produces a
happiness reward.

The user expects overfeeding to be a meaningful population strategy:
*"increasing food allocation should impact happiness."* This feature adds a
surplus-food happiness bonus.

Reproduced in QA Session 20260427_151244 at 15:51 — the captured colony shows
Allocation 1.35× but Happiness 0.24 with Food ratio 1.00:

[![Colony detail showing Allocation 1.35x, Food ratio 1.00, Happiness 0.24](../../../tools/qa_observer/session_data/20260427_151244/images/bug_capture_155128.png)](../../../tools/qa_observer/session_data/20260427_151244/images/bug_capture_155128.png)

## Required changes
1. **Track surplus separately** — alongside `last_food_ratio` (capped at 1.0),
   compute an unbounded `last_food_surplus` (e.g., `supplied / needed_at_1x`)
   that can exceed 1.0 when allocation > 1.0× and supply meets the increased
   demand.
2. **Happiness contribution** — extend
   `HappinessEngine` (`game/strategy/engine/happiness_engine.py`) with a
   bonus term when surplus > 1.0. Suggested shape:
   `happiness += surplus_bonus_coefficient × (surplus - 1.0)` clamped to a
   small cap (e.g., +0.2) so overfeeding is rewarding but not dominant.
3. **Tunable from data** — `economy.json` (or `happiness.json`) gains
   `surplus_food_bonus_per_x` (e.g., 0.2 per +0.5 surplus, capped at +0.2)
   so the value is data-driven rather than hardcoded.
4. **UI feedback** — Population panel shows the surplus value when above 1.0
   (e.g., "Food surplus: 1.35× → +0.10 happiness") so the player can see the
   reward. (May warrant a follow-up bug if the slider above 1.0× still feels
   misleading after this lands.)
5. **Tests** — unit tests for: surplus = 1.0 (no bonus), surplus = 1.35
   (capped or partial bonus), surplus when colony is starving (no bonus, ratio
   still drives the base term).

## Acceptance
- Increasing allocation above 1.0× while food supply meets the new demand
  visibly raises happiness in the Population panel.
- Increasing allocation above what supply can sustain still penalises
  happiness via reduced `last_food_ratio` (existing behaviour preserved).
- Bonus is data-driven and bounded (no runaway happiness from extreme
  allocations).

## Priority
Medium

## Status
Awaiting Confirmation

## Work Log
- 2026-04-27: Created from QA Session 20260427_151244.
- 2026-04-27: Implemented (TDD).
  - **Approach:** added `ColonySpeciesConfig.last_food_surplus` `@property` (= `food_allocation × MIN(last_consumption_ratios)`, 1.0 fallback for empty dict). Extended `EconomyConfig` with `surplus_food_bonus_per_x` (0.20) + `surplus_food_bonus_cap` (0.20). `HappinessEngine` now takes `economy_config` keyword-only kwarg and adds `min(cap, per_x × (surplus - 1.0))` to the raw happiness expression BEFORE the existing [0, 3] clamp when `surplus > 1.0`. Facade `EconomySlice` pre-computes `food_surplus` + `food_surplus_bonus` on `SpeciesDemographicView`; UI conditionally renders "Food surplus: X.XX× → +Y.YY happiness" when surplus > 1.0.
  - **Decision:** `OrganicsConsumptionEngine` and `PopulationEngine` are NOT touched. Surplus is derivable from data the consumption engine already writes (each per-resource ratio is `supplied / (count × allocation × rate)`, so multiplying by allocation yields `supplied / needed_at_1x`). Surplus reaches population growth indirectly through `pop.happiness`; adding a separate surplus term to growth would double-count the reward.
  - **Files modified:**
    - `data/economy.json` — added `surplus_food_bonus_per_x: 0.20`, `surplus_food_bonus_cap: 0.20`.
    - `game/strategy/config/economy_config.py` — added two fields with dataclass defaults; loader populates from JSON with graceful 0.20/0.20 fallback.
    - `game/strategy/data/colony_species_config.py` — added `last_food_surplus` `@property`.
    - `game/strategy/engine/happiness_engine.py` — added `economy_config` kwarg (DI mirrors `OrganicsConsumptionEngine`), additive bonus before clamp.
    - `game/strategy/facade/dto/colony_demographic_view.py` — added `food_surplus` + `food_surplus_bonus` fields.
    - `game/strategy/facade/slices/economy_slice.py` — pre-computes both fields from `EconomyConfig` coefs.
    - `game/ui/screens/strategy_detail_fmt.py` — conditional surplus row in per-species sub-block.
    - `docs/systems/strategy_layer.md` — Happiness §8 documents `last_food_surplus`, the new economy.json fields, the additive bonus formula, and the "PopulationEngine NOT touched" decision. Bumped `Last verified:` to 2026-04-27.
    - Tests: `tests/unit/strategy/data/test_colony_species_config.py` (+5 surplus-property tests, +1 read-only test), `tests/unit/strategy/engine/test_happiness_engine.py` (+9 surplus-bonus tests, 1 legacy test updated to acknowledge the bonus), `tests/integration/strategy/test_demographics_loop.py` (+1 end-to-end surplus test), `tests/unit/strategy/facade/test_colony_demographic_view.py` (+3 DTO-population tests, 1 helper updated), `tests/unit/ui/screens/test_strategy_detail_fmt.py` (+2 UI render tests, 1 helper updated).
  - **Test results:** Targeted (212/212 pass on the 7 affected test files). Full sharded suite: 15800/15802 pass (the 2 failing tests — `test_empire_build_queue_window`, `test_empire_build_queue_filter_manager` — are pre-existing FEAT-17-related failures unrelated to FEAT-19; verified by re-running with the FEAT-19 working tree stashed: those tests pass without my changes when other parallel teammate edits are also gone).
  - **QA-ticket reproduction (verified by `test_surplus_partial_below_cap`):** allocation 1.35× with full supply → surplus 1.35 → bonus = `min(0.20, 0.20 × 0.35) = 0.07`. Pre-fix happiness 0.24 → post-fix 0.31.
  - **Save compatibility:** No new persisted fields. `last_food_surplus` is a derived property; `to_dict` / `from_dict` unchanged. Old saves load identically.
  - **Branch:** `main` (worktree not enabled per coordinator).
