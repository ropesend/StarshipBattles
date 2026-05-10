# BUG-49: Component Modifier Grid - Hide Irrelevant Columns

## Description
In the Component modifier Grid Panel, columns that don't actually apply to any of the abilities or attributes of the component should be hidden, for example A component that produces no strategic movement should not have strategic movement as a column. This will have to be calculated in a data driven manner, the .json files need to be processed and the actual abilities and attributes that are modified should be shown. It should not be hard coded on a per component basis, it needs to work with new components with novel combinations of abilities. Here is what currently shows for a Bridge component, many of the abilities are not present on the bridge:

**Screenshot:** C:\Developer\StarshipBattles\screenshots\screenshot_20260124_072304_813450_mouse_focus.png

## Priority
Medium

## Status
Awaiting Confirmation

## Work Log
- 2026-01-24: Ticket created
- 2026-01-24: Fixed by implementing data-driven column filtering:
  - Modified `update()` to use `_get_component_consumed_stats()` for filtering columns
  - Added `UNIVERSAL_STATS` constant for stats all components have (mass, hp, cost)
  - `_get_component_consumed_stats()` now returns:
    - Universal stats (always included)
    - Ability-specific stats from `STAT_BINDINGS` on the component's abilities
  - Grid now only shows columns for stats the component actually uses
  - File modified: `game/ui/panels/modifier_impact_grid.py:105-112, 143-175`
