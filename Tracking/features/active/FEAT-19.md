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
Pending

## Work Log
- 2026-04-27: Created from QA Session 20260427_151244.
