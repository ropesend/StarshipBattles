# BUG-64: Design Workshop - Component Disappears When Placed in Multiple Layers

## Description

In the Design Workshop placing a component in multiple layers causes problems, I had a Life Support component in the Inner layer, then added one to the outer layer, and then it looks like this: C:\Dev\Starship Battles\output\screenshots\screenshot_20260207_150507_593326_mouse_focus.png  The component in the outer layer shows, but the inner layer component disappears, and there is a blank space.

![Screenshot](C:\Dev\Starship Battles\output\screenshots\screenshot_20260207_150507_593326_mouse_focus.png)

## Priority
High

## Status
Awaiting Confirmation

## Work Log

### Root Cause
The `LayerPanel.rebuild()` method used `("group", group_key)` as the UI cache key for component groups. The `group_key` is `(component_id, modifiers_tuple)`, which is identical for the same component type regardless of which layer it's in. When processing INNER then OUTER, the OUTER layer's group reused the cached INNER UI element, repositioning it to the OUTER position and leaving a blank space where the INNER entry was.

### Fix
Changed the cache key from `("group", group_key)` to `("group", l_type, group_key)` in `layer_panel.py:192`, including the layer type to ensure each layer gets its own unique UI entry.

### Files Modified
- `game/ui/screens/builder/layer_panel.py` - Fixed group item cache key to include layer type
- `tests/unit/ui/test_structure_visibility.py` - Added `test_same_component_in_multiple_layers_shows_in_both`

### Test
Added test that places `life_support` in both INNER and OUTER layers of a Cruiser, then verifies 2 separate `LayerComponentItem` groups exist. All 5 structure visibility tests pass.
