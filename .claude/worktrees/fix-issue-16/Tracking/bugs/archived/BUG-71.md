# BUG-71: Design Workshop - +/- buttons affect wrong layer for duplicate components

## Description

In the Design Workshop, in the ship structure list when multiple of the same component are in different layers, pressing the + or - buttons to the right do not necessarily add/remove the component from that layer. It may come from or go to another layer that already has one of the same components.

## Priority

**High** - Significant feature broken. Users cannot reliably manage component placement across layers.

## Status (Awaiting Confirmation)

## Work Log

### 2026-02-08 - Fix Applied

**Root Cause:** When +/- buttons were clicked on `LayerComponentItem` or `IndividualComponentItem`, they passed only the `group_key` or `component` object — no layer context. The event handlers in `WorkshopEventRouter` and legacy `BuilderScreen` then searched ALL layers for a match, picking the first one found by iteration order. When the same component type existed in multiple layers (e.g., Armor Plate in CORE and INNER), the wrong layer was targeted.

**Fix:** Threaded `layer_type` through the entire event chain:
1. `structure_list_items.py` — `LayerComponentItem` and `IndividualComponentItem` now store `layer_type` and pass `(payload, layer_type)` tuples for add/remove actions (select/drag unchanged).
2. `layer_panel.py` — passes `layer_type=l_type` when constructing items during `rebuild()`.
3. `workshop_event_router.py` — `_handle_remove_group`, `_handle_remove_individual`, and `_handle_add_component` unpack the tuple and search only the targeted layer. Fixed pre-existing broken tuple check (`not isinstance(data[0], str)` which could never match since group_key IS a string).
4. `main.py` (legacy builder) — same layer-targeted logic for backwards compatibility.

**Files Modified:**
- `game/ui/screens/builder/structure_list_items.py`
- `game/ui/screens/builder/layer_panel.py`
- `game/ui/screens/workshop_event_router.py`
- `game/ui/screens/builder/main.py`
- `tests/unit/builder/test_layer_targeted_actions.py` (new — 8 tests)
