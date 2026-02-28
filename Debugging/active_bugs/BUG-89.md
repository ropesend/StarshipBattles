## Description
The game crashes upon clicking the design button due to an `AttributeError: 'ModifierEditorPanel' object has no attribute 'update'` occurring in `game\ui\screens\workshop_screen.py` at line 471.

## Priority
Critical

## Status
Awaiting Confirmation

## Root Cause
`workshop_screen.py:471` calls `self.modifier_panel.update(dt)` every frame, but `ModifierEditorPanel` in `game/ui/panels/builder_widgets.py` was missing the `update(dt)` method. Both sibling panels (`BuilderLeftPanel`, `LayerPanel`) have this method. The modifier panel has no time-dependent state, so a no-op `update` is correct.

## Fix
Added `update(self, dt)` method to `ModifierEditorPanel` class in `game/ui/panels/builder_widgets.py` (after `set_panel_height`).

### Files Modified
1. `game/ui/panels/builder_widgets.py` — Added `update(dt)` method
2. `tests/unit/ui/panels/test_modifier_editor_panel.py` — New test file (3 tests)

### Tests
- 3 new tests pass: method exists, doesn't raise with normal dt, doesn't raise with zero dt
- Full suite: 12,976 passed (4 pre-existing failures in unrelated colony flag tests)

## Work Log
- 2026-02-28: Bug identified from QA session log and traceback. Tickets created.
- 2026-02-28: Fixed — added missing `update(dt)` method to `ModifierEditorPanel`.
