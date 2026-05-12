# FEAT-16: Planet List — filter and column support for planet effects/abilities

## Description
The Galactic Planet Registry currently filters by Planet Type, Owner, Gravity,
Temperature, Mass Density, and Water, and offers toggleable columns for stats
and resources. There is **no filter** for planet effects/abilities and **no
column** to display them.

Once intrinsic abilities become rare per FEAT-15, the player needs a way to
locate the planets that do carry effects. This feature adds:

1. **Filter section** — "Effects" filter group listing every distinct ability
   present on planets in the current galaxy (ShieldModifier, ThrustModifier,
   EnvironmentalDamage, FuelDrain, StrategicSpeedModifier, etc.). Selecting
   one or more narrows the planet list to planets carrying those effects.
2. **Toggleable columns** — every effect type appears as a column candidate
   (alongside the existing resource columns). Toggling a column on shows the
   effect's magnitude (e.g., "x0.85" or "0.5/turn") for each planet that has
   it; blank for planets that don't.

Reproduced layout in QA Session 20260427_151244 at 15:26–15:27:

[![Galactic Planet Registry — current filters and columns](../../../tools/qa_observer/session_data/20260427_151244/images/bug_capture_152718.png)](../../../tools/qa_observer/session_data/20260427_151244/images/bug_capture_152718.png)

## Required changes
- `game/ui/screens/planet_list_sidebar.py` — add Effects filter group and
  Effects column toggles.
- `game/ui/screens/planet_list_window.py` — table rendering for the new
  columns; filter predicate evaluation.
- Effect list should be **dynamic** — derived from the abilities actually
  present in the loaded save, not a hardcoded enum.

## Acceptance
- Filter by one effect → only planets with that effect appear.
- Filter by multiple effects → AND or OR semantics (decide and document).
- Toggle a column → the column appears with magnitude data.
- Empty galaxy effect → filter group hidden (no effects → no filters).

## Related
- FEAT-15 (Per-planet probability roll for intrinsic abilities) — this
  feature becomes meaningful once planet effects are rare and need to be
  located.

## Priority
Low

## Status
Awaiting Confirmation

## Work Log
- 2026-04-27: Created from QA Session 20260427_151244.
- 2026-04-27: Implementation complete (investigator-feat-16, deep-dive-session).

  **Approach summary**
  - Promoted `_make_group_key` and `_make_display_name` to public
    `make_group_key` / `make_display_name` in
    `game/strategy/services/system_effects_collector.py` (no aliases — Rule 3
    eradication; both internal call sites migrated).
  - Added shared formatter `format_intrinsic_ability_magnitude(ability_name,
    ability_data)` in the same module. Returns `"-0.27 hull/turn"`,
    `"-0.50 fuel/turn"`, `"x0.91"`, etc., or `""` for identity values.
  - `system_tree_panel._format_effect_value` now **delegates** to the shared
    formatter for the rate-style and shared multiplier-style paths
    (ResourceHarvestBooster / BuildRateBooster / QualityImprovement
    aggregate-only renderings stay local — no per-planet equivalent exists).
  - Refactored `filter_planets` to a **predicate-list pipeline** (six builders
    — name/type/owner/grav/temp/mass + new `effects_predicate`). Public
    function signature stays positional-compatible; new filter is appended
    as keyword-only `filter_effects=None`.
  - `compute_planet_effect_keys(all_planets)` discovers group-keys
    dynamically; `effects_predicate(filter_effects)` implements
    OR-within-Effects.
  - `PlanetListFilterManager.filter_effects: Dict[str, bool] = {}` +
    `toggle_effect`, `set_all_effects`, `get_filter_state['effects']`.
  - `build_sidebar(..., effect_keys=None)` conditionally renders the Effects
    section (label, All/None, chips) only when non-empty. Empty galaxy →
    section omitted entirely; `ui_filters['effects']` is `{}`.
  - `PlanetListWindow` populates `_effect_keys`, appends per-effect columns
    via `build_effect_columns`, seeds `filter_effects` all-True (so the
    filter is a no-op until the user unticks something), wires Effects
    All/None buttons + per-chip toggles. Toggle handler reads `_display_label`
    so chips render as "Thermal Damage" not "EnvironmentalDamage:thermal".
  - Preset round-trip: `capture_planet_list_state(filter_effects=...)` and
    `apply_planet_list_state(filter_effects=...)` both new optional kwarg.
    Apply silently drops keys not present in the current galaxy's effect
    set (preset from a different save won't crash).

  **Filter semantics**
  - OR within Effects category, AND across categories.
  - **Special case: zero effects selected = no-op (every planet passes).**
    Different from Type/Owner where zero-selected = "show none". The
    reasoning is documented in `planet_list_filters.py` module docstring
    and the contract is pinned by named tests
    (`TestEffectsPredicate::test_no_selections_is_noop_show_all`,
    `TestEffectsPredicate::test_all_false_selections_is_also_noop_show_all`).

  **Refactor decision**
  - Predicates pattern adopted as recommended by the investigation. No
    sprawl encountered — all six existing categories cleanly mapped to
    builder helpers. No fall-back to the kwarg-only path was needed.

  **Files modified**
  - `game/strategy/services/system_effects_collector.py` — public helpers + formatter
  - `game/ui/panels/system_tree_panel.py` — delegation to shared formatter
  - `game/ui/screens/planet_list_filters.py` — predicate refactor + new helpers
  - `game/ui/screens/planet_list_filter_manager.py` — filter_effects state
  - `game/ui/screens/planet_list_sidebar.py` — Effects section rendering
  - `game/ui/screens/planet_list_window.py` — wiring + build_effect_columns
  - `game/ui/screens/planet_list_presets.py` — round-trip filter_effects

  **Files added — none** (all changes extend existing modules in their
  established style).

  **Test results**
  - 124 / 124 FEAT-16 scope tests pass:
    - `test_planet_list_filters.py` — 14 (8 new)
    - `test_planet_list_filter_manager.py` — 20 (3 new)
    - `test_planet_list_window.py` — 8 (5 new)
    - `test_planet_list_components.py` — 41 (2 new sidebar tests)
    - `test_system_effects_collector.py` — 41 (13 new formatter / public-helper tests)
  - `tests/ -k "system_tree"` (41) — all pass; the system tree's
    `_format_effect_value` delegation is verified end-to-end.
  - Two unrelated pre-existing failures observed in
    `tests/unit/strategy/services/test_planet_economy_projector.py::TestYardDrain` and
    `tests/unit/strategy/production_engine/test_tick_consumption.py` — caused
    by another in-flight teammate's BuildQueue refactor work (touches
    `production_engine.py` / `build_queue_source.py`); zero overlap with
    FEAT-16's surface.

  **Branch:** main (no worktree).
