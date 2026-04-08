# BUG-40: Component Modifier Grid should be persistent panel

## Description
In the design workshop the Component Modifier Grid should be a persistent panel, and when there is no component selected, it is fine to say: "no modifier effects to display"

## Priority
Medium

## Status
Awaiting Confirmation

## Work Log
- 2026-01-23: Ticket created
- 2026-01-23: Fixed. Changed `ComponentModifierGridPanel` to be persistent:
  - Removed `self.panel.hide()` on init (line 79-80)
  - Modified `update_component()` to not hide panel when no component selected
  - Modified `draw()` to always draw when panel visible (not just when component exists)
  - The `ModifierImpactGrid` already displays "No modifier effects to display" when empty
  - Files modified: `game/ui/panels/component_modifier_grid_panel.py`
  - Tests pass: `tests/unit/ui/test_modifier_impact_grid.py` (9 passed)
