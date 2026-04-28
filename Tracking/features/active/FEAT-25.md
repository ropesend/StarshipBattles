# FEAT-25: Planet Registry — upgrade Effects filter from on/off chips to 3-way tri-state

## Description
Extend the Effects filter section added in FEAT-16 on the Galactic
Planet Registry from binary on/off chips to proper tri-state filters
using the existing
[`FilterState`](../../../game/ui/filters/filter_state.py) primitive
(`YES` / `NO` / `IGNORE`) and the
[`TriStateWidget`](../../../game/ui/components/filters/tri_state_widget.py)
component.

The user explicitly called out **Thermal Damage**, **Shield Modifier**,
and **Thrust Modifier** as the effects that benefit most from tri-state
filtering — these are common planet abilities a player wants to either
avoid (don't colonise) or actively seek out (do colonise).

## Filter semantics
- `IGNORE` (default for every effect): effect is not part of the
  filter; planets pass regardless of whether they have it.
- `YES`: planet must have this effect to pass.
- `NO`: planet must NOT have this effect to pass.
- **Across multiple effects:** AND. Example: `Thermal Damage = NO` and
  `Shield Modifier = YES` shows planets with a shield modifier but no
  thermal damage.

This replaces the FEAT-16 contract of "OR within Effects, AND across
categories, zero-selected = no-op". Under tri-state, the no-op state is
"all effects on IGNORE".

## Required changes
- [game/ui/screens/planet_list_filter_manager.py](../../../game/ui/screens/planet_list_filter_manager.py)
  — change `filter_effects: Dict[str, bool]` to `Dict[str, FilterState]`.
  Migrate `toggle_effect`, `set_all_effects`, `get_filter_state['effects']`.
- [game/ui/screens/planet_list_filters.py](../../../game/ui/screens/planet_list_filters.py)
  — rewrite `effects_predicate(filter_effects)`: skip IGNORE entries,
  require YES matches, exclude NO matches.
- [game/ui/screens/planet_list_sidebar.py](../../../game/ui/screens/planet_list_sidebar.py)
  — replace the chips section with one `TriStateWidget` per effect.
- [game/ui/screens/planet_list_presets.py](../../../game/ui/screens/planet_list_presets.py)
  — preset round-trip uses the FilterState enum.
- Tests under `TestEffectsPredicate` and the relevant filter-manager
  tests updated for the three states.

## Out of scope
- Extending tri-state to the existing Type / Owner / Gravity /
  Temperature / Mass-Density / Water filters. Those have different
  semantics (presence + range filters, not effect-presence filters).
- Adding new planet effect types beyond what FEAT-16 already
  discovers dynamically from the loaded save.
- Multi-select within a single tri-state row.

## Acceptance
- Each effect in the Effects filter renders as a tri-state widget
  with three visible positions.
- Setting an effect to YES filters the planet list to only planets
  that have it.
- Setting an effect to NO filters to only planets that don't have it.
- Setting an effect to IGNORE leaves the filter inactive.
- The "All / None" buttons at the section top set every effect to
  YES / IGNORE respectively (no "set all to NO" affordance unless the
  All/None buttons make it natural; consider out-of-scope otherwise).
- Presets round-trip the tri-state values cleanly across save / load
  and across different galaxies (effect ids not present in the
  current galaxy are silently dropped, matching FEAT-16 behaviour).
- Existing FEAT-16 tests pass after migration; new tri-state tests
  added for the three states and AND-across-effects semantics.

## Priority
Low (UX refinement of an already-working feature)

## Status
Pending

## Related
- FEAT-16 (archived, completed) — added the Effects filter section
  with binary on/off chips.

## Work Log
- 2026-04-28: Created from QA Session 20260428_052952.
