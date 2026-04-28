# FEAT-14: Race Setup Summary tab — show all environmental factors and aptitudes

## Description
The Summary tab on the Species Setup screen currently shows only a partial
slice of the chosen environmental factors (gravity, temperature, water,
radiation, plus a gas atmosphere summary). Other factors defined in
`FACTOR_REGISTRY` (PROJ-283) — pressure, tectonic, magnetic — are not
displayed.

The user wants the Summary tab to show **every factor** that has been set for
the species: every entry in `FACTOR_REGISTRY` plus every aptitude. This makes
the Summary a complete review surface before saving the race. Descriptions
remain in the Descriptions box (too large to inline).

## Required changes
1. **Iterate `FACTOR_REGISTRY`** in
   `game/strategy/data/habitability_factors.py` to drive the environment
   summary. Use the `display_unit` and `display_precision` fields added in
   PROJ-293 so formatting stays data-driven.
2. **Render every factor row** with setpoint ± tolerance, formatted via the
   PROJ-293 display contract.
3. **Show all 7 aptitudes** explicitly: strength, intelligence, constitution,
   dexterity, tolerance_other_species, cooperation, conflict_tolerance.
4. **Stop hardcoding** gravity / temperature / water / radiation as separate
   `summary_labels` entries in `game/ui/panels/race_summary_panel.py` (lines
   262-289) — replace with a registry-driven loop.

## Acceptance
- Adding a new factor to `FACTOR_REGISTRY` makes it appear automatically in
  the Summary tab without code changes (matches PROJ-283/293 contract).
- All 7 aptitudes show with their assigned scores.
- Tab layout stays within the existing column width — long lists scroll if
  they overflow.

## Priority
Medium

## Status
Pending

## Work Log
- 2026-04-27: Created from QA Session 20260427_151244.
