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
Awaiting Confirmation

## Work Log
- 2026-04-27: Created from QA Session 20260427_151244.
- 2026-04-27: Implemented (deep-dive-session/investigator-feat-14).
  - **Approach:** Replaced the static 4-factor / 1-aptitude-summary block in
    `_create_column3_content` with a `UIScrollingContainer`. The container's
    contents are rebuilt on every `refresh()` from `iter_scalar_factors()`
    + filtered `iter_gas_factors()` (setpoint > 0) + the 7 RaceConfig
    aptitudes. Setpoint ± tolerance values are formatted via
    `PreferenceRow.format_value` — the canonical PROJ-293 display contract,
    NOT a re-implementation. Adding a new factor to `FACTOR_REGISTRY`
    surfaces a row automatically (acceptance criterion).
  - **Files modified:**
    - `game/ui/panels/race_summary_panel.py` (+115 / -129 LOC; net −14)
    - `tests/unit/ui/test_race_summary_panel.py` (+213 / -85 LOC; net +128)
  - **Deletions:** Removed 5 per-factor formatters
    (`_format_gravity_summary`, `_format_temperature_summary`,
    `_format_radiation_summary`, `_format_water_summary`,
    `_format_aptitudes_summary`) and the obsolete legacy tests that
    called them.
  - **Discovery:** `_format_atmosphere_summary` was found to be dead code
    (defined but never invoked from `refresh()`) — deleted in this PR.
    The atmosphere "summary line" mentioned in the original ticket
    description has not actually appeared in the rendered UI for some
    time; the new registry-driven loop now renders all gases the race
    has set explicitly.
  - **New aptitude rendering:** all 7 aptitudes now show on one row each
    (Strength / Intelligence / Constitution / Dexterity / Tolerance
    (other species) / Cooperation / Conflict Tolerance) plus the two
    PROJ-283 derived seeds (Base Happiness, Base Reproduction Rate).
    Replaces the legacy compact 3-line "STR:5 INT:5 CON:5 ..." packing.
  - **Tests:** 6 new acceptance tests in
    `TestFeat14RegistryDrivenSummary`:
      1. Every scalar factor's `display_name` rendered.
      2. Every gas factor with setpoint > 0 rendered.
      3. Setpoint values use `PreferenceRow.format_value` ("1.0 g",
         "293 K") — verifies PROJ-293 display contract reuse.
      4. All 7 aptitudes rendered by long name.
      5. `base_happiness` and `base_reproduction_rate` both rendered.
      6. Monkeypatching `iter_scalar_factors` to yield a synthetic
         factor surfaces it in the rendered text — the
         "registry-add-only" acceptance proof.
  - **Test results:** Targeted (`tests/unit/ui/ tests/unit/strategy/`):
    6657/6657 passed. Full sharded suite: **15726/15726 passed**, zero
    regressions.
  - **Branch:** main.
