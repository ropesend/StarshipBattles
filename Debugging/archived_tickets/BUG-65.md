# BUG-65: Design Workshop - Component Modifiers Should Auto-Select Applicable Modifiers

## Description

In the Design Workshop, in the Component modifiers Panel, all applicable modifiers should always be selected, and shown, all non applicable modifiers should not be shown. Here is a visual of the panel when a Life Support module is selected, the Hardened component should be selected, but just default to 1.00 it should not be possible to unselect it, and Currently it does not start out selected like it should be. Please look into all modifiers, as there are a few that seem to do this: C:\Dev\Starship Battles\output\screenshots\screenshot_20260207_150924_614024_mouse_focus.png

![Screenshot](C:\Dev\Starship Battles\output\screenshots\screenshot_20260207_150924_614024_mouse_focus.png)

## Priority
High

## Status
Awaiting Confirmation

## Work Log

### Root Cause
Two separate `get_mandatory_modifiers()` methods existed - one in `ModifierLogic` (UI layer) and one in `ModifierService` (simulation layer). Both used hardcoded lists of specific modifier IDs that were incomplete. The UI version was missing `hardened_mount` and `efficiency_mount` entirely, so they showed as optional toggles rather than auto-selected.

### Fix
Changed both `get_mandatory_modifiers()` implementations to dynamically return ALL allowed modifiers for a component:
- Any modifier where `is_modifier_allowed(mod_id, component)` returns True is now mandatory
- Modifiers are auto-applied at their default value when a component is added to the ship
- Toggle buttons are disabled (cannot be unchecked) - users adjust values only
- Non-applicable modifiers are hidden (already worked correctly via `is_modifier_allowed` filter in layout)

### Files Modified
- `game/ui/screens/builder/modifier_logic.py` - Simplified `get_mandatory_modifiers()` to return all allowed modifiers
- `game/simulation/services/modifier_service.py` - Same change for the simulation layer counterpart

### Test
All 6519 tests pass (360 modifier-specific tests included). No regressions.
