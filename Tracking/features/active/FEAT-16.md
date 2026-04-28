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
Pending

## Work Log
- 2026-04-27: Created from QA Session 20260427_151244.
